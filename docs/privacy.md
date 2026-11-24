<p align="right"><b>🇳🇱 Nederlands</b> · <a href="en/privacy.md">🇬🇧 English</a></p>

# Privacy

DutchQuill AI is een plugin voor Claude Code en draait op je eigen computer. De maker van DutchQuill verzamelt
niets: er is geen account, geen telemetrie, geen analytics en geen server van DutchQuill.

## Wat op je computer blijft

- Je teksten, bronnen en uitvoer staan in je werkmap. Die map is van jou.
- Je instellingen staan in `dutchquill.yaml` in je werkmap.
- De Python-omgeving en de cache staan in de datamap van de plugin, onder `~/.claude/plugins/data/`.
- DutchQuill Studio draait op 127.0.0.1, met een eenmalige sleutel. Andere apparaten kunnen er niet bij.

## Wat naar Claude gaat

Wat je in een gesprek met Claude deelt of laat lezen, gaat naar Anthropic, net als bij elk ander gesprek in Claude
Code. Daarvoor geldt het [privacybeleid van Anthropic](https://www.anthropic.com/legal/privacy), niet dit document.
DutchQuill stuurt je tekst nergens anders heen.

## Wat naar internet gaat, en wanneer

| Host | Wanneer | Wat er heen gaat |
|---|---|---|
| `api.languagetool.org` | Alleen als je de online taalcheck aanzet. Die staat standaard uit. | De tekst die je laat controleren en de taalcode. Daarvoor geldt het [privacybeleid van LanguageTool](https://languagetool.org/legal/privacy). |
| `pypi.org`, `files.pythonhosted.org` | De eerste keer dat een commando Python nodig heeft, en na een update | Een gewone download van de Python-pakketten. Geen tekst van jou. |
| `www.scribbr.nl`, `en.wikipedia.org`, `api.github.com` | Alleen als je `/dutchquill:bijwerken` geeft | Een aanvraag voor openbare pagina's, met de user-agent `DutchQuill-bronnencheck`. Geen tekst van jou. |

De hosts die de plugin mag bereiken, staan in `.claude-plugin/plugin.json` onder `network.hosts`. Interne adressen
(localhost, privé-IP's) in je materiaal haalt DutchQuill nooit automatisch op.

## Verwijderen

Typ `/plugin` in Claude Code, kies DutchQuill en verwijder hem. Je werkmap blijft staan. De datamap onder
`~/.claude/plugins/data/` kun je daarna weghalen; dan is alles van DutchQuill van je computer.

## Contact

- Een vraag of een fout: [GitHub Issues](https://github.com/nickyjacobs/DutchQuill-AI/issues).
- Een beveiligingsprobleem: meld het privé, zoals [SECURITY.md](../SECURITY.md) beschrijft.

Verandert dit beleid, dan staat dat in de [CHANGELOG](../CHANGELOG.md). Laatst bijgewerkt: 2026-11-25.
