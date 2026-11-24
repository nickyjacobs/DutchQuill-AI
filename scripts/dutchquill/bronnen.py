"""Controleer of de bronnen van de gidsen veranderd zijn sinds de laatste controle.

  dq bronnen check        # vergelijkt; schrijft het resultaat ook naar <data>/bronnen-laatste-check.json
  dq bronnen markeer      # na de review: de huidige stand van alle bronnen geldt als gezien; herinnering op nul

Scribbr: lastmod uit de sitemap. Wikipedia: revisie via de API. GitHub: laatste release.
Overige URL's: een hash van de pagina (de eerste meting is de basis).
Beleefd: een generieke user-agent, drie seconden tussen verzoeken naar dezelfde site, alleen sitemaps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from dutchquill import paden

UA = "DutchQuill-bronnencheck/2.0 (+https://github.com/nickyjacobs/DutchQuill-AI)"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
_laatste: dict[str, float] = {}


def _get(url: str, timeout: int = 20):
    import requests
    host = urlparse(url).netloc
    wacht = 3 - (time.time() - _laatste.get(host, 0))
    if wacht > 0:
        time.sleep(wacht)
    _laatste[host] = time.time()
    return requests.get(url, headers={"User-Agent": UA}, timeout=timeout)


def _frontmatter(pad: Path) -> dict:
    from ruamel.yaml import YAML
    tekst = pad.read_text(encoding="utf-8")
    if pad.suffix in (".yaml", ".yml"):
        d = YAML(typ="safe").load(tekst) or {}
        return {"gecontroleerd": str(d.get("bijgewerkt", "")), "bronnen": d.get("bronnen", [])}
    if not tekst.startswith("---"):
        return {}
    eind = tekst.find("\n---", 3)
    d = YAML(typ="safe").load(tekst[3:eind]) or {}
    return {"gecontroleerd": str(d.get("gecontroleerd", "")), "bronnen": d.get("bronnen", []) or []}


def gidsen_en_urls() -> dict[str, dict]:
    """Alle gidsen (en de tells-data) met hun controledatum en bron-URL's, in de versie die nu geldt."""
    from dutchquill.gidsen import pad as gids_pad
    uit = {}
    basis = paden.root() / "gidsen"
    for p in sorted(basis.rglob("*")):
        if p.suffix not in (".md", ".yaml") or p.name == "bronnen.yaml" or "werkwijze" in p.parts:
            continue
        naam = p.relative_to(basis).with_suffix("").as_posix()
        if p.suffix == ".md":
            p = gids_pad(naam)
        else:
            eigen = paden.data() / "gidsen" / p.relative_to(basis)
            p = eigen if eigen.is_file() else p
        fm = _frontmatter(p)
        uit[naam] = {"pad": str(p), "gecontroleerd": fm.get("gecontroleerd", ""), "bronnen": fm.get("bronnen", [])}
    return uit


def _stand_pad() -> Path:
    return paden.data() / "bronnen-stand.json"


