"""Werk de sleuteltabel in docs/configuratie.md bij vanuit config/schema.json (alleen voor onderhoud).

  uv run --no-project --with-requirements requirements.txt python scripts/dev/configuratie_doc.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "config" / "schema.json").read_text(encoding="utf-8"))
DOC = ROOT / "docs" / "configuratie.md"
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
        return "lijst van " + " \\| ".join(f"`{x}`" for x in item.get("enum", [])) if "enum" in item else "lijst"
    return d.get("type", "")


def betekenis(d: dict) -> str:
    delen = [(d.get("x-label") or {}).get("nl", ""), (d.get("x-uitleg") or {}).get("nl", "")]
    return ". ".join(x.rstrip(".") for x in delen if x) + ("." if any(delen) else "")


def rij(sleutel: str, d: dict) -> str:
    std = "" if d.get("default") is None else f"`{json.dumps(d['default'], ensure_ascii=False)}`"
    return f"| `{sleutel}` | {waarden(d)} | {std} | {betekenis(d)} |"


def tabel() -> str:
    kop = "| Sleutel | Waarden | Standaard | Betekenis |\n|---|---|---|---|"
    regels = [kop]
    for k, d in SCHEMA["properties"].items():
        if d.get("type") == "object" and "properties" in d and k != "student":
            regels += [rij(f"{k}.{k2}", d2) for k2, d2 in d["properties"].items()]
        else:
            regels.append(rij(k, d))
    regels += ["", "**In een profiel** (`profielen.<naam>.…`):", "", kop]
    p = SCHEMA["$defs"]["profiel"]["properties"]
    for sectie in ("controles", "toon", "uitvoer"):
        regels += [rij(f"{sectie}.{k}", d) for k, d in p[sectie]["properties"].items()]
    regels.append("| `basis` | profielnaam |  | " + betekenis(p["basis"]) + " |")
    regels.append("| `taal` | `nl` \\| `en` \\| `auto` |  | Overschrijft de algemene taal voor dit profiel. |")
    return "\n".join(regels)


if __name__ == "__main__":
    tekst = DOC.read_text(encoding="utf-8")
    tekst = re.sub(re.escape(BEGIN) + r".*?" + re.escape(EIND), f"{BEGIN}\n{tabel()}\n{EIND}", tekst, flags=re.S)
    DOC.write_text(tekst, encoding="utf-8")
    print(f"{DOC} bijgewerkt")
