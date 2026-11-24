import importlib.util
from pathlib import Path

PAD = Path(__file__).resolve().parents[1] / "scripts" / "dev" / "release_check.py"
spec = importlib.util.spec_from_file_location("release_check", PAD)
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)


def test_repo_is_releaseklaar():
    assert rc.controleer() == []


def test_tag_moet_bij_changelog_passen():
    versie = rc.versies_in_code()["plugin.json"]
    assert rc.controleer(f"v{versie}") == []
    assert rc.controleer("v99.0.0")


def test_notes_beginnen_met_in_short():
    versie = rc.versies_in_code()["plugin.json"]
    tekst = rc.notes(f"v{versie}")
    assert tekst.startswith("> **In short:**") and "## [" not in tekst