def _lees(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _sitemap_lastmods(index: str, fouten: list) -> dict[str, str]:
    uit: dict[str, str] = {}
    try:
        r = _get(index)
        r.raise_for_status()
        kinderen = [e.findtext("s:loc", namespaces=NS) for e in ET.fromstring(r.content).findall("s:sitemap", NS)]
    except Exception as e:
        fouten.append(f"Sitemap {index}: {e}")
        return uit
    for kind in kinderen:
        if not kind or any(x in kind for x in ("author", "category")):
            continue
        try:
            r = _get(kind)
            r.raise_for_status()
            for u in ET.fromstring(r.content).findall("s:url", NS):
                loc, mod = u.findtext("s:loc", namespaces=NS), u.findtext("s:lastmod", namespaces=NS)
                if loc:
                    uit[loc.rstrip("/") + "/"] = (mod or "")[:10]
        except Exception as e:
            fouten.append(f"Sitemap {kind}: {e}")
    return uit


def check() -> dict:
    from ruamel.yaml import YAML
    cfg = YAML(typ="safe").load((paden.root() / "gidsen" / "bronnen.yaml").read_text(encoding="utf-8"))
    stand = _lees(_stand_pad())
    gidsen = gidsen_en_urls()
    fouten: list[str] = []
    gewijzigd, ongewijzigd, nieuw_gemeten, niet_gevonden = [], 0, [], []
    meting: dict = {"urls": {}, "wikipedia": {}, "github": {}}

    per_url: dict[str, list[str]] = {}
    for naam, g in gidsen.items():
        for u in g["bronnen"]:
            per_url.setdefault(u, []).append(naam)

    sitemap: dict[str, str] = {}
    for index in cfg.get("sitemaps", []):
        sitemap.update(_sitemap_lastmods(index, fouten))
    sitemap_hosts = {urlparse(i).netloc for i in cfg.get("sitemaps", [])}

    for url, namen in sorted(per_url.items()):
        host = urlparse(url).netloc
        oud = stand.get("urls", {}).get(url, {})
        ref = oud.get("lastmod") or min((gidsen[n]["gecontroleerd"] for n in namen if gidsen[n]["gecontroleerd"]),
                                        default="")
        if host in sitemap_hosts and "/category/" not in url:
            mod = sitemap.get(url.rstrip("/") + "/")
            if mod is None:
                if sitemap:
                    niet_gevonden.append({"url": url, "gidsen": namen})
                continue
            meting["urls"][url] = {"lastmod": mod}
            if ref and mod > ref:
                gewijzigd.append({"url": url, "gidsen": namen, "soort": "scribbr", "wanneer": mod,
                                  "reden": f"lastmod {mod} is na {ref}"})
            else:
                ongewijzigd += 1
            continue
        if host in sitemap_hosts or "apastyle.apa.org" in host:
            continue  # categoriepagina's en sites die automatische verzoeken weigeren
        try:
            r = _get(url, timeout=15)
            r.raise_for_status()
            tekst = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>|\s+", " ", r.text, flags=re.S)
            h = hashlib.sha256(tekst.encode()).hexdigest()[:16]
            meting["urls"][url] = {"hash": h}
            if not oud.get("hash"):
                nieuw_gemeten.append(url)
            elif oud["hash"] != h:
                gewijzigd.append({"url": url, "gidsen": namen, "soort": "pagina", "wanneer": date.today().isoformat(),
                                  "reden": "inhoud van de pagina is veranderd"})
            else:
                ongewijzigd += 1
        except Exception as e:
            fouten.append(f"{url}: {type(e).__name__}")

    for w in cfg.get("wikipedia", []):
        try:
            r = _get("https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=ids|timestamp"
                     f"&format=json&titles={w['pagina']}")
            rev = next(iter(r.json()["query"]["pages"].values()))["revisions"][0]
            meting["wikipedia"][w["pagina"]] = rev["revid"]
            oud = stand.get("wikipedia", {}).get(w["pagina"])
            ref = min((gidsen[g]["gecontroleerd"] for g in w["gidsen"] if g in gidsen), default="")
            if (oud and rev["revid"] != oud) or (not oud and rev["timestamp"][:10] > ref):
                gewijzigd.append({"url": f"https://en.wikipedia.org/wiki/{w['pagina']}", "gidsen": w["gidsen"],
                                  "soort": "wikipedia", "wanneer": rev["timestamp"][:10],
                                  "reden": f"nieuwe revisie {rev['revid']}"})
            else:
                ongewijzigd += 1
        except Exception as e:
            fouten.append(f"Wikipedia {w['pagina']}: {type(e).__name__}")

    for g in cfg.get("github", []):
        try:
            r = _get(f"https://api.github.com/repos/{g['repo']}/releases/latest")
            tag = r.json().get("tag_name")
            meting["github"][g["repo"]] = tag
            bekend = stand.get("github", {}).get(g["repo"]) or g.get("bekend")
            if tag and tag != bekend:
                gewijzigd.append({"url": f"https://github.com/{g['repo']}/releases/tag/{tag}", "gidsen": g["gidsen"],
                                  "soort": "github", "wanneer": tag, "reden": f"nieuwe release {tag} (was {bekend})"})
            else:
                ongewijzigd += 1
        except Exception as e:
            fouten.append(f"GitHub {g['repo']}: {type(e).__name__}")

    uit = {
        "gecontroleerd_op": date.today().isoformat(),
        "gewijzigd": gewijzigd,
        "ongewijzigd": ongewijzigd,
        "eerste_meting": nieuw_gemeten,
        "niet_in_sitemap": niet_gevonden,
        "handmatig": cfg.get("handmatig", []),
        "fouten": fouten,
        "gidsen": {n: {"pad": g["pad"], "gecontroleerd": g["gecontroleerd"]} for n, g in gidsen.items()},
    }
    (paden.data() / "bronnen-laatste-check.json").write_text(
        json.dumps({**uit, "_meting": meting}, ensure_ascii=False, indent=2), encoding="utf-8")
    return uit


def markeer() -> dict:
    laatste = _lees(paden.data() / "bronnen-laatste-check.json")
    if not laatste:
        raise SystemExit("Eerst dq bronnen check draaien.")
    stand = _lees(_stand_pad())
    meting = laatste.get("_meting", {})
    for soort in ("urls", "wikipedia", "github"):
        stand.setdefault(soort, {}).update(meting.get(soort, {}))
    stand["gemarkeerd"] = date.today().isoformat()
    _stand_pad().write_text(json.dumps(stand, ensure_ascii=False, indent=2), encoding="utf-8")
    bw = paden.data() / "bijwerken.json"
    status = _lees(bw)
    status["laatst_gecontroleerd"] = date.today().isoformat()
    bw.write_text(json.dumps(status, indent=2), encoding="utf-8")
    return {"gemarkeerd": stand["gemarkeerd"], "bronnen": sum(len(v) for k, v in stand.items() if isinstance(v, dict)),
            "volgende_herinnering": "over een maand (of wat bijwerken.herinnering_dagen zegt)"}


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq bronnen", description="Bronnen van de gidsen controleren")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("markeer")
    a = p.parse_args(argv)
    uit = check() if a.cmd == "check" else markeer()
    print(json.dumps(uit, ensure_ascii=False, indent=2))
    sys.exit(0)
