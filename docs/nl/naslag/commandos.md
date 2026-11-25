<p align="right"><a href="../../reference/commands.md">🇬🇧 English</a> · <b>🇳🇱 Dutch</b></p>

# Commando's

## In Claude Code

| Commando | Wat het doet |
|---|---|
| `/dutchquill:schrijven` | Nieuwe tekst, vanuit je vraag of je materiaal in de werkmap. Documenten krijgen eerst een opzet. |
| `/dutchquill:herschrijven` | Verbeteren, inkorten, formeler of luchtiger, vertalen NL↔EN. Feiten blijven gelijk. |
| `/dutchquill:reviewen` | Nakijken zonder iets te veranderen: taal, structuur, toon, AI-patronen, en (als dat aan staat) APA en de rubric van je vak. |
| `/dutchquill:humaniseren` | AI-patronen eruit, in je eigen stem; of alleen een scan. |
| `/dutchquill:instellen` | Werkmap, profielen, controles, toon, templates en privacy, visueel (Studio) of in de chat. |
| `/dutchquill:bijwerken` | De referentiegidsen controleren tegen hun bronnen en per gids een update voorstellen. |

De commando's hoef je niet te onthouden: "schrijf een mail aan ..." of "klinkt dit als AI?" werkt ook.

## Subagents

| Subagent | Wat hij doet |
|---|---|
| `bronnen-lezer` | Leest veel materiaal tegelijk en maakt er één samenvatting van, met kernpunten, citaten met paginanummer en een voorstel voor de plek van elk beeld. |
| `stem-analist` | Maakt van je teksten in `mijn-stijl/` een stemprofiel. |
| `tekst-analist` | Draait de analyses op een tekst (AI-patronen, leesbaarheid, voor en na) en geeft alleen de cijfers terug. |

## `dq`: de gereedschapskist

De skills roepen `dq` aan; je kunt het ook zelf gebruiken. `dq <commando> --help` geeft de opties.

| Commando | Wat het doet |
|---|---|
| `dq doctor` | Omgeving controleren: Python, pakketten, werkmap, hoe pdf's gemaakt worden |
| `dq config toon` / `zet` / `valideer` / `profielen` | De samengevoegde config tonen, één instelling zetten, het bestand controleren |
| `dq werkmap init` / `pad` / `status` | Een werkmap aanmaken, het pad tonen, de stand van de werkmap |
| `dq studio` | DutchQuill Studio starten |
| `dq materiaal inventaris` / `verzamel` | Wat er in `1-input/` staat, en wat nieuw is |
| `dq extraheer` | .docx, .pdf, .pptx, .xlsx, .csv en .html naar tekst |
| `dq beeld` | Beelden klaarmaken (oriëntatie, metadata eruit, HEIC naar PNG) |
| `dq tells` | AI-patronen meten (`--compare` voor voor en na, `--json` voor alles) |
| `dq feiten` | Feitencontrole tussen origineel en nieuwe versie |
| `dq leesbaarheid` | Flesch-Douma en zinslengte |
| `dq stem` | Stemprofiel meten uit `mijn-stijl/` |
| `dq export` | Markdown naar docx, pdf, html, md en txt, met een template |
| `dq template lijst` / `check` / `aanpas` | Word-templates tonen, controleren, een aangepaste kopie maken |
| `dq versie volgende` / `laatste` / `lijst` | Versiemappen in `2-output/` |
| `dq historie toon` / `log` | De geschiedenis van je opdrachten tonen of aanvullen |
| `dq gids voor` / `pad` / `diff` / `schrijf` | Welke gidsen bij een opdracht horen; een bijgewerkte gids vergelijken en wegschrijven |
| `dq bronnen check` / `markeer` | De bronnen van de gidsen controleren |
| `dq vak toon` / `lijst` | De inlevereisen en rubric van een vak, alleen de sectie `## Rapportage` |
| `dq apa-check`, `dq apa-bron` | APA-controles en bronvermeldingen |
| `dq taalcheck` | LanguageTool, alleen als de online taalcheck aan staat |
| `dq reviewgrafiek` | Het overzichtsbeeld bovenaan een review: AI-patronen, leesbaarheid, woordvariatie, taalronde en de zwaarste patronen |
| `dq diff`, `dq docx-tekst`, `dq grafiek`, `dq diagram` | Woordverschil, .docx naar Markdown, grafieken en diagrammen als png |

Buiten Claude Code staat `dq` in de pluginmap (`scripts/dq`). Bij het eerste gebruik maakt het een eigen
Python-omgeving in de datamap van de plugin.
