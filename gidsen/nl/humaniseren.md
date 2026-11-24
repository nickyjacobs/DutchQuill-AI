---
titel: Humaniseren (Nederlands)
module: humaniseren
geldt: als controles.humaniseren aan staat
versie: 3
gecontroleerd: 2026-11-24
data: gidsen/data/tells_nl.yaml
bronnen:
  - https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
  - https://github.com/blader/humanizer
  - https://vu.nl/nl/over-de-vu/meer-over/alp-gids-ai-teksten-herkennen
  - https://www.welingelichtekringen.nl/tech/zo-herken-je-chatgpt-deze-woorden-en-zinnen-verraden-ai
  - https://onzetaal.nl/uploads/editor/Invloed.pdf
  - https://arxiv.org/html/2507.00838v2
  - https://arxiv.org/pdf/2509.10179
---

# Humaniseren (Nederlands)

Humaniseren betekent: een tekst laten klinken alsof iemand hem schreef die het onderwerp kent en iets te zeggen
heeft. Dat is meestal ook de schrijver zelf. Het resultaat is een betere tekst: preciezer, persoonlijker,
prettiger om te lezen. De inhoud verandert niet. Feiten, cijfers, namen, citaten en bronnen blijven precies
zoals ze waren.

De woordenlijsten staan in `gidsen/data/tells_nl.yaml`; `dq tells` gebruikt ze. Deze gids legt uit wat erachter
zit en wat de scripts niet kunnen zien.

## 1. Werkwijze

1. **Stem eerst.** Is er een stemprofiel (`stemprofiel.md` of `.dutchquill/stem.json` in de werkmap), lees dat
   dan voordat je één woord verandert. Wat de schrijver zelf doet, gaat voor elke regel in deze gids: gebruikt
   iemand graag gedachtestreepjes, korte zinnen of "kortom", dan blijft dat. Zonder stemprofiel volg je het genre
   en de toon (`toon.md`).
2. **Markeer.** Draai `dq tells` met het juiste genre. Lees daarna zelf: de scripts tellen woorden en patronen,
   maar zien niet of een zin iets zegt.
3. **Herschrijf** per patroon (sectie 3). Begin bij de sterkste patronen. Verander niet meer dan nodig: een
   goede zin met één zwak woord laat je staan.
4. **Controleer.**
   - Draai `dq tells --compare` (de score moet omlaag) en `dq feiten --origineel ... --nieuw ...`.
   - Er mag niets verloren gaan en niets bijkomen.
   - Kijk ook of je niet bent doorgeslagen naar het andere uiterste: alleen korte zinnen, geen enkele
     verbinding meer, overal punten.
5. **Eindversie.** Lees hem een keer als de lezer. Klinkt het als een mens die dit onderwerp kent?

## 2. Wanneer niet ingrijpen

- **Tekst van vóór december 2022**: die kan geen AI-tekst zijn. Verbeter de stijl als dat gevraagd is, maar
  noem niets een AI-patroon.
- **Informele tekst met één tell**: één "bovendien" in een mail is geen probleem.
- **Vaktermen en vaste combinaties**: "robuuste schatting" (statistiek), "essentiële aminozuren" (biologie),
  "integrale aanpak" als het de officiële naam van een beleid is.
- **Eigenaardigheden van de schrijver**: een ongewone woordkeus, een uitweiding, gemengde gevoelens, een
  zijpad. Dat zijn juist tekenen van een mens. Laat ze staan.
- **Citaten**: verander nooit iets binnen aanhalingstekens.
- **Woorden in `eigen-regels.md` onder "Juist wel"**.

## 3. De patronen

### A. Woordkeus

**Sterke tells** zijn woorden die in gewone Nederlandse tekst bijna nooit voorkomen en in AI-tekst juist veel:
cruciaal, naadloos, synergie, holistische aanpak, baanbrekend, toonaangevend, transformatief, katalysator,
"duiken in", "het landschap van", "een breed scala aan", "speelt een cruciale rol", "rijk tapijt". Een keer is
genoeg om te kijken.

