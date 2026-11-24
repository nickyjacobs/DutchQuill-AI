# Roadmap DutchQuill AI v2.0

Van hbo-schrijfassistent naar een Claude Code-plugin voor iedereen die tekst maakt: rapporten, mails,
social posts, procesdocumentatie, research en README's. Nederlands eerst, Engels volwaardig.

## Wat v2.0 wordt

- **Plugin met eigen marketplace:** `/plugin marketplace add nickyjacobs/DutchQuill-AI` en daarna
  `/plugin install dutchquill@dutchquill`.
- **Eén werkmap:**
  - `1-input` met notities, rapporten, beeld, bronnen en mijn-stijl;
  - `2-output` per actie, per titel, met versies v1, v2, ...
- **Eén `dutchquill.yaml`:**
  - profielen (student, zakelijk, social, techniek, of je eigen profiel);
  - controles: APA, academische stijl, taal en humaniseren, elk los aan of uit;
  - toon in vijf niveaus, formaten, templates en privacy.
- **Mails, posts en korte teksten** komen in de chat; documenten komen in de werkmap.
- **Humaniseren:**
  - stemkalibratie op je eigen teksten;
  - de AI-patronen van 2026 in NL en EN;
  - een feitencontrole: niets aan je inhoud verandert ongemerkt.
- **Templates:** APA-hbo, zakelijk en notitie meegeleverd; eigen .docx-templates toe te voegen.
- **`/dutchquill:bijwerken`:** controleert maandelijks of de bronnen van de gidsen (Scribbr NL, APA Style,
  Wikipedia "Signs of AI writing") veranderd zijn, en stelt per gids een update voor.
- **DutchQuill Studio:** een lokale, visuele wizard voor installatie en instellingen.

## Fases

| Fase | Wat | Status |
|---|---|---|
| 0 | Repo voorbereiden, branch `feature/plugin-v2` | klaar |
| 1 | Pluginskelet: manifest, `dq`-wrapper met venv, config met schema en profielen, werkmap, versies, historie, SessionStart-hook, `/dutchquill:instellen` | klaar |
| 2 | Input-pipeline: inventaris, extractie (docx, pdf, md, html, pptx, xlsx), beelden, subagent `bronnen-lezer` | |
| 3 | Gidsen: splitsen in modules, humaniseren NL en EN herschreven, `dq tells`, `dq feiten`, toonschaal, AI-bronvermelding volgens APA 2025 | |
| 4 | Kernskills herschrijven: genre, toon, modules, chat of bestand, genre-sjablonen | |
| 5 | Export: template-gestuurde exporter, `apa-hbo.docx`, pdf, md, txt en html, eerlijke metadata | |
| 6 | `/dutchquill:bijwerken` en de maandmelding | |
| 7 | DutchQuill Studio en de subagent `stem-analist` | |
| 8 | Tests, evals, README, release v2.0.0 | |
