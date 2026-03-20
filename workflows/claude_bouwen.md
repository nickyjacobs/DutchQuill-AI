# Workflow: Bouwen met Claude-features

## Wanneer gebruik je deze workflow

Altijd — bij **elk** bouwmoment dat Claude-specifiek is:

- CLAUDE.md schrijven of aanpassen
- Hooks configureren
- Subagents bouwen of aanpassen
- Skills / slash commands maken
- Tools die de Claude API aanroepen
- MCP-servers verbinden
- Agent teams opzetten
- Settings en permissions aanpassen

---

## Stap 1 – Bepaal wat je gaat bouwen

Formuleer concreet: welk feature, welke aanpassing, welk doel.

## Stap 2 – Fetch de relevante documentatie

Zoek de URL op in de tabel hieronder en fetch die pagina via WebFetch. Lees de pagina en extraheer de best practices die relevant zijn voor jouw specifieke taak.

| Feature | Documentatie-URL |
|---|---|
| Overzicht & architectuur | https://code.claude.com/docs/en/overview |
| CLAUDE.md & memory | https://code.claude.com/docs/en/memory |
| Settings & configuratie | https://code.claude.com/docs/en/settings |
| Hooks (referentie) | https://code.claude.com/docs/en/hooks |
| Hooks (quickstart) | https://code.claude.com/docs/en/hooks-guide |
| Subagents | https://code.claude.com/docs/en/sub-agents |
| Skills / slash commands | https://code.claude.com/docs/en/skills |
| MCP-servers | https://code.claude.com/docs/en/mcp |
| Agent teams | https://code.claude.com/docs/en/agent-teams |
| Permissions | https://code.claude.com/docs/en/permissions |
| Plugins | https://code.claude.com/docs/en/plugins |
| CLI-referentie | https://code.claude.com/docs/en/cli-reference |

> Twijfel je welke URL relevant is? Fetch dan eerst https://code.claude.com/docs/en/overview — daar staan links naar alle onderdelen.

### Nieuwe subagent-features (sinds upgrade maart 2026)

De sub-agents documentatie is uitgebreid. Relevante nieuwe mogelijkheden:

- **`memory` veld** in AGENT.md frontmatter (`user` / `project` / `local`): subagent bouwt persistent geheugen op over sessies heen
- **`isolation: worktree`**: subagent werkt in een geïsoleerde git-worktree (automatisch opgeruimd na afloop)
- **`background: true`**: subagent loopt asynchroon terwijl de hoofdconversatie doorgaat
- **`--agent <naam>`** CLI-vlag: hele sessie draait als een specifieke subagent (vervangt standaard systeem-prompt)
- **`skills` veld** in subagent frontmatter: injiceer skill-content direct in de context van de subagent bij opstarten
- **`/agents` commando**: interactieve interface voor aanmaken, bewerken en beheren van subagents
- **`maxTurns`**: begrenst het aantal agentic turns dat een subagent mag uitvoeren

## Stap 3 – Bouw op basis van de documentatie

Gebruik de gelezen best practices als leidraad. Wijk niet af van de officiële patronen tenzij er een expliciete reden voor is.

## Stap 4 – Controleer op afwijkingen

Vergelijk het resultaat met onze huidige `CLAUDE.md` en de betreffende workflow. Als de documentatie beter of anders is dan wat wij nu doen:
- Pas `CLAUDE.md` aan
- Update de relevante workflow
- Documenteer wat je hebt geleerd

---

## Randgevallen

**URL geeft 404 of redirect:** Probeer de alternatieve URL `https://docs.anthropic.com/en/docs/claude-code/[naam]` — die redirecten naar de huidige locatie.

**Documentatie is onduidelijk voor jouw specifieke geval:** Stel de vraag aan de gebruiker voordat je aannames maakt. Fout bouwen kost meer tijd dan even vragen.