**Zwakke tells** zijn gewone woorden die AI te vaak gebruikt: essentieel, robuust, aanzienlijk, inzichten,
benutten, optimaliseren, proactief, in het kader van, met betrekking tot, kortom. Eén zo'n woord zegt niets.
Drie verschillende in dezelfde alinea vormen een **cluster**, en dat klinkt wel als AI.

**Woorden wisselen per modelgeneratie.** Lijsten verouderen; daarom worden ze maandelijks bijgewerkt.

| Tijdperk | Engels (Wikipedia) | Nederlandse tegenhanger |
|---|---|---|
| GPT-4 (2023-2024) | delve, tapestry, underscore, pivotal | duiken in, rijk tapijt, onderstrepen, cruciaal |
| GPT-4o (2024-2025) | align with, enhance, showcasing, serves as | in lijn met, versterken, laten zien, fungeert als |
| GPT-5 (2025) | emphasizing, highlighting | benadrukken, belichten |
| vanaf medio 2026 | leverage, multifaceted, quietly, dependable | inzetten op, veelzijdig, stilletjes, betrouwbaar |

**"Is" vermijden** is ook een tell: "fungeert als", "dient als", "beschikt over", "pronkt met" waar gewoon
"is" of "heeft" kan.

**Vage verbanden** (sinds 2026 een van de duidelijkste tells): "in verband met", "gerelateerd aan",
"geassocieerd met". Welk verband precies? Oorzaak, gevolg, onderdeel, tegenstelling? Zeg het.

**Verborgen anglicismen**: Nederlandse woorden met Engelse zinsbouw. "Impact hebben op" (invloed hebben op),
"het maakt sense" (het klopt), "op een dagelijkse basis" (dagelijks), "aan het eind van de dag" (uiteindelijk),
"neemt plaats" (vindt plaats).

### B. Formules

| Soort | Voorbeelden | Wat te doen |
|---|---|---|
| Brede aanloop | "In de huidige digitale wereld...", "In een tijd waarin...", "Het is geen geheim dat..." | Begin met de zaak zelf |
| Tekst over de tekst | "In dit rapport wordt...", "Hieronder volgt een overzicht", "Laten we eens kijken naar" | Zeg het gewoon. In een academische inleiding mag één leeswijzer |
| Afsluiter zonder inhoud | "Kortom, het is duidelijk dat...", "De toekomst ziet er rooskleurig uit", "Ondanks deze uitdagingen..." | Eindig met de laatste echte bewering, of met een concrete volgende stap |
| Vulzin | "Het is belangrijk om op te merken dat...", "Het spreekt voor zich dat..." | Schrappen; de zin erna kan meestal alleen staan |
| Vage bron | "Uit onderzoek blijkt...", "Experts stellen...", "Men zegt..." | Noem de bron (en bij APA: met jaartal), of schrap de bewering |
| Chatbotrest | "Ik hoop dat dit helpt", "Laat het me weten", "Als taalmodel...", "Hier is een herschreven versie" | Altijd weg (behalve "laat het me weten" in een echte mail) |
| Disclaimer over bronnen (2026) | "Op basis van de beschikbare informatie...", "Hoewel specifieke gegevens beperkt zijn..." | Weg; ontbreekt er iets, zeg dan concreet wat |
| Bewerkingsverslag (2026) | "Alle informatie is behouden", "De betekenis is intact gebleven" | Weg: dat hoort niet in de tekst |

### C. Constructies

- **Niet X, maar Y** ("Het is niet alleen een tool, maar een manier van werken"). Sterkste structurele tell
  sinds 2024. Zeg wat het wél is. Eén keer in een lange tekst kan; drie keer is een patroon.
