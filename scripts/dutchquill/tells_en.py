"""
style_check_en.py — Check English client text for AI writing patterns.

English counterpart of humanizer_nl.py (which only understands Dutch). Rules mirror
`.claude/rules/schrijfstijl_en.md`; keep both lists in sync.

Usage:
    python3 tools/style_check_en.py --input text.txt
    python3 tools/style_check_en.py --content content.json        # checks summary + recommendations
    python3 tools/style_check_en.py --input text.txt --json

Risk score (same thresholds as humanizer_nl.py):
    Laag      (0–2 points)
    Gemiddeld (3–6 points)
    Hoog      (7+ points)

Categories:
    1. Banned words/phrases            (1 point per hit)
    2. Banned sentence openers         (1 point per hit)
    3. Dashes in running text          (1 point per hit; rule names "Title Case - Title Case" exempt)
    4. Filler / chatbot phrases        (1 point per hit)
    5. Vague quantifiers               (1 point when > 2)
    6. Uniform sentence rhythm         (1 point when stdev < 4 words with >= 6 sentences)
    7. Repeated paragraph starters     (1 point per first word used in >= 3 paragraphs)
    8. Backticks / Markdown residue    (1 point per paragraph)
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

BANNED = [
    "crucial", "pivotal", "vital", "essential", "robust", "seamless", "seamlessly", "cutting-edge",
    "groundbreaking", "transformative", "holistic", "comprehensive", "meticulous", "meticulously",
    "leverage", "leverages", "leveraging", "harness", "delve", "delves", "foster", "fosters",
    "bolster", "underscore", "underscores", "showcase", "showcases", "streamline", "streamlines",
    "navigate the", "landscape", "realm", "tapestry", "testament to", "a myriad of", "plethora",
    "paramount", "ever-evolving", "game-changer", "synergy", "empower", "empowers", "unlock",
    "elevate", "embark", "endeavour", "endeavor", "noteworthy", "furthermore", "moreover",
    "additionally", "serves as", "stands as",
]

OPENERS = [
    r"in today'?s\b", r"in an era\b", r"it is important to note", r"it is worth noting",
    r"it's worth noting", r"in conclusion\b", r"overall,", r"in the ever-evolving",
    r"in summary,", r"notably,",
]

FILLER = [
    "i hope this helps", "feel free to", "let me know", "great question", "certainly!",
    "remains committed", "the future looks", "plays a key role",
    "plays a crucial role", "it should be noted", "needless to say", "at the end of the day",
    "a wide range of", "in order to",
]

VAGUE = ["several", "various", "numerous", "a number of", "many", "some of the", "a lot of"]

RULE_DASH = re.compile(r"\b[A-Z][\w()./]*(?:\s+[A-Z(][\w()./]*)*\s-\s[A-Z][\w()./]*")


def paragraphs_from_content(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    paras: list[str] = []
    for key in ("intro_investigations", "intro_aanbevelingen"):
        if data.get(key):
            paras.append(data[key])
    for a in data.get("samenvatting", []):
        if isinstance(a, str):
            paras.append(a)
        else:
            paras.append(" ".join(x for x in (a.get("lead"), a.get("tekst")) if x))
    for a in data.get("aanbevelingen", []):
        paras.append(a.get("actie", ""))
        paras.append(a.get("toelichting", ""))
    return [p for p in paras if p and p.strip()]


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", text.strip())
    return [p for p in parts if len(p.split()) >= 2]


def word_hits(text: str, terms: list[str]) -> list[str]:
    low = text.lower()
    hits = []
    for t in terms:
        for _ in re.finditer(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])", low):
            hits.append(t)
    return hits


def check(paras: list[str]) -> dict:
    findings: list[dict] = []
    full = "\n".join(paras)

    for t in word_hits(full, BANNED):
        findings.append({"categorie": "banned_word", "match": t, "punten": 1})

    for p in paras:
        for s in split_sentences(p):
            for rx in OPENERS:
                if re.match(rx, s.strip().lower()):
                    findings.append({"categorie": "opener", "match": s[:60], "punten": 1})

    for p in paras:
        stripped = RULE_DASH.sub("RULE", p)
        for m in re.finditer(r"—|–|\s-\s", stripped):
            ctx = stripped[max(0, m.start() - 25): m.end() + 25].replace("\n", " ")
            findings.append({"categorie": "dash", "match": ctx, "punten": 1})

    for t in word_hits(full, FILLER):
        findings.append({"categorie": "filler", "match": t, "punten": 1})

    vague = word_hits(full, VAGUE)
    if len(vague) > 2:
        findings.append({"categorie": "vague", "match": ", ".join(sorted(set(vague))),
                         "aantal": len(vague), "punten": 1})

    sentences = [s for p in paras for s in split_sentences(p)]
    lengths = [len(s.split()) for s in sentences]
    stdev = statistics.pstdev(lengths) if len(lengths) >= 2 else None
    if len(lengths) >= 6 and stdev is not None and stdev < 4:
        findings.append({"categorie": "rhythm", "match": f"stdev {stdev:.1f} words", "punten": 1})

    starters = Counter(p.split()[0].lower().strip(",.:") for p in paras if len(p.split()) > 8)
    for word, n in starters.items():
        if n >= 3:
            findings.append({"categorie": "repeated_starter", "match": f"'{word}' x{n}", "punten": 1})

    for p in paras:
        if "`" in p or "**" in p:
            findings.append({"categorie": "markdown", "match": p[:50], "punten": 1})

    score = sum(f["punten"] for f in findings)
    risico = "Laag" if score <= 2 else "Gemiddeld" if score <= 6 else "Hoog"
    return {
        "score": score,
        "risico": risico,
        "zinnen": len(sentences),
        "gem_zinslengte": round(statistics.mean(lengths), 1) if lengths else 0,
        "stdev_zinslengte": round(stdev, 1) if stdev is not None else None,
        "korte_zinnen_pct": round(100 * sum(1 for x in lengths if x < 10) / len(lengths)) if lengths else 0,
        "bevindingen": findings,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="English AI-pattern style check")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="Plain text / markdown file")
    src.add_argument("--content", help="JSON file with 'summary' and 'recommendations' text fields")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    else:
        paras = paragraphs_from_content(Path(args.content))

    r = check(paras)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    print(f"Risico: {r['risico']} (score {r['score']})")
    print(f"Zinnen: {r['zinnen']}, gem. lengte {r['gem_zinslengte']}, stdev {r['stdev_zinslengte']}, "
          f"kort (<10 woorden): {r['korte_zinnen_pct']}%")
    for f in r["bevindingen"]:
        print(f"- [{f['categorie']}] {f['match']}")


if __name__ == "__main__":
    main()
