# Tokengebruik en kosten

De drie workflows draaien op **Claude Sonnet 4.6** via Claude Code. De tekst-analist subagent draait op **Haiku 4.5** om kosten te drukken. De schattingen hieronder zijn gebaseerd op de werkelijke bestandsgroottes in dit project.

---

## Wat bepaalt de kosten

- **Contextvenster:** CLAUDE.md, de schrijfstijlregels en de gidsen die tijdens de sessie gelezen worden, tellen altijd mee als input-tokens.
- **Tekstlengte:** hoe langer de aangeleverde of te schrijven tekst, hoe meer input- en output-tokens.
- **Aantal gidsen:** `/reviewen` leest alle vier gidsen; `/schrijven` leest er meestal een of twee.

---

## Kosten per workflow

Prijzen: Sonnet 4.6, **$3,00/M input en $15,00/M output** (Haiku 4.5 zie onderaan).

| Workflow | Scenario | Input-tokens | Output-tokens | Kosten (USD) | Kosten (EUR) |
|----------|----------|:------------:|:-------------:|:------------:|:------------:|
| `/schrijven` | klein, 1 gids, ~150 woorden output | 8.000 | 700 | $0,03 | €0,03 |
| `/schrijven` | typisch, 2 gidsen, ~300 woorden | 14.000 | 950 | $0,06 | €0,05 |
| `/schrijven` | groot, 3 gidsen, ~500 woorden | 20.000 | 1.300 | $0,08 | €0,07 |
| `/herschrijven` | klein, korte tekst (~200 woorden) | 12.000 | 1.200 | $0,05 | €0,05 |
| `/herschrijven` | typisch, middellange tekst (~500 woorden) | 22.000 | 2.000 | $0,10 | €0,09 |
| `/herschrijven` | groot, lange tekst (~1.000 woorden) | 35.000 | 3.000 | $0,15 | €0,14 |
| `/reviewen` | klein, ~300 woorden rapport | 15.000 | 1.500 | $0,07 | €0,06 |
| `/reviewen` | typisch, ~800 woorden rapport | 28.000 | 2.500 | $0,12 | €0,11 |
| `/reviewen` | groot, ~2.000 woorden rapport | 45.000 | 3.500 | $0,19 | €0,17 |

EUR-bedragen zijn indicatief op basis van een wisselkoers van ~1 USD = 0,92 EUR.

---

## Componentenbreakdown (input-tokens)

| Component | Tokens | Altijd geladen? |
|-----------|:------:|:---------------:|
| `CLAUDE.md` | ~1.200 | Ja |
| `.claude/rules/schrijfstijl.md` | ~242 | Ja |
| Claude Code systeemoverhead | ~500 | Ja |
| **Subtotaal basis** | **~2.000** | |
| Skill `/schrijven` | ~650 | Bij aanroep |
| Skill `/herschrijven` | ~484 | Bij aanroep |
| Skill `/reviewen` | ~588 | Bij aanroep |
| Gids `apa_nl_gids.md` | ~5.250 | Indien gelezen |
| Gids `humanize_nl_gids.md` | ~3.520 | Indien gelezen |
| Gids `academische_stijl_gids.md` | ~2.980 | Indien gelezen |
| Gids `taal_gids.md` | ~2.830 | Indien gelezen |

---

## Tekst-analist subagent (Haiku 4.5)

De subagent draait `humanizer_nl.py` en `readability_nl.py` en levert een beknopte analyse op. Hij wordt alleen gebruikt bij `/reviewen` wanneer de analyse-stap actief is.

Prijs: **$0,80/M input en $4,00/M output**

| Component | Tokens | Kosten |
|-----------|:------:|:------:|
| Input (AGENT.md + tool-output + instructie) | ~3.000 | $0,0024 |
| Output (gestructureerd rapport) | ~300 | $0,0012 |
| **Totaal per aanroep** | | **~$0,004 (<€0,01)** |

---

## Tips om kosten laag te houden

- Plak de tekst direct in de chat. Dat scheelt extra tool-calls om bestanden in te lezen.
- Weet je wat je wilt checken? Vraag dan een gerichte review (bijv. "alleen APA"), zodat Claude minder gidsen hoeft te laden.
- Houd sessies kort. Een lang gesprek stapelt context op. Sluit de sessie af zodra je de output hebt.

---

## Prijsnota

Actuele prijzen: [anthropic.com/pricing](https://www.anthropic.com/pricing). Bedragen zijn exclusief btw. Deze kosten gelden bij API-gebruik; met een Claude Pro- of Max-abonnement betaal je een vaste maandprijs zonder per-token factuur.