- **Retorische aanloop** ("Het resultaat? Een snellere app."). Schrijf de zin gewoon uit.
- **Drieslag**: alles in drieën ("snel, veilig en betrouwbaar"). Varieer met twee, vier of één, en
  alleen als het er ook echt zoveel zijn.
- **Opgeblazen belang**: "markeert een keerpunt", "van onschatbare waarde", "heeft het debat blijvend gevormd".
  Wat gebeurde er concreet?
- **Oppervlakkige bijzin aan het eind**: "..., waarmee het belang van samenwerking wordt onderstreept". Die
  bijzin voegt een oordeel toe zonder inhoud. Schrappen, of er een eigen zin met bewijs van maken.
- **Een gezegde dat diep klinkt**: "Uiteindelijk draait alles om mensen." Klinkt wijs, zegt niets.
- **Herhaalde begins**: drie zinnen in een alinea met hetzelfde eerste woord, of alinea's die allemaal met
  "Daarnaast" beginnen.
- **Verbindingswoorden als zinsopener**: bovendien, daarnaast, echter, tevens. Meer dan een kwart van de zinnen
  is te veel. Vaak kan het verband zonder signaalwoord, of in het midden van de zin ("Dat bleek echter...").
- **De kop herhaald**: kop "Resultaten van de enquête", eerste zin "De resultaten van de enquête laten zien...".

### D. Ritme

- **Te gelijk**: alle zinnen 15 tot 20 woorden, alle alinea's vier zinnen. Mensen wisselen af.
- **Overgecorrigeerd** (de nieuwe tell sinds 2026): nieuwere modellen en humanizer-tools hakken alles in korte
  zinnen en vervangen elk streepje door een punt. Resultaat: "Dit werkt. Het is snel. Het team is blij." Dat
  klinkt net zo kunstmatig. Verbind zinnen weer waar de gedachte doorloopt.
- **Weinig woordvariatie**: hetzelfde zelfstandig naamwoord vijf keer in een alinea. Gebruik een verwijswoord
  of formuleer anders. Ga niet krampachtig synoniemen wisselen ("de auto ... het voertuig ... de wagen"); ook
  dat is een tell.

### E. Opmaak

- **Gedachtestreepje** als leesteken: tot 2025 een sterke tell, nu zwak. Vervang het als de schrijver het zelf
  niet gebruikt.
- **Vet als versiering** midden in een zin.
- **Emoji** voor koppen of opsommingen, vooral in zakelijke tekst.
- **Koppen in Engelse title case** ("De Rol Van AI In Het Onderwijs"). Nederlands: alleen de eerste letter.
- **Opsommingen in plaats van een redenering**: als de punten op elkaar voortbouwen, schrijf dan een alinea.
- **LinkedIn**: elke zin een eigen alinea ("broetry"), emoji-opsommingen, meer dan drie hashtags, en de
  formule "haak, dit is wat ik leerde, drie punten, vraag aan het eind".

### F. De verkeerde lezer

- Uitleggen wat de lezer al weet ("E-mail is een belangrijk communicatiemiddel").
- Schrijven over het document in plaats van over het onderwerp.
- Een conclusie die alles nog een keer opsomt.

## 4. Wat tekst menselijk maakt

Patronen weghalen is de helft. Dit voegt toe:

- **Specifiek**: namen, getallen, data, plaatsen. Maar alleen uit het materiaal of van de gebruiker. **Verzin
  nooit een voorbeeld, anekdote of cijfer.** Ontbreekt er iets concreets, vraag het dan of zet `[voorbeeld nodig]`.
- **Een standpunt**: een mens kiest. "Optie B is beter, omdat..." in plaats van "Beide opties hebben voor- en
  nadelen." Twijfel alleen waar echt twijfel is.
- **Gewone werkwoorden**: is, heeft, doet, maakt, zegt. "Er is" en "er zijn" mogen.
- **Verleden tijd en een verloop** waar het genre het toelaat: wat er gebeurde, in welke volgorde. AI-tekst
  is vaak tijdloos en algemeen.
