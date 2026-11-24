"""De config van DutchQuill: laden, samenvoegen, valideren en aanpassen.

Voorrang (laag naar hoog): standaardwaarden uit het schema, werkmapconfig (dutchquill.yaml), het actieve
profiel (met zijn basis-keten), de projectconfig (.dutchquill.yaml), en losse --set-waarden uit de prompt.

Commando's (via scripts/dq):
  dq config toon [--genre G] [--profiel P] [--set sleutel=waarde ...] [--kort]
  dq config zet <sleutel> <waarde>
  dq config valideer
  dq config profielen
  dq config profiel nieuw <naam> [--basis B] [--beschrijving T]
  dq config profiel kies <naam>
  dq config profiel verwijder <naam>
"""

from __future__ import annotations

import argparse
import copy
import io
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from dutchquill import __version__, paden
from dutchquill.schema_check import standaardwaarden, valideer

PROFIEL_SLEUTELS = ("controles", "toon", "uitvoer", "taal")
# Bij `dq config zet` gaan alleen deze naar het actieve profiel; `taal` blijft dan een algemene instelling.
NAAR_PROFIEL = ("controles", "toon", "uitvoer")
INGEBOUWDE_TEMPLATES = ("apa-hbo", "zakelijk", "notitie")


class ConfigFout(Exception):
    pass


# ---------------------------------------------------------------- laden


def _yaml(rt: bool = True) -> YAML:
    y = YAML(typ="rt" if rt else "safe")
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=4, offset=2)
    y.width = 120
    return y


