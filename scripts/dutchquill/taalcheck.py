#!/usr/bin/env python3
"""
tools/grammar_check.py — DutchQuill AI

Controleert Nederlandse tekst op grammatica- en stijlfouten via de LanguageTool API.
Gebruikt de gratis publieke API — geen API-sleutel vereist.

Limieten publieke API:
  - 20 requests per minuut
  - Max 75 KB per request
  Grote teksten worden automatisch opgesplitst in stukken van max 5.000 tekens.

Gebruik:
    python3 tools/grammar_check.py --input rapport.txt
    cat rapport.txt | python3 tools/grammar_check.py
    python3 tools/grammar_check.py --input rapport.txt --json
    python3 tools/grammar_check.py --input rapport.txt --categorie grammatica

Dependencies:
    pip install requests   (of: pip install -r requirements.txt)
"""

import sys
import re
import json
import time
import hashlib
import warnings
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

# Onderdruk urllib3 SSL-waarschuwing op macOS (LibreSSL vs OpenSSL) vóór import
warnings.filterwarnings("ignore")

try:
    import requests
    warnings.resetwarnings()  # Herstel daarna zodat andere warnings wel zichtbaar zijn
except ImportError:
    print(
        "Fout: 'requests' is niet geïnstalleerd.\n"
        "Voer uit: pip install requests\n"
        "Of: pip install -r requirements.txt",
        file=sys.stderr
    )
    sys.exit(1)

API_URL = "https://api.languagetool.org/v2/check"
MAX_CHARS = 5000        # Veilige grens per request
REQUEST_DELAY = 3.5     # Seconden tussen requests (publieke limiet: 20/min)
CACHE_FILE = Path(".tmp/grammar_cache.json")
CACHE_TTL_HOURS = 24

# LanguageTool-categoriecodes → Nederlandse labels
CATEGORY_LABELS = {
    "GRAMMAR": "Grammatica",
    "TYPOS": "Spelling",
    "PUNCTUATION": "Interpunctie",
    "STYLE": "Stijl",
    "CASING": "Hoofdletters",
    "CONFUSED_WORDS": "Verwisselbare woorden",
    "REDUNDANCY": "Overbodig taalgebruik",
    "MISC": "Overig",
}

# Regels met te veel false positives voor academische tekst — uitsluiten
EXCLUDED_RULES = {
    "WHITESPACE_RULE",
    "SENTENCE_WHITESPACE",
    "DOUBLE_PUNCTUATION",
    "EN_QUOTES",
    "ARROWS",
    "COMMA_PARENTHESIS_WHITESPACE",
    "WORD_CONTAINS_UNDERSCORE",
}


# ─────────────────────────────────────────────
# CACHE HELPERS
# ─────────────────────────────────────────────

def _cache_key(text: str, lang: str, categorie_filter: Optional[str]) -> str:
    """SHA256-hash van text + taalcode + filter als cache-sleutel."""
    payload = f"{lang}|{categorie_filter or ''}|{text}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_cache() -> Dict:
    """Laad het cachebestand. Retourneert lege dict bij ontbrekend of corrupt bestand."""
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: Dict) -> None:
    """Schrijf de cache naar schijf. Maakt .tmp/ aan indien nodig."""
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_cached(key: str) -> Optional[List[Dict]]:
    """Retourneer gecachede bevindingen als ze binnen de TTL vallen, anders None."""
    cache = _load_cache()
    entry = cache.get(key)
    if not entry:
        return None
    try:
        ts = datetime.fromisoformat(entry["timestamp"])
        age_hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        if age_hours <= CACHE_TTL_HOURS:
            return entry["findings"]
    except (KeyError, ValueError):
        pass
    return None


def _store_cache(key: str, findings: List[Dict]) -> None:
    """Sla bevindingen op in de cache met de huidige timestamp."""
    cache = _load_cache()
    cache[key] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "findings": findings,
    }
    # Beperk cachegrootte: max 50 entries (oudste verwijderen)
    if len(cache) > 50:
        oldest = sorted(cache.items(), key=lambda x: x[1].get("timestamp", ""))
        for old_key, _ in oldest[:len(cache) - 50]:
            del cache[old_key]
    _save_cache(cache)


