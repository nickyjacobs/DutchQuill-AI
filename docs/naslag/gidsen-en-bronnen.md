# Gidsen en bronnen

De regels die DutchQuill volgt, staan in gidsen in de map `gidsen/`. Claude leest alleen de gidsen die bij een
opdracht horen (`dq gids voor`), zodat een mail niet door de APA-regels hoeft.

## De gidsen

| Gids | Wanneer | Inhoud |
|---|---|---|
| `nl/kern.md` | altijd (Nederlandse tekst) | Basisregels voor goed Nederlands: actief, concreet, getallen, zinslengte |
| `nl/taal.md` | controle taal (Nederlands) | Spelling, d/t, hoofdletters, komma's, samenstellingen |
| `nl/academische-stijl.md` | controle academische stijl | Formeel, onderbouwd, werkwoordstijd per hoofdstuk |
| `nl/apa.md` | controle APA | APA 7 volgens Scribbr NL |
| `nl/ai-gebruik.md` | controle APA | AI citeren (formaat van september 2025) en de AI-verantwoording |
| `nl/humaniseren.md`, `en/humanize.md` | controle humaniseren | AI-patronen en hoe je ze oplost |
| `en/style.md` | altijd (Engelse tekst) | Basisregels voor goed Engels, in plaats van `nl/kern.md` |
| `toon.md` | altijd | Wat elk toonniveau betekent |
| `data/tells_nl.yaml`, `data/tells_en.yaml` | `dq tells` | De woordenlijsten en formules achter de AI-patronen |
| `werkwijze/` | altijd | De gedeelde werkwijze van de skills en de Markdown-afspraken voor de export |

Elke gids heeft bovenaan `bronnen:` (de URL's waar hij op steunt), `gecontroleerd:` en `versie:`. De gidsen bevatten
eigen geformuleerde regels met een bronverwijzing, geen gekopieerde tekst.

## De bronnen

- **Scribbr NL** voor APA 7 en taal, vergeleken via de sitemap (één verzoek, geen pagina's crawlen).
- **APA Style** voor AI citeren. Die site weigert geautomatiseerde verzoeken; Claude zoekt daar zelf naar nieuwe
  berichten.
- **[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)**, vergeleken op
  revisienummer.
- **[blader/humanizer](https://github.com/blader/humanizer)** (MIT), vergeleken op de laatste release.

De lijst staat in `gidsen/bronnen.yaml`.

## Bijwerken

Eén keer per maand meldt DutchQuill bij de start van een sessie dat de gidsen weer gecontroleerd kunnen worden.
Met `/dutchquill:bijwerken` (of de knop "Nu controleren" in de Studio):

1. `dq bronnen check` vergelijkt de bronnen met de vorige keer.
2. Per gewijzigde bron leest Claude de pagina en legt die naast de gids.
3. Je krijgt per gids een voorstel met een diff. Er wordt pas iets geschreven na jouw akkoord.
4. Bijgewerkte gidsen komen in de datamap van de plugin en gaan voor de meegeleverde, tot een nieuwere
   plugin-versie een nieuwere gids meebrengt.

Zonder wijzigingen wordt alleen de datum van de laatste controle bijgewerkt, en is de herinnering weer voor een
maand weg.
