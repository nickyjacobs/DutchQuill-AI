---
name: reviewen
description: >-
  Reviewt een tekst zonder iets te veranderen: taal en spelling, AI-patronen, structuur en opbouw, toon voor de
  lezer, en (als die aan staan) APA en academische stijl, plus de beoordelingscriteria of inlevereisen van een
  vak als die in de werkmap staan. Levert een reviewrapport met bevindingen per regel, prioriteiten en de vijf
  belangrijkste acties; korte teksten (mail, post) krijgen hun review in de chat. Gebruik bij
  /dutchquill:reviewen, of als de gebruiker vraagt een tekst na te kijken, te beoordelen of feedback te geven
  ("kijk mijn rapport na", "review this draft", "is deze mail goed zo", "geef feedback op hoofdstuk 3").
argument-hint: "[tekst of pad] [waar je vooral op wilt letten]"
when_to_use: >-
  Gebruik deze skill ook als de gebruiker DutchQuill niet noemt: bij elke vraag om feedback op of een check van
  een eigen tekst (rapport, hoofdstuk, mail, post), zonder dat de tekst herschreven hoeft te worden.
---

# Reviewen

Opdracht: $ARGUMENTS

Je verandert niets aan de tekst. Je levert een review.

Elk `dq`-commando draai je via Bash met dit voorvoegsel; hieronder staat het als `DQ`:

```bash
CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_ROOT}/scripts/dq"
```

## Stand

!`DQ_NIET_INSTALLEREN=1 CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_ROOT}/scripts/dq" config toon --kort 2>&1 | tail -10 || true`

## Stappen

1. **Lees de werkwijze:** `${CLAUDE_PLUGIN_ROOT}/gidsen/werkwijze/basis.md`.
2. **Tekst en genre.** Lees de tekst: geplakt, een pad, of uit de werkmap. Een .docx of .pdf lees je via
   `DQ extraheer`. Bij een .docx ook de opmaak: kijk of de beelden (in de map `-beelden`) en de koppen kloppen.
   Bepaal het genre en laad de config: `DQ gids voor --genre <genre>`. Een review gaat over de modules die aan
   staan. Vraagt de gebruiker expliciet om iets anders ("let ook op APA"), doe dat dan ook.
3. **Gidsen lezen** (werkwijze 2), plus bij het studentprofiel de criteria van het vak:
   - `<werkmap>/templates/vakken/<VAKCODE>/quick-scan.md` (inlevereisen);
   - `beoordelingscriteria.md` in diezelfde map (rubric).

   De vakcode komt uit de tekst (titelpagina) of uit de vraag. Voorbeelden van het formaat staan in
   `${CLAUDE_PLUGIN_ROOT}/templates/student/`.
4. **Scripts** (de subagent `dutchquill:tekst-analist` kan ze voor je draaien en samenvatten):
   - `DQ tells --input <tekst> --genre <genre> --json`
   - `DQ leesbaarheid --input <tekst>` (Nederlands)
   - `DQ apa-check --input <tekst>` als APA aan staat
   - `DQ taalcheck --input <tekst> --lang nl` alleen als `privacy.languagetool` aan staat
5. **Zelf lezen.** De scripts vangen niet alles. Loop deze domeinen na:

   | Domein | Waarop | Geldt |
   |---|---|---|
   | Taal | spelling, d/t, zinsbouw, interpunctie, consistentie (je/u, schrijfwijze van termen) | altijd |
   | Helderheid en structuur | hoofdboodschap vooraan, rode draad, alinea's met één gedachte, koppen die kloppen, aansluiting vraag en conclusie | altijd |
   | Toon en lezer | past de toon bij lezer en genre (`toon.md`), wordt er uitgelegd wat de lezer al weet | altijd |
   | AI-patronen | volgens `humaniseren.md`; sterke tells, clusters, formules, ritme | als humaniseren aan staat |
   | APA | bronvermelding in de tekst en in de lijst, titelpagina, koppen, tabellen en figuren, bijlagen, AI-verantwoording | als apa aan staat |
   | Academische stijl | spreektaal, werkwoordstijden, ik-vorm, onderbouwing | als academische_stijl aan staat |
   | Vakcriteria | per criterium uit de rubric: voldoet de tekst, en waar blijkt dat uit | als er een rubric is |

6. **Het reviewrapport.** Elke bevinding krijgt:
   - een plek (hoofdstuk, alinea of regel, met een citaat van hooguit tien woorden);
   - wat er mis is;
   - een voorstel;
   - een prioriteit: **moet** (fout of eis), **beter** (duidelijke winst), **kan** (smaak).

   Geef per domein een kort oordeel in één zin, en eindig met de vijf acties die het meeste opleveren.
   Schrijf het rapport in de taal van de tekst.
7. **Uitvoer.**
   - Mail, post of korte tekst: de review in de chat. Hooguit tien bevindingen, de belangrijkste eerst.
   - Document:
     1. `DQ versie volgende --actie reviewen --titel "<titel van de tekst>"`.
     2. Schrijf het rapport als `<map>/bron.md`, met als titel "Review: <titel>".
     3. `DQ export --bron <map>/bron.md --naam "Review <titel>" --genre memo` (de reviewtemplate komt uit het
        genre memo).
     4. In de chat: het pad, het oordeel in drie zinnen en de vijf acties.
   - Historie: `DQ historie log --actie reviewen ...`.

## Klaar als

- [ ] Er is niets aan de tekst zelf veranderd.
- [ ] Elke bevinding heeft een plek, een voorstel en een prioriteit.
- [ ] Er zijn alleen domeinen beoordeeld die aan staan of waar de gebruiker om vroeg; de rubric is gebruikt als
      die er is.
- [ ] De vijf belangrijkste acties staan in de chat.
