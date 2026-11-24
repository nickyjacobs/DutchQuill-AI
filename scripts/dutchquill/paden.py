"""Waar alles staat: plugin, datamap, werkmap en projectconfig."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_CONFIG = ".dutchquill.yaml"
WERKMAP_CONFIG = "dutchquill.yaml"


def root() -> Path:
    """De map van de plugin (alleen-lezen: wordt bij elke update vervangen)."""
    env = os.environ.get("DUTCHQUILL_ROOT")
    return Path(env) if env else Path(__file__).resolve().parents[2]


def data() -> Path:
    """Blijvende datamap van de plugin: venv, werkmap-wijzer, bijwerkstatus, bijgewerkte gidsen."""
    env = os.environ.get("DUTCHQUILL_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    pad = Path(env) if env else root() / ".dev-data"
    pad.mkdir(parents=True, exist_ok=True)
    return pad


def wijzer() -> Path:
    return data() / "werkmap"


def project_config(start: Path | None = None) -> Path | None:
    """Zoek .dutchquill.yaml vanaf de huidige map omhoog, tot en met de thuismap."""
    huidig = (start or Path.cwd()).resolve()
    thuis = Path.home().resolve()
    for map_ in [huidig, *huidig.parents]:
        kandidaat = map_ / PROJECT_CONFIG
        if kandidaat.is_file():
            return kandidaat
        if map_ == thuis:
            break
    return None


def werkmap(projectwaarde: str | None = None) -> Path | None:
    """De werkmap: eerst uit de projectconfig, dan uit de wijzer in de datamap."""
    if projectwaarde:
        return Path(projectwaarde).expanduser().resolve()
    w = wijzer()
    if w.is_file():
        tekst = w.read_text(encoding="utf-8").strip()
        if tekst:
            return Path(tekst).expanduser()
    return None


def zet_werkmap(pad: Path) -> None:
    wijzer().write_text(str(pad.expanduser().resolve()) + "\n", encoding="utf-8")
