# Claude Code Setup

DutchQuill AI draait als project binnen [Claude Code](https://docs.anthropic.com/en/docs/claude-code), de CLI van Anthropic. Op deze pagina lees je hoe het systeem in elkaar zit en wat je kunt aanpassen.

## Project openen

```bash
cd /pad/naar/dutchquill-ai
claude
```

Claude Code herkent het `CLAUDE.md` bestand vanzelf en laadt de projectconfiguratie.

## CLAUDE.md

`CLAUDE.md` in de root bevat alle instructies voor Claude. Hierin staat:

- **WAT-framework:** hoe Workflows (instructies), Agent (beslisser) en Tools (uitvoering) samenwerken
- **Skill-uitvoering:** welke gidsen gelezen moeten worden en welke tools verplicht zijn
- **Exportconventies:** waar output naartoe gaat en welke bestanden gegenereerd worden
- **Schrijfstijlregels:** verboden woorden, verboden openers en regels voor academisch Nederlands

Claude leest dit bestand automatisch bij het starten van een sessie. Handmatig laden is niet nodig.

### Aanpassen

Je mag `CLAUDE.md` aanpassen, maar let op:
- De schrijfstijlregels zijn afgestemd op AI-detectietools
- De verplichte stappen in de skills zijn er niet voor niets
- Test na een wijziging of de workflows nog goed werken

## Skills

Skills zijn slash-commando's die je in Claude Code typt:

| Commando | Functie | Model |
|----------|---------|-------|
| `/schrijven` | Nieuwe rapportsectie schrijven | Sonnet 4.6 |
| `/herschrijven` | Bestaande tekst verbeteren | Sonnet 4.6 |
| `/reviewen` | Rapport nakijken op 4 domeinen | Sonnet 4.6 |
| `/humaniseer` | Snelle AI-detectiecheck | Haiku 4.5 |

De definities staan in `.claude/skills/<naam>/SKILL.md`.

## Agents

DutchQuill AI heeft een subagent:

| Agent | Functie | Model |
|-------|---------|-------|
| `tekst-analist` | Draait humanizer_nl.py en readability_nl.py | Haiku 4.5 |

De tekst-analist wordt automatisch aangeroepen vanuit de skills. De definitie staat in `.claude/agents/tekst-analist/AGENT.md`.

## Hooks

De stop-hook `check_verboden_woorden.py` draait na elke Claude-response:
- Checkt of de gegenereerde tekst verboden AI-woorden bevat
- Bij een match: exit code 2, waarna Claude de passage automatisch herschrijft

De configuratie staat in `.claude/settings.json` onder `hooks.Stop`.

## Memory

Claude Code heeft een geheugen dat blijft bestaan tussen sessies. De memory-bestanden staan buiten de repository (in `~/.claude/projects/`) en zijn persoonlijk per gebruiker.

### Wat wordt onthouden

- **Feedback:** correcties en bevestigingen over je werkwijze
- **Projectcontext:** lopend werk, deadlines, beslissingen
- **Voorkeuren:** hoe je het liefst met de tool werkt

### Memory opbouwen

Memory bouwt zich vanzelf op terwijl je werkt. Je kunt ook expliciet iets vragen:
- "Onthoud dat ik altijd APA 7 moet gebruiken"
- "Vergeet het vorige project"

### Geen memory? Geen probleem

Alles werkt ook zonder memory. Het enige verschil is dat Claude in een nieuwe sessie je voorkeuren niet kent en daarom wat meer vragen stelt.

## Settings

### settings.json (project)

Bevat vooraf goedgekeurde permissies voor alle tools en de hook-configuratie. Dit bestand wordt meegecommit.

### settings.local.json (persoonlijk)

Voor persoonlijke aanpassingen (extra permissies, eigen hooks). Dit bestand staat in `.gitignore`.

## Troubleshooting

**Tool wordt niet automatisch uitgevoerd:**
Check of de tool in `.claude/settings.json` onder `permissions.allow` staat.

**Hook blokkeert een response:**
De stop-hook heeft een verboden woord gevonden. Claude herschrijft de passage vanzelf. Is het onterecht? Kijk dan in de woordenlijst in `.claude/hooks/check_verboden_woorden.py`.

**Skill niet gevonden:**
Check of `SKILL.md` bestaat in `.claude/skills/<naam>/SKILL.md` en of de frontmatter klopt.
