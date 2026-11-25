<p align="right"><a href="../../guide/faq.md">🇬🇧 English</a> · <b>🇳🇱 Dutch</b></p>

# Vragen

## Wat gaat er naar internet?

- Je teksten blijven op je computer en in je gesprek met Claude.
- De online taalcheck (LanguageTool) staat standaard uit. Zet je hem aan, dan gaat je tekst naar
  api.languagetool.org.
- `/dutchquill:bijwerken` haalt alleen openbare pagina's op (de sitemap van Scribbr NL, Wikipedia, GitHub), en
  alleen als jij het commando geeft.
- De eerste keer installeert DutchQuill zijn Python-pakketten van PyPI, in de datamap van de plugin.
- DutchQuill Studio draait alleen op je eigen computer (127.0.0.1).

De hosts die de plugin mag bereiken, staan in `.claude-plugin/plugin.json` onder `network.hosts`. Het volledige
overzicht staat in het [privacybeleid](../privacy.md).

## Controleert DutchQuill mijn spelling ook zonder LanguageTool?

Ja. Elke tekst krijgt als laatste stap een taalronde: Claude leest hem zin voor zin na op spelling, d/t, komma's en
consistentie en herstelt wat hij vindt; een review zet het als bevindingen in het rapport. De online taalcheck met
LanguageTool komt daar bovenop en vangt meer kleine fouten, maar stuurt je tekst naar api.languagetool.org. Daarom
staat die standaard uit.

## Welke metadata zet DutchQuill in mijn bestand?

Standaard de titel en de auteur uit je tekst of profiel, en niets over het gereedschap: een pdf heeft geen
maker of producent. In Word zijn de aanmaaktijd en de revisie wat python-docx zet (nu, en 1). DutchQuill verzint
nooit metadata zoals een bewerkingstijd, een aantal revisies of een eerdere datum.

Wil je niets herleidbaars in het bestand, bijvoorbeeld voor een stuk dat naar buiten gaat? Zet
**Documentgegevens** op **Leeg** in de Studio (Uitvoer), of `dq config zet uitvoer.metadata leeg`. Dan blijven in
Word auteur, laatst gewijzigd door, titel, onderwerp, trefwoorden, opmerkingen, bedrijf, manager en het programma
leeg, en in de pdf titel en auteur. Er komt niets anders voor in de plaats.

## Kost het iets?

DutchQuill zelf is gratis (MIT). Het draait in Claude Code, dus je gebruikt je eigen Claude-abonnement of API-tegoed.

## Mijn pdf lijkt niet op mijn Word-bestand

Zonder LibreOffice maakt DutchQuill de pdf via je browser, in een eigen opmaak. Installeer LibreOffice (gratis)
voor een pdf die precies op het Word-bestand lijkt. `dq doctor` laat zien welke route je hebt en hoe je
LibreOffice installeert.

## Werkt het op Windows?

Ja. De tests draaien op Windows, macOS en Linux. Op Windows heb je Python 3.10 of nieuwer nodig, of uv.

## Werkt het in het Engels?

Ja. Zet de taal op Engels of `auto` (dan volgt DutchQuill de taal van je materiaal). De gidsen voor humaniseren en
stijl bestaan in beide talen, `dq tells` rapporteert in de taal van de tekst, en de Studio heeft een Engelse
versie. APA-regels en academische stijl zijn op het Nederlandse hbo gericht.

## Hoe houd ik DutchQuill bij?

Typ `/plugin` in Claude Code en kies bij DutchQuill voor bijwerken. Wat er per versie veranderd is, staat in de
[CHANGELOG](../../../CHANGELOG.md). De referentiegidsen controleer je los met `/dutchquill:bijwerken`; je krijgt daar
één keer per maand een herinnering voor.

## Hoe verwijder ik DutchQuill?

Typ `/plugin` in Claude Code, kies DutchQuill en verwijder hem. Je werkmap blijft staan; die is van jou. De
Python-omgeving van DutchQuill staat in de datamap van de plugin, onder `~/.claude/plugins/data/`; die map kun je
daarna weghalen.

## Ik kom van v1

Versie 1 was een map die je opende in Claude Code. Versie 2 is een plugin. Je oude map blijft werken zoals hij
was. Neem je rapporten mee door ze in de nieuwe werkmap te zetten (`1-input/rapporten/`), en vul je
studentgegevens in via `/dutchquill:instellen`.

## Iets werkt niet

Draai `dq doctor` en open een [issue](https://github.com/nickyjacobs/DutchQuill-AI/issues/new/choose) met de
uitvoer. Haal eerst alles weg wat privé is.