- **Wat onregelmatigheid**: een zin die wat langer doorloopt, een korte reactie, een bijzin tussen haakjes.
  Een perfect gladde tekst valt juist op.

## 5. Per genre

| Genre | Let vooral op | Mag gewoon |
|---|---|---|
| Hbo-rapport | vage bronnen, formules, opgeblazen belang, aankondigingen | passief in de methode, signaalwoorden met mate, een leeswijzer in de inleiding |
| Zakelijk rapport, SOP | aanloop, vulzinnen, vage verbanden, opsommingen zonder redenering | genummerde stappen, vaktermen, kortere zinnen in procedures |
| Mail | chatbotresten, aanloop, te formeel voor de lezer | "laat het me weten", een korte groet, een vraag |
| LinkedIn en social | formules, broetry, emoji-opsommingen, hashtags, retorische aanloop | ik-vorm, een mening, een korte zin voor nadruk, één emoji |
| README | marketingtaal ("naadloos", "krachtig"), tekst over de tekst | korte zinnen, codeblokken, opsommingen voor features |

## 6. Score

`dq tells` geeft punten per 1000 woorden en een niveau:

| Genre | Laag | Gemiddeld | Hoog |
|---|---|---|---|
| Rapport, SOP, README, memo (streng) | onder 4 | 4 tot 9 | 9 of meer |
| Mail, LinkedIn, social, kort (los) | onder 6 | 6 tot 12 | 12 of meer |

Doel na humaniseren: laag. Een gemiddelde score met alleen zwakke tells is vaak prima. Belangrijker dan het
getal: zijn de sterke tells weg, is er geen cluster meer, en klopt de feitencontrole?

## 7. Leesbaarheid en humaniseren

Een makkelijke tekst is niet automatisch menselijk, en een moeilijke tekst niet automatisch AI. Flesch-Douma
(`dq leesbaarheid`) is een hulpmiddel. Een hbo-rapport zit meestal tussen 30 en 50, een mail of post hoger.
Verlaag de leesbaarheid nooit om "academischer" te klinken.

## 8. Voor en na

**Voor (AI):**

> In de huidige digitale wereld speelt kunstmatige intelligentie een cruciale rol in het onderwijs. Het is
> niet alleen een hulpmiddel, maar een transformatieve kracht. Bovendien biedt AI een breed scala aan
> mogelijkheden voor gepersonaliseerd leren. Kortom, de toekomst ziet er rooskleurig uit.

**Na (zelfde inhoud, met een concreet gegeven uit het materiaal van de gebruiker):**

> Sinds januari mogen leerlingen op onze school AI gebruiken, als ze opschrijven waarvoor. De meesten
> gebruiken het om bronnen te ordenen of om uitleg te krijgen bij een begrip dat ze niet snappen. Dat werkt
> vooral goed voor leerlingen die in de les niet durven te vragen.

Wat er gebeurde: de aanloop is weg, net als de niet-X-maar-Y en de afsluiter. De sterke tells (cruciaal,
transformatief, breed scala) zijn vervangen door wat er concreet gebeurt. Het gegeven over januari kwam uit de
notities van de gebruiker; zonder dat gegeven had de versie "[sinds wanneer?]" gevraagd.

## 9. Over AI-detectoren

- **Turnitin** herkent sinds 6 oktober 2026 ook Nederlandse tekst.
- **Detectoren meten** woordkeus, voorspelbaarheid en ritme, dus grotendeels dezelfde patronen als hierboven.
- **Onafhankelijk onderzoek** laat zien dat ze vaak fout zitten, juist ook bij mensen die in hun tweede taal
  schrijven.
- **DutchQuill richt zich op de tekst**, niet op een detectorscore. Een tekst die specifiek is en in de stem
  van de schrijver staat, is gewoon een goede tekst.

Is AI gebruikt bij een studieopdracht, kijk dan in `ai-gebruik.md` hoe je dat verantwoordt.