def naar_dict(obj: Any) -> Any:
    """ruamel-objecten (CommentedMap/Seq) naar gewone dicts en lists."""
    if isinstance(obj, dict):
        return {str(k): naar_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [naar_dict(v) for v in obj]
    return obj


def laad_yaml(pad: Path) -> Any:
    try:
        with pad.open(encoding="utf-8") as f:
            data = _yaml().load(f)
    except Exception as e:  # YAML-fout: duidelijk melden, niet crashen met een stacktrace
        raise ConfigFout(f"{pad} is geen geldige YAML: {e}") from e
    return data if data is not None else {}


def schema() -> dict:
    with (paden.root() / "config" / "schema.json").open(encoding="utf-8") as f:
        return json.load(f)


def ingebouwde_profielen() -> dict:
    return naar_dict(laad_yaml(paden.root() / "config" / "profielen.yaml"))


def diep_samenvoegen(basis: dict, boven: dict) -> dict:
    uit = copy.deepcopy(basis)
    for k, v in boven.items():
        if isinstance(v, dict) and isinstance(uit.get(k), dict):
            uit[k] = diep_samenvoegen(uit[k], v)
        else:
            uit[k] = copy.deepcopy(v)
    return uit


def _profiel_standaard(sch: dict) -> dict:
    return standaardwaarden(sch["$defs"]["profiel"], sch) or {}


def profiel_keten(naam: str, eigen: dict, ingebouwd: dict) -> list[tuple[str, dict]]:
    """Van het verste basisprofiel tot het gevraagde profiel."""
    keten: list[tuple[str, dict]] = []
    gezien: set[str] = set()
    huidig: str | None = naam
    while huidig:
        if huidig in gezien:
            raise ConfigFout(f"Profiel '{naam}' verwijst in een kring naar zichzelf (via '{huidig}').")
        gezien.add(huidig)
        if huidig in eigen:
            data = eigen[huidig] or {}
        elif huidig in ingebouwd:
            data = ingebouwd[huidig]
        else:
            bekend = ", ".join(sorted({*ingebouwd, *eigen}))
            raise ConfigFout(f"Onbekend profiel '{huidig}'. Bekend: {bekend}.")
        keten.append((huidig, data))
        huidig = data.get("basis")
    return list(reversed(keten))


def _zet_pad(doel: dict, sleutel: str, waarde: Any) -> None:
    delen = sleutel.split(".")
    for d in delen[:-1]:
        if not isinstance(doel.get(d), dict):
            doel[d] = {}
        doel = doel[d]
    doel[delen[-1]] = waarde


def parse_waarde(tekst: str) -> Any:
    """Waarde uit de opdrachtregel als YAML lezen: true, 3, [docx, pdf], tekst."""
    try:
        return naar_dict(YAML(typ="safe").load(io.StringIO(tekst)))
    except Exception:
        return tekst


def werkmap_en_bestanden() -> tuple[Path | None, Path | None, dict, Path | None, dict]:
    """(werkmap, werkmapconfig-pad, werkmapconfig, projectconfig-pad, projectconfig)."""
    project_pad = paden.project_config()
    project = naar_dict(laad_yaml(project_pad)) if project_pad else {}
    werkmap = paden.werkmap(project.get("werkmap"))
    cfg_pad = werkmap / paden.WERKMAP_CONFIG if werkmap else None
    cfg = naar_dict(laad_yaml(cfg_pad)) if cfg_pad and cfg_pad.is_file() else {}
    return werkmap, cfg_pad, cfg, project_pad, project


def effectief(genre: str | None = None, profiel: str | None = None, sets: list[str] | None = None) -> dict:
    sch = schema()
    ingebouwd = ingebouwde_profielen()
    werkmap, cfg_pad, cfg, project_pad, project = werkmap_en_bestanden()
    waarschuwingen: list[str] = []

    alg = diep_samenvoegen(standaardwaarden(sch, sch), cfg)
    project_alg = {k: v for k, v in project.items() if k not in PROFIEL_SLEUTELS and k != "werkmap"}
    alg = diep_samenvoegen(alg, project_alg)

    gekozen = profiel or (alg.get("genre_profielen", {}).get(genre) if genre else None) or alg["profiel"]
    keten = profiel_keten(gekozen, alg.get("profielen", {}), ingebouwd)
    prof = _profiel_standaard(sch)
    for _, deel in keten:
        prof = diep_samenvoegen(prof, {k: v for k, v in deel.items() if k in PROFIEL_SLEUTELS})
    prof = diep_samenvoegen(prof, {k: v for k, v in project.items() if k in PROFIEL_SLEUTELS})

    for s in sets or []:
        if "=" not in s:
            raise ConfigFout(f"--set verwacht sleutel=waarde, kreeg '{s}'")
        k, v = s.split("=", 1)
        doel = prof if k.split(".")[0] in PROFIEL_SLEUTELS else alg
        _zet_pad(doel, k.strip(), parse_waarde(v.strip()))

    taal = prof.get("taal") or alg["taal"]
    mappen = alg["mappen"]
    abs_mappen = {}
    if werkmap:
        inp, outp = werkmap / mappen["input"], werkmap / mappen["output"]
        abs_mappen = {
            "werkmap": str(werkmap),
            "input": str(inp),
            "output": str(outp),
            **{k: str(inp / mappen[k]) for k in ("notities", "rapporten", "beeld", "bronnen", "mijn_stijl")},
            **{k: str(outp / mappen[k]) for k in ("schrijven", "herschrijven", "reviewen", "humaniseren")},
            "templates": str(werkmap / mappen["templates"]),
            "eigen_regels": str(werkmap / "eigen-regels.md"),
            "stemprofiel": str(werkmap / "stemprofiel.md"),
            "intern": str(werkmap / ".dutchquill"),
        }
        if not cfg_pad or not cfg_pad.is_file():
            waarschuwingen.append(f"Geen {paden.WERKMAP_CONFIG} in {werkmap}: standaardwaarden gebruikt.")

    template = prof["uitvoer"].get("template")
    if template and template not in INGEBOUWDE_TEMPLATES and template not in alg.get("templates", {}):
        waarschuwingen.append(f"Template '{template}' bestaat niet; gebruik een meegeleverde of registreer hem.")
    if prof["controles"].get("apa") and prof["toon"].get("niveau") in ("informeel", "luchtig"):
        waarschuwingen.append("APA staat aan met een informele toon; dat botst meestal.")

    return {
        "ingesteld": werkmap is not None and werkmap.is_dir(),
        "werkmap": str(werkmap) if werkmap else None,
        "taal": taal,
        "genre": genre,
        "profiel": gekozen,
        "profiel_keten": [n for n, _ in keten],
        "controles": prof["controles"],
        "toon": prof["toon"],
        "uitvoer": prof["uitvoer"],
        "versies": alg["versies"],
        "privacy": alg["privacy"],
        "stem": alg["stem"],
        "student": alg.get("student", {}),
        "templates": alg.get("templates", {}),
        "stijlen": alg.get("stijlen", {}),
        "genre_profielen": alg.get("genre_profielen", {}),
        "eigen_profielen": sorted(alg.get("profielen", {})),
        "bijwerken": alg["bijwerken"],
        "mappen": abs_mappen,
        "configbestanden": [str(p) for p in (cfg_pad, project_pad) if p and p.is_file()],
        "plugin": {"versie": __version__, "root": str(paden.root()), "data": str(paden.data())},
        "waarschuwingen": waarschuwingen,
    }


# ---------------------------------------------------------------- valideren


def valideer_config(cfg: dict, project: bool = False) -> list[str]:
    sch = schema()
    if project:
        sch = copy.deepcopy(sch)
        sch["properties"]["werkmap"] = {"type": "string"}
        for k in ("controles", "toon", "uitvoer"):
            sch["properties"][k] = sch["$defs"]["profiel"]["properties"][k]
    fouten = valideer(cfg, sch)
    ingebouwd = ingebouwde_profielen()
    eigen = cfg.get("profielen", {}) or {}
    for naam in eigen:
        if naam in ingebouwd:
            fouten.append(f"profielen.{naam}: deze naam is van een meegeleverd profiel; kies een andere naam")
    for naam in [cfg.get("profiel"), *eigen, *(cfg.get("genre_profielen") or {}).values()]:
        if naam:
            try:
                profiel_keten(naam, eigen, ingebouwd)
            except ConfigFout as e:
                fouten.append(str(e))
    return sorted(set(fouten))


# ---------------------------------------------------------------- schrijven


def _hook_status_bijwerken(cfg: dict) -> None:
    """De SessionStart-hook leest geen YAML; geef hem de paar waarden die hij nodig heeft als JSON."""
    dagen = (cfg.get("bijwerken") or {}).get("herinnering_dagen", 30)
    (paden.data() / "hook.json").write_text(json.dumps({"herinnering_dagen": dagen}), encoding="utf-8")


def schrijf_config(pad: Path, data: Any) -> None:
    fouten = valideer_config(naar_dict(data))
    if fouten:
        raise ConfigFout("Niet opgeslagen, de config klopt niet:\n- " + "\n- ".join(fouten))
    if pad.is_file():
        shutil.copy2(pad, pad.with_suffix(pad.suffix + ".bak"))
    tmp = pad.with_suffix(pad.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        _yaml().dump(data, f)
    tmp.replace(pad)
    _hook_status_bijwerken(naar_dict(data))


def _laad_werkmapconfig_rt() -> tuple[Path, Any]:
    werkmap, cfg_pad, *_ = werkmap_en_bestanden()
    if not werkmap or not cfg_pad:
        raise ConfigFout("Nog geen werkmap ingesteld. Draai eerst /dutchquill:instellen.")
    data = laad_yaml(cfg_pad) if cfg_pad.is_file() else _yaml().load("{}")
    return cfg_pad, data


def _rt_pad(data: Any, delen: list[str]) -> Any:
    for d in delen:
        if d not in data or not isinstance(data[d], dict):
            data[d] = {}
        data = data[d]
    return data


def zet(sleutel: str, waarde: Any) -> str:
    """Pas één instelling aan. Profielinstellingen gaan naar het actieve profiel; is dat een meegeleverd
    profiel, dan maakt dit een eigen kopie '<naam>-eigen' en zet die actief. Geeft een uitleg terug."""
    pad, data = _laad_werkmapconfig_rt()
    delen = sleutel.split(".")
    melding = ""
    if delen[0] in NAAR_PROFIEL:
        actief = data.get("profiel") or schema()["properties"]["profiel"]["default"]
        eigen = data.get("profielen") or {}
        if actief not in eigen:
            nieuw = f"{actief}-eigen"
            profielen = _rt_pad(data, ["profielen"])
            if nieuw not in profielen:
                profielen[nieuw] = {"basis": actief}
            data["profiel"] = nieuw
            melding = (f"'{actief}' is meegeleverd en blijft ongewijzigd; "
                       f"aangepast in eigen profiel '{nieuw}' (nu actief). ")
            actief = nieuw
        doel = _rt_pad(data, ["profielen", actief, *delen[:-1]])
        doel[delen[-1]] = waarde
        melding += f"profielen.{actief}.{sleutel} = {json.dumps(naar_dict(waarde), ensure_ascii=False)}"
    else:
        doel = _rt_pad(data, delen[:-1])
        doel[delen[-1]] = waarde
        melding = f"{sleutel} = {json.dumps(naar_dict(waarde), ensure_ascii=False)}"
    schrijf_config(pad, data)
    return melding


def profiel_nieuw(naam: str, basis: str | None, beschrijving: str | None) -> str:
    pad, data = _laad_werkmapconfig_rt()
    profielen = _rt_pad(data, ["profielen"])
    if naam in profielen or naam in ingebouwde_profielen():
        raise ConfigFout(f"Profiel '{naam}' bestaat al.")
    nieuw: dict = {"basis": basis or data.get("profiel") or "zakelijk"}
    if beschrijving:
        nieuw["beschrijving"] = beschrijving
    profielen[naam] = nieuw
    schrijf_config(pad, data)
    return f"Profiel '{naam}' gemaakt (basis: {nieuw['basis']}). Kies het met: dq config profiel kies {naam}"


def profiel_kies(naam: str) -> str:
    pad, data = _laad_werkmapconfig_rt()
    data["profiel"] = naam
    schrijf_config(pad, data)
    return f"Actief profiel: {naam}"


def profiel_verwijder(naam: str) -> str:
    pad, data = _laad_werkmapconfig_rt()
    profielen = data.get("profielen") or {}
    if naam not in profielen:
        raise ConfigFout(f"'{naam}' is geen eigen profiel (meegeleverde profielen kun je niet verwijderen).")
    afhankelijk = [n for n, p in profielen.items() if (p or {}).get("basis") == naam]
    if afhankelijk:
        raise ConfigFout(f"Kan niet: {', '.join(afhankelijk)} bouwt voort op '{naam}'.")
    basis = (profielen[naam] or {}).get("basis", "zakelijk")
    del profielen[naam]
    extra = ""
    if data.get("profiel") == naam:
        data["profiel"] = basis
        extra = f" Actief profiel is nu '{basis}'."
    gp = data.get("genre_profielen") or {}
    for g in [g for g, p in gp.items() if p == naam]:
        del gp[g]
        extra += f" Genre '{g}' volgt weer het actieve profiel."
    schrijf_config(pad, data)
    return f"Profiel '{naam}' verwijderd (backup: {pad.name}.bak).{extra}"


# ---------------------------------------------------------------- weergave


def kort(e: dict) -> str:
    c = e["controles"]
    aan = [n for n, k in (("APA", "apa"), ("academische stijl", "academische_stijl"),
                          ("taal", "taalregels"), ("humaniseren", "humaniseren")) if c.get(k)]
    basis = " > ".join(e["profiel_keten"][:-1])
    regels = [
        f"Werkmap: {e['werkmap'] or 'nog niet ingesteld (/dutchquill:instellen)'}",
        f"Profiel: {e['profiel']}" + (basis and f" (bouwt op {basis})"),
        f"Taal: {e['taal']} | Toon: {e['toon']['niveau']}, aanspreekvorm {e['toon']['aanspreekvorm']}"
        + (f", mix: {e['toon']['mix']}" if e['toon'].get('mix') else ""),
        f"Controles aan: {', '.join(aan) or 'geen'}",
        f"Uitvoer: {', '.join(e['uitvoer']['formaten'])} | template {e['uitvoer']['template']} | "
        f"alleen chat: {', '.join(e['uitvoer']['chat_voor'])}",
        f"Online taalcheck: {'aan' if e['privacy']['languagetool'] else 'uit'} | "
        f"Versies: {'aan' if e['versies'] else 'uit'}",
    ]
    regels += [f"Let op: {w}" for w in e["waarschuwingen"]]
    return "\n".join(regels)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq config", description="DutchQuill-config tonen en aanpassen")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("toon", help="Samengevoegde config (JSON)")
    t.add_argument("--genre")
    t.add_argument("--profiel")
    t.add_argument("--set", action="append", default=[], metavar="SLEUTEL=WAARDE")
    t.add_argument("--kort", action="store_true", help="Korte samenvatting in gewone taal")
    z = sub.add_parser("zet", help="Eén instelling aanpassen")
    z.add_argument("sleutel")
    z.add_argument("waarde")
    sub.add_parser("valideer", help="Werkmap- en projectconfig controleren")
    sub.add_parser("profielen", help="Alle profielen tonen")
    sub.add_parser("schema", help="Pad naar het schema")
    pr = sub.add_parser("profiel", help="Eigen profielen beheren")
    prs = pr.add_subparsers(dest="actie", required=True)
    n = prs.add_parser("nieuw")
    n.add_argument("naam")
    n.add_argument("--basis")
    n.add_argument("--beschrijving")
    prs.add_parser("kies").add_argument("naam")
    prs.add_parser("verwijder").add_argument("naam")
    a = p.parse_args(argv)

    try:
        if a.cmd == "toon":
            e = effectief(a.genre, a.profiel, a.set)
            print(kort(e) if a.kort else json.dumps(e, ensure_ascii=False, indent=2))
        elif a.cmd == "zet":
            print(zet(a.sleutel, parse_waarde(a.waarde)))
        elif a.cmd == "valideer":
            werkmap, cfg_pad, cfg, project_pad, project = werkmap_en_bestanden()
            fouten = []
            if cfg_pad and cfg_pad.is_file():
                fouten += [f"{cfg_pad.name}: {f}" for f in valideer_config(cfg)]
            if project_pad:
                fouten += [f"{project_pad}: {f}" for f in valideer_config(project, project=True)]
            if fouten:
                print("Config bevat fouten:\n- " + "\n- ".join(fouten))
                sys.exit(1)
            print("Config is geldig.")
        elif a.cmd == "profielen":
            _, _, cfg, _, _ = werkmap_en_bestanden()
            uit = {"meegeleverd": {k: v.get("beschrijving", "") for k, v in ingebouwde_profielen().items()},
                   "eigen": {k: {"basis": (v or {}).get("basis"), "beschrijving": (v or {}).get("beschrijving", "")}
                             for k, v in (cfg.get("profielen") or {}).items()},
                   "actief": cfg.get("profiel", "zakelijk")}
            print(json.dumps(uit, ensure_ascii=False, indent=2))
        elif a.cmd == "schema":
            print(paden.root() / "config" / "schema.json")
        elif a.cmd == "profiel":
            if a.actie == "nieuw":
                print(profiel_nieuw(a.naam, a.basis, a.beschrijving))
            elif a.actie == "kies":
                print(profiel_kies(a.naam))
            else:
                print(profiel_verwijder(a.naam))
    except ConfigFout as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)
