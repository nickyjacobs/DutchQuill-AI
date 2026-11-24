import json

import pytest
from dutchquill import stem
from dutchquill.config import ConfigFout


def test_stem_analyse(werkmap):
    with pytest.raises(ConfigFout):
        stem.analyse()
    tekst = ("Ik schrijf graag kort. Soms ook wat langer, als het onderwerp erom vraagt en ik de tijd heb - "
             "zoals nu. Wat vind jij ervan? Ik ben benieuwd. ") * 6
    (werkmap / "1-input" / "mijn-stijl" / "blog.md").write_text(tekst)
    p = stem.analyse()
    assert p["bestanden"] == ["blog.md"] and p["streepjes_per_1000"] > 0
    assert json.loads((werkmap / ".dutchquill" / "stem.json").read_text())["woorden"] == p["woorden"]