def chunk_text(text: str, max_chars: int = MAX_CHARS) -> List[str]:
    """
    Splits tekst in stukken van max max_chars tekens.
    Splitst bij voorkeur op alinea- of zinsgrenzen.
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    paragraphs = re.split(r'\n\s*\n', text)
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current += ("\n\n" if current else "") + para
        else:
            if current:
                chunks.append(current)

            if len(para) > max_chars:
                # Lange alinea opsplitsen op zinsgrenzen
                sentences = re.split(r'(?<=[.!?])\s+', para)
                current = ""
                for sent in sentences:
                    if len(current) + len(sent) + 1 <= max_chars:
                        current += (" " if current else "") + sent
                    else:
                        if current:
                            chunks.append(current)
                        current = sent
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def check_chunk(text: str, lang: str = "nl") -> Optional[List[Dict]]:
    """Stuur één tekstchunk naar de LanguageTool API. Retourneert matches of None bij fout."""
    try:
        response = requests.post(
            API_URL,
            data={"text": text, "language": lang},
            timeout=20,
        )
        response.raise_for_status()
        return response.json().get("matches", [])

    except requests.exceptions.ConnectionError:
        print(
            "\nFOUT: Geen verbinding met de LanguageTool API.\n"
            "  Mogelijke oorzaken:\n"
            "    • Geen internetverbinding\n"
            "    • api.languagetool.org tijdelijk niet bereikbaar\n"
            "  Wat te doen:\n"
            "    • Controleer je internetverbinding en probeer opnieuw\n"
            "    • Of sla grammar_check.py over en voer de taalcheck handmatig uit\n",
            file=sys.stderr
        )
        return None

    except requests.exceptions.Timeout:
        print(
            "\nFOUT: LanguageTool API reageert niet binnen 20 seconden.\n"
            "  Wat te doen:\n"
            "    • Probeer het opnieuw (API kan tijdelijk overbelast zijn)\n"
            "    • Of sla grammar_check.py over en voer de taalcheck handmatig uit\n",
            file=sys.stderr
        )
        return None

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "?"
        if status == 429:
            print(
                "\nFOUT: Ratelimiet bereikt (HTTP 429).\n"
                "  De gratis LanguageTool API staat maximaal 20 verzoeken per minuut toe.\n"
                "  Wat te doen:\n"
                "    • Wacht 60 seconden en probeer opnieuw\n"
                "    • Of splits de tekst in kleinere stukken\n",
                file=sys.stderr
            )
        else:
            print(
                f"\nFOUT: LanguageTool API gaf foutcode {status}.\n"
                f"  Details: {e}\n"
                "  Wat te doen: probeer opnieuw of controleer api.languagetool.org/status\n",
                file=sys.stderr
            )
        return None


def map_category(match: Dict) -> str:
    """Vertaal LanguageTool-categorie naar Nederlandse label."""
    cat_id = match.get("rule", {}).get("category", {}).get("id", "MISC")
    return CATEGORY_LABELS.get(cat_id, "Overig")


def run_grammar_check(
    text: str,
    lang: str = "nl",
    categorie_filter: Optional[str] = None,
    use_cache: bool = True,
) -> List[Dict]:
    """
    Voer grammar check uit op de volledige tekst.
    Splits automatisch bij lange teksten.
    Retourneert genormaliseerde bevindingen.

    Bij use_cache=True: retourneert gecachede resultaten als die binnen 24u vallen.
    Gebruik --no-cache om de cache te omzeilen en de API opnieuw aan te roepen.
    """
    if use_cache:
        key = _cache_key(text, lang, categorie_filter)
        cached = _get_cached(key)
        if cached is not None:
            print("Cache hit — grammar check overgeslagen (resultaat < 24u oud).", file=sys.stderr)
            return cached

    chunks = chunk_text(text)
    all_findings = []
    char_offset = 0

    for idx, chunk in enumerate(chunks):
        if idx > 0:
            time.sleep(REQUEST_DELAY)

        if len(chunks) > 1:
            print(
                f"Chunk {idx + 1}/{len(chunks)} analyseren "
                f"({len(chunk)} tekens)...",
                file=sys.stderr
            )

        matches = check_chunk(chunk, lang)
        if matches is None:
            print("Analyse gestopt na API-fout.", file=sys.stderr)
            all_findings.append({
                "regel": 0,
                "categorie": "API-FOUT",
                "bericht": "Analyse kon niet worden voltooid — API niet bereikbaar. Zie foutmelding hierboven.",
                "context": "",
                "suggesties": [],
                "rule_id": "API_ERROR",
            })
            break

        for m in matches:
            rule_id = m.get("rule", {}).get("id", "")
            if rule_id in EXCLUDED_RULES:
                continue

            abs_offset = char_offset + m.get("offset", 0)
            line_num = text[:abs_offset].count('\n') + 1
            context_obj = m.get("context", {})
            context_text = context_obj.get("text", "")
            ctx_offset = context_obj.get("offset", 0)
            ctx_length = context_obj.get("length", 0)

            # Markeer de fout in de contextstring
            marked_context = (
                context_text[:ctx_offset]
                + f"[{context_text[ctx_offset:ctx_offset + ctx_length]}]"
                + context_text[ctx_offset + ctx_length:]
            )

            categorie = map_category(m)
            if categorie_filter and categorie.lower() != categorie_filter.lower():
                continue

            replacements = [r["value"] for r in m.get("replacements", [])[:3]]

            all_findings.append({
                "regel": line_num,
                "categorie": categorie,
                "bericht": m.get("message", ""),
                "context": marked_context.strip(),
                "suggesties": replacements,
                "rule_id": rule_id,
            })

        char_offset += len(chunk) + 2  # +2 voor de \n\n

    if use_cache:
        _store_cache(key, all_findings)

    return all_findings


def print_report(findings: List[Dict]) -> None:
    total = len(findings)
    lijn = "═" * 60
    lijn2 = "─" * 60

    print(f"\n{lijn}")
    print("  GRAMMAR CHECK RAPPORT — DutchQuill AI")
    print("  Bron: LanguageTool (api.languagetool.org)")
    print(lijn)
    print(f"  Gevonden: {total} mogelijke fout/stijlkwestie(s)")
    print(lijn2)

    if not findings:
        print("\n  ✓ Geen fouten gevonden.\n")
    else:
        categories: Dict[str, List] = {}
        for f in findings:
            categories.setdefault(f["categorie"], []).append(f)

        for cat, items in categories.items():
            print(f"\n  [{cat}] — {len(items)} bevinding(en)")
            for item in items:
                print(f"\n  ✗ Regel {item['regel']}: {item['bericht']}")
                if item["context"]:
                    print(f"    Context:   \"{item['context'][:100]}\"")
                if item["suggesties"]:
                    print(f"    Suggestie: {' / '.join(item['suggesties'])}")

    print(f"\n{lijn}")
    print("  Automatische check — controleer bevindingen zelf.")
    print("  Niet alle meldingen zijn fouten in academische tekst.")
    print(f"{lijn}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Grammar check via LanguageTool API (DutchQuill AI)"
    )
    parser.add_argument("--input", "-i", help="Invoerbestand. Standaard: stdin.")
    parser.add_argument("--lang", default="nl",
                        help="Taalcode (standaard: nl). Gebruik nl-NL voor striktere check.")
    parser.add_argument("--categorie",
                        help="Filter op categorie (bijv. grammatica, spelling, stijl)")
    parser.add_argument("--json", action="store_true", help="Uitvoer als JSON")
    parser.add_argument("--no-cache", action="store_true",
                        help="Cache omzeilen en API opnieuw aanroepen")
    args = parser.parse_args()

    if args.input:
        try:
            with open(args.input, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Fout: Bestand niet gevonden — {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("Fout: Lege invoer.", file=sys.stderr)
        sys.exit(1)

    use_cache = not args.no_cache
    if not use_cache:
        print("Cache uitgeschakeld — API wordt rechtstreeks aangesproken.", file=sys.stderr)
    print(f"Analyseren ({len(text)} tekens)...", file=sys.stderr)
    findings = run_grammar_check(
        text, lang=args.lang, categorie_filter=args.categorie, use_cache=use_cache
    )

    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        print_report(findings)


if __name__ == "__main__":
    main()
