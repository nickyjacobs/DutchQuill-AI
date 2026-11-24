---
name: schrijven
description: >-
  Schrijft nieuwe tekst in het Nederlands of Engels, in de toon en met de controles die de gebruiker koos:
  hbo-rapporten (APA), onderzoeks- en adviesrapporten, zakelijke rapporten, procesdocumenten (SOP),
  research-notities, memo's, mails, LinkedIn- en andere social posts, README's en korte teksten. Gebruikt het
  materiaal in de DutchQuill-werkmap (notities, rapporten, beelden, bronnen). Mails, posts en korte teksten komen
  in de chat, documenten als bestand met versies. Gebruik bij /dutchquill:schrijven, of als de gebruiker vraagt
  om een tekst te schrijven, op te stellen of te maken ("schrijf een mail aan", "maak een rapport van mijn
  notities", "write a LinkedIn post about", "draft a README").
argument-hint: "[wat je wilt laten schrijven]"
when_to_use: >-
  Gebruik deze skill ook als de gebruiker DutchQuill niet noemt: bij elk verzoek om een tekst voor iemand anders te
  schrijven of op te stellen, hoe kort ook (een mail of antwoord op een mail, een bericht aan een collega, een
  LinkedIn- of social post, een bio, een rapport, een README). Ook in het Engels ("write", "draft", "compose").
  Niet voor code, commit messages of uitleg in de chat zelf.
---

# Schrijven

Opdracht: $ARGUMENTS

Elk `dq`-commando draai je via Bash met dit voorvoegsel; hieronder staat het als `DQ`:

```bash
CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_ROOT}/scripts/dq"
```

## Stand

!`DQ_NIET_INSTALLEREN=1 CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_ROOT}/scripts/dq" config toon --kort 2>&1 | tail -10 || true`

## Stappen

1. **Lees de werkwijze:** `${CLAUDE_PLUGIN_ROOT}/gidsen/werkwijze/basis.md`. Gaat het om een bestand, lees dan
   ook `${CLAUDE_PLUGIN_ROOT}/gidsen/werkwijze/markdown.md`.
2. **Genre, config en uitvoer** (werkwijze 1). Is de opdracht te dun om te schrijven, stel dan in één keer de
   vragen die je echt nodig hebt (doel, lezer, kernboodschap, lengte). Bij een mail of post is de
   opdracht meestal genoeg: schrijf, en zeg wat je aannam.
3. **Gidsen lezen** (werkwijze 2): alles uit `DQ gids voor --genre <genre>`, plus het genre-sjabloon.
4. **Materiaal** (werkwijze 3), als de opdracht erom vraagt of naar de werkmap verwijst.
5. **Opzet (alleen bij documenten).** Laat een korte opzet zien: koppen met per kop één regel over de inhoud, de
   figuren met hun plek, en wat er nog ontbreekt. Wacht op akkoord of aanpassingen. Bij chat-uitvoer sla je
   deze stap over.
6. **Schrijven.**
   - In de stem van de gebruiker (stemprofiel) en de toon uit de config.
   - Volgens het genre-sjabloon en `kern.md`.
   - Gebruik alleen feiten uit het materiaal of van de gebruiker. Wat ontbreekt, markeer je als `[bron nodig]`,
     `[cijfer nodig]` of `[voorbeeld nodig]`.
   - Beelden uit het materiaal zet je op de plek waar de tekst erover gaat, met een bijschrift en een
     verwijzing in de tekst (markdown.md).
   - Bevat het materiaal cijfers die een grafiek waard zijn, maak er dan een:
     `DQ grafiek --type bar|timeline|comparison|donut --data '<json>' --output <map>/grafiek-1.png`.
     Een proces of architectuur: `DQ diagram --type flow|architecture|layers --data '<json>' --output ...`.
     `DQ grafiek --help` toont het JSON-formaat.
   - Is het document langer dan ± 1500 woorden, schrijf het dan hoofdstuk voor hoofdstuk in `bron.md`. Begin
     met een paar alinea's en voeg toe.
7. **Controles en herstellus** (werkwijze 5).
8. **Opslaan en exporteren** (werkwijze 6), of de tekst in de chat (werkwijze 7).
9. **Bij het profiel student met AI-gebruik:** bied een AI-verantwoording en de bronvermelding van de chat
   aan, volgens `ai-gebruik.md`. Vul alleen in wat de gebruiker echt heeft gedaan.

## Varianten

- **"Geef me drie versies"** (vooral posts en mails): maak versies die echt verschillen in opening, lengte of
  invalshoek, niet drie keer dezelfde tekst.
- **Antwoord op een mail:** de gebruiker plakt de mail. Beantwoord elke vraag, neem de aanspreekvorm over, en
  maak het niet langer dan de mail zelf, tenzij het onderwerp dat vraagt.
- **Een hoofdstuk of sectie** van een bestaand rapport: lees het rapport eerst (`DQ extraheer`), schrijf in
  dezelfde stijl en zet het resultaat als nieuwe versie in `schrijven/<titel>/`.

## Klaar als

- [ ] De werkwijze en alle gidsen uit `DQ gids voor` zijn gelezen.
- [ ] De controles zijn gedraaid. Het tells-niveau is laag, of het restant is uitgelegd.
- [ ] Er is geen verzonnen feit, cijfer, bron of voorbeeld in de tekst; open plekken zijn gemarkeerd.
- [ ] Chat: de tekst plus hooguit twee regels toelichting. Bestand: `bron.md`, de exports,
  `wat-is-er-veranderd.md` en een historieregel.
