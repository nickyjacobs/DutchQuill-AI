"""De bash-ingang scripts/dq: waar de datamap komt als de gewone niet beschrijfbaar is."""
import os
import shutil
import subprocess
import sys

import pytest
from dutchquill.paden import root

pytestmark = pytest.mark.skipif(sys.platform == "win32" or not shutil.which("bash"), reason="bash-script")


def draai(env_extra, cwd):
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PLUGIN_DATA", "DUTCHQUILL_DATA", "EVAL_DQ_DATA")}
    env.update(env_extra, DQ_NIET_INSTALLEREN="1")
    return subprocess.run(["bash", str(root() / "scripts" / "dq"), "tells"], cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=60)


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root mag overal schrijven")
def test_valt_terug_op_tijdelijke_map(tmp_path):
    ro = tmp_path / "ro"
    ro.mkdir()
    ro.chmod(0o555)
    try:
        r = draai({"CLAUDE_PLUGIN_DATA": str(ro / "data"), "TMPDIR": str(tmp_path / "tmp")}, tmp_path)
    finally:
        ro.chmod(0o755)
    assert r.returncode == 0, r.stderr
    assert "kan niet schrijven in" in r.stderr
    assert any(p.name.startswith("dutchquill-data-") for p in (tmp_path / "tmp").iterdir())


def test_eval_datamap_relatief_aan_werkmap(tmp_path):
    r = draai({"CLAUDE_PLUGIN_DATA": str(tmp_path / "plugin"), "EVAL_DQ_DATA": ".dq-data"}, tmp_path)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / ".dq-data").is_dir() and not (tmp_path / "plugin").exists()


def test_lichte_commandos_hebben_alleen_ruamel_nodig():
    """Een commando in de basislijst van scripts/dq mag niets buiten de standaardbibliotheek en ruamel.yaml laden."""
    import ast
    tekst = (root() / "scripts" / "dq").read_text(encoding="utf-8")
    regel = next(r for r in tekst.splitlines() if 'NIVEAU="basis"' in r and "config|" in r)
    from dutchquill import cli
    modules = {cli.EIGEN.get(c) or cli.TOOLS.get(c, (None,))[0] for c in regel.split(")")[0].strip().split("|")}
    toegestaan = set(sys.stdlib_module_names) | {"ruamel", "dutchquill"}
    for m in sorted(x for x in modules if x):
        boom = ast.parse((root() / "scripts" / "dutchquill" / f"{m.replace('.', '/')}.py").read_text(encoding="utf-8"))
        for knoop in ast.walk(boom):
            if isinstance(knoop, ast.Import):
                namen = [a.name for a in knoop.names]
            elif isinstance(knoop, ast.ImportFrom) and knoop.level == 0:
                namen = [knoop.module or ""]
            else:
                continue
            for naam in namen:
                assert naam.split(".")[0] in toegestaan, f"{m} laadt {naam}"
