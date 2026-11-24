"""Werk de sleuteltabellen in docs/naslag/configuratie.md (NL) en docs/en/reference/configuration.md (EN) bij
vanuit config/schema.json (alleen voor onderhoud).

  uv run --no-project --with-requirements requirements.txt python scripts/dev/configuratie_doc.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "config" / "schema.json").read_text(encoding="utf-8"))
DOCS = {"nl": ROOT / "docs" / "naslag" / "configuratie.md",
        "en": ROOT / "docs" / "en" / "reference" / "configuration.md"}
TAAL = "nl"
BEGIN, EIND = "<!-- tabel:begin -->", "<!-- tabel:eind -->"


def _def(d: dict) -> dict:
    ref = d.get("$ref")
    if not ref:
        return d
    deel = ref.split("/")
    return SCHEMA["$defs"][deel[-1]] if deel[1] == "$defs" else SCHEMA["properties"][deel[-1]]


def waarden(d: dict) -> str:
    d = _def(d)
    if "enum" in d:
        return " \\| ".join(f"`{x}`" for x in d["enum"])
    if d.get("type") == "array":
        item = _def(d.get("items", {}))
        if "enum" not in item:
            return "lijst" if TAAL == "nl" else "list"
        return ("lijst van " if TAAL == "nl" else "list of ") + " \\| ".join(f"`{x}`" for x in item["enum"])
    return d.get("type", "")


def betekenis(d: dict) -> str:
    delen = [(d.get("x-label") or {}).get(TAAL, ""), (d.get("x-uitleg") or {}).get(TAAL, "")]
    return ". ".join(x.rstrip(".") for x in delen if x) + ("." if any(delen) else "")


def rij(sleutel: str, d: dict) -> str:
    std = "" if d.get("default") is None else f"`{json.dumps(d['default'], ensure_ascii=False)}`"
    return f"| `{sleutel}` | {waarden(d)} | {std} | {betekenis(d)} |"


def tabel() -> str:
    kop = ("| Sleutel | Waarden | Standaard | Betekenis |" if TAAL == "nl"
           else "| Key | Values | Default | Meaning |") + "\n|---|---|---|---|"
    regels = [kop]
    for k, d in SCHEMA["properties"].items():
        if d.get("type") == "object" and "properties" in d and k != "student":
            regels += [rij(f"{k}.{k2}", d2) for k2, d2 in d["properties"].items()]
        else:
            regels.append(rij(k, d))
    in_profiel = ("**In een profiel** (`profielen.<naam>.…`):" if TAAL == "nl"
                  else "**In a profile** (`profielen.<name>.…`):")
    regels += ["", in_profiel, "", kop]
    p = SCHEMA["$defs"]["profiel"]["properties"]
    for sectie in ("controles", "toon", "uitvoer"):
        regels += [rij(f"{sectie}.{k}", d) for k, d in p[sectie]["properties"].items()]
    naam = "profielnaam" if TAAL == "nl" else "profile name"
    regels.append(f"| `basis` | {naam} |  | " + betekenis(p["basis"]) + " |")
    regels.append("| `taal` | `nl` \\| `en` \\| `auto` |  | "
                  + ("Overschrijft de algemene taal voor dit profiel. |" if TAAL == "nl"
                     else "Overrides the general language for this profile. |"))
    return "\n".join(regels)


def main() -> None:
    global TAAL
    for TAAL, doc in DOCS.items():  # noqa: B007 - TAAL is de taal voor de hulpfuncties hierboven
        tekst = doc.read_text(encoding="utf-8")
        tekst = re.sub(re.escape(BEGIN) + r".*?" + re.escape(EIND), f"{BEGIN}\n{tabel()}\n{EIND}", tekst, flags=re.S)
        doc.write_text(tekst, encoding="utf-8")
        print(f"{doc} bijgewerkt")


if __name__ == "__main__":
    main()
