---
name: herschrijven
description: >-
  Herschrijft bestaande tekst in het Nederlands of Engels zonder de inhoud te veranderen: verbeteren, inkorten,
  formeler of luchtiger maken, een andere toon, vertalen tussen Nederlands en Engels, parafraseren, of een eerdere
  versie bijwerken. Werkt op geplakte tekst, een bestand (.docx, .pdf, .md) of een rapport in de
  DutchQuill-werkmap, en controleert achteraf dat er geen feit, getal, citaat of bron verloren ging. Gebruik bij
  /dutchquill:herschrijven, of als de gebruiker vraagt een tekst te herschrijven, verbeteren, korter of
  formeler te maken of te vertalen ("herschrijf dit", "maak dit zakelijker", "rewrite this", "make this
  shorter", "vertaal naar het Engels").
argument-hint: "[tekst, pad of titel] [wat er anders moet]"
when_to_use: >-
  Gebruik deze skill ook als de gebruiker DutchQuill niet noemt: bij elke vraag een bestaande tekst te verbeteren,
  in te korten, anders te laten klinken of te vertalen tussen Nederlands en Engels.
---

# Herschrijven

Opdracht: $ARGUMENTS

Elk `dq`-commando draai je via Bash met dit voorvoegsel; hieronder staat het als `DQ`:

```bash
CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_ROOT}/scripts/dq"
```

## Stand

!`DQ_NIET_INSTALLEREN=1 CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_ROOT}/scripts/dq" config toon --kort 2>&1 | tail -10 || true`

## Stappen

1. **Lees de werkwijze:** `${CLAUDE_PLUGIN_ROOT}/gidsen/werkwijze/basis.md` (en `markdown.md` bij een bestand).
2. **Welke tekst?**
   - geplakte tekst;
   - een pad (lees een .docx of .pdf via `DQ extraheer`);
   - een bestand in `1-input/rapporten`;
   - een eerdere output: `DQ versie laatste --actie schrijven|herschrijven --titel "<titel>"`.

   Bewaar het origineel als `origineel.md` in de werkmap (`.dutchquill/tmp/`, of de nieuwe versiemap bij
   bestandsuitvoer). Het originele bestand van de gebruiker raak je nooit aan.
3. **Wat moet er anders?** Bepaal de modus. Meerdere tegelijk kan.

   | Modus | Wat je doet |
   |---|---|
   | verbeteren (standaard) | taal, helderheid, structuur van zinnen en alinea's; de opbouw blijft |
   | korter | schrappen wat niets toevoegt; doel-lengte van de gebruiker, anders ± 30% korter |
   | toon | naar het gevraagde niveau (`toon.md`), inclusief je/u |
   | formaliseren | spreektaal eruit, academisch of zakelijk (zie `academische-stijl.md` bij het studentprofiel) |
   | vertalen | naar NL of EN, vrij vertaald in plaats van letterlijk; vaktermen, namen en citaten blijven |
   | parafraseren | voor een bron die je wilt verwerken: eigen woorden en eigen zinsbouw, met de bronvermelding |
   | humaniseren | de gids `humaniseren.md` volgen (of gebruik `/dutchquill:humaniseren`) |

   Het genre bepaalt de config: `DQ gids voor --genre <genre>`.
4. **Gidsen lezen** (werkwijze 2).
5. **Analyse van het origineel:** `DQ tells --input <origineel> --genre <genre>`. Bij een document ook
   `DQ apa-check` als APA aan staat. Noteer de grootste problemen, het liefst niet meer dan vijf.
6. **Herschrijven.**
   - De opbouw (koppen, volgorde, opsommingen) blijft, tenzij de gebruiker anders vraagt of de opbouw het
     probleem is. Zeg het als je de opbouw verandert.
   - Verander niets binnen citaten.
   - Bronvermeldingen, getallen en namen blijven precies.
   - In de stem van de gebruiker. Komt de tekst van de gebruiker zelf, dan bewaar je ook de eigenaardigheden
     van de schrijver; zie `humaniseren.md`, sectie 2.
7. **Controles** (werkwijze 5), verplicht:
   - `DQ feiten --origineel <origineel> --nieuw <concept>`: geeft dit iets terug, controleer dan elk punt. Een
     verloren getal of bron zet je terug. Een naam die alleen anders gespeld is, mag.
   - `DQ tells --compare <origineel> <concept> --genre <genre>`: de score moet omlaag of gelijk blijven.
   - Bij documenten: `DQ diff --original <origineel> --rewritten <concept> --summary`.
8. **Opslaan en exporteren** (werkwijze 6). De nieuwe versie gaat in `2-output/herschrijven/<titel>/vN/`.
   In `wat-is-er-veranderd.md` komen de modus, de belangrijkste wijzigingen, de tells-score voor en na, en de
   uitkomst van de feitencontrole. Bij chat-uitvoer: de nieuwe tekst plus één regel over wat je veranderde.

## Klaar als

- [ ] De feitencontrole is gedraaid en elk verschil is verklaard of hersteld.
- [ ] De tells-score is niet gestegen.
- [ ] De opbouw is behouden, of de wijziging is gemeld.
- [ ] Het origineel van de gebruiker is onaangeroerd.
