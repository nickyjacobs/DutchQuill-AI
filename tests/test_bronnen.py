import json

from dutchquill import bronnen, gidsen, paden


class Antwoord:
    def __init__(self, content=b"", data=None, text=""):
        self.content, self._data, self.text = content, data, text

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


INDEX = (b'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap>'
         b"<loc>https://www.scribbr.nl/post-sitemap.xml</loc></sitemap></sitemapindex>")


def nep(lastmod_apa: str, revid: int, tag: str, paginatekst: str):
    def _get(url, timeout=20):
        if url.endswith("sitemap_index.xml"):
            return Antwoord(INDEX)
        if url.endswith("post-sitemap.xml"):
            return Antwoord((
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<url><loc>https://www.scribbr.nl/apa-stijl/verwijzing-in-de-tekst/</loc>'
                f'<lastmod>{lastmod_apa}T10:00:00+00:00</lastmod></url>'
                '</urlset>').encode())
        if "wikipedia.org" in url:
            rev = {"revid": revid, "timestamp": "2026-01-01T00:00:00Z"}
            return Antwoord(data={"query": {"pages": {"1": {"revisions": [rev]}}}})
        if "api.github.com" in url:
            return Antwoord(data={"tag_name": tag})
        return Antwoord(text=paginatekst)
    return _get


def test_eerste_check_en_wijzigingen(monkeypatch):
    monkeypatch.setattr(bronnen, "_get", nep("2026-01-01", 100, "v4.0.0", "zelfde"))
    r = bronnen.check()
    assert r["gewijzigd"] == [] and r["fouten"] == []
    bronnen.markeer()
    status = json.loads((paden.data() / "bijwerken.json").read_text())
    assert status["laatst_gecontroleerd"]

    monkeypatch.setattr(bronnen, "_get", nep("2099-01-01", 101, "v5.0.0", "anders"))
    r = bronnen.check()
    soorten = {g["soort"] for g in r["gewijzigd"]}
    assert {"scribbr", "wikipedia", "github", "pagina"} <= soorten
    apa = next(g for g in r["gewijzigd"] if g["soort"] == "scribbr")
    assert "nl/apa" in apa["gidsen"]


def test_gids_diff_en_schrijf(tmp_path):
    huidig = gidsen.pad("toon").read_text(encoding="utf-8")
    voorstel = tmp_path / "toon.md"
    voorstel.write_text(huidig.replace("# Toon", "# Toon (bijgewerkt)"), encoding="utf-8")
    assert "+# Toon (bijgewerkt)" in gidsen.diff("toon", voorstel)
    r = gidsen.schrijf("toon", voorstel)
    assert r["geschreven"].startswith(str(paden.data()))
    assert gidsen.pad("toon") == paden.data() / "gidsen" / "toon.md"  # de nieuwe versie wint
