# Humanize NL Gids — Nederlandse AI-Patronen Vermijden

Referentiegids voor het detecteren en vermijden van AI-schrijfpatronen in Nederlandse teksten.
Gebaseerd op drie Humanizer-repos (blader/humanizer, brandonwise/humanizer, openclaw/skills ai-humanizer, alle MIT-licentie),
Nederlandse bronnen (aikundig.nl, frankwatching.com, Scribbr NL, Mensify.nl, Smals Research) en
webonderzoek naar Nederlandstalige AI-detectiepatronen. Volledig aangepast voor Nederlands taalgebruik en academische schrijfstijl.
20 detectiecategorieën — geïmplementeerd in `tools/humanizer_nl.py`.

---

## Waarom humaniseren?

AI-gegenereerde tekst is herkenbaar. Niet omdat AI per definitie slecht schrijft, maar omdat
het dezelfde woorden, dezelfde zinsstructuren en dezelfde patronen herhaalt. Docenten en
AI-detectietools pikken dit op.

Menselijk schrijven varieert. Het heeft ritme. Het wisselt korte en lange zinnen af. Het mist
de strakke uniformiteit die AI automatisch produceert. En het heeft specifieke details — geen
vage algemeenheden.

Drie signalen worden gebruikt om AI-tekst te detecteren:
1. **Woordherkenning** — AI-typische woorden en uitdrukkingen
2. **Patronen** — formulaïsche structuren en AI-communicatievormen
3. **Statistieken** — zinslengtevariatie, woordenschatvariatie, n-gram repetitie

---

## Categorie 1: Nederlandse AI-Woordenlijst

De volgende woorden komen statistisch buitenproportioneel voor in Nederlandse AI-teksten.
Georganiseerd in drie niveaus (gebaseerd op Humanizer's tier-systeem, vertaald naar NL).

### Niveau 1 — Directe Verraaders
Vrijwel zeker AI als aanwezig. **Altijd vervangen.**

| AI-woord/uitdrukking | Probleem | Betere alternatieven |
|----------------------|----------|---------------------|
| cruciaal | Superlatiefwoord, overgebruikt | belangrijk, bepalend, doorslaggevend, van groot belang |
| essentieel | Idem | noodzakelijk, onmisbaar, vereist |
| speelt een cruciale/centrale/sleutelrol | AI-cliché | [beschrijf de specifieke functie] |
| naadloos | Vage kwalificering | [beschrijf waarom het goed werkt] |
| synergie / synergiën | Managementjargon | samenwerking, combinatie, wisselwerking |
| verdiepen in | Anglicisme ("delve into") | onderzoeken, bestuderen, analyseren |
| het landschap van | Vage omschrijving ("the landscape of") | [wees specifiek: de sector, het veld, de markt] |
| het speelveld | Idem | [wees specifiek] |
| holistische aanpak | Vaag managementbegrip | [beschrijf wat er precies wordt meegenomen] |
| baanbrekend | Overdreven kwalificering | nieuw, vernieuwend, eerste in zijn soort |
| grondig | Vaag intensiveringswoord | [beschrijf wat er grondig werd gedaan] |
| toonaangevend | AI-superlatiefwoord | vooraanstaand, groot, invloedrijk |
| optimaliseren | Managementjargon | verbeteren, efficiënter maken, aanpassen |
| benutten | Anglicisme ("leverage") | gebruiken, inzetten, toepassen |
| ontsluiten | Anglicisme ("unlock") | openen, beschikbaar maken, vrijgeven |
| biedt kansen en uitdagingen | Nietszeggend | [noem de specifieke kansen en problemen] |
| een breed scala aan | Vage kwantificering | veel, diverse, verschillende — of geef voorbeelden |
| in toenemende mate | Vage tijdsindicator | steeds meer, [geef data of datum] |
| aanzienlijk | Vage kwantificering | [geef een getal of percentage] |
| inzichten | Vaag zelfstandig naamwoord | bevindingen, conclusies, resultaten, kennis |
| duiken / duik in | Letterlijke vertaling "deep dive" | analyseer, onderzoek, bekijk nader |
| scala | Overgebruikt voor "reeks/aantal" | veel, diverse, [geef concrete voorbeelden] |
| betekenisvol | Overdreven woordkeuze | zinvol, nuttig, relevant |
| diepgaand | Onnatuurlijk AI-anglicisme in NL | uitgebreid, grondig [maar beschrijf ook wát] |
| transformatief | Anglicisme, te vaag | veranderend, ingrijpend, structureel anders |
| katalysator | Anglicisme ("catalyst") | aanjager, trigger, directe oorzaak |
| speerpunt | Beleidsjargon | prioriteit, focus, hoofddoel |
| robuust | Vage kwalificering | stabiel, betrouwbaar, [beschrijf waarom] |
| faciliteert | Omslachtig ("facilitates") | maakt mogelijk, helpt, zorgt voor |
| demonstreert | AI-copulavervanger | laat zien, toont, bewijst |
| onderstreept | Vage intensivering ("underscores") | bevestigt, toont aan, maakt duidelijk |
| weerspiegelt | Vaag verbindingswoord ("reflects") | toont, is te zien in, volgt uit |
| stroomlijnen | Managementjargon ("streamline") | vereenvoudigen, efficiënter maken, samenvoegen |
| duiken in | Letterlijke vertaling "delve into" — sterk anglicisme | analyseer, onderzoek, bekijk nader |
| fosteren | Anglicisme ("to foster") — bestaat niet organisch in NL | bevorderen, stimuleren, aanmoedigen |
| testament aan | Letterlijke vertaling "a testament to" — klinkt on-Nederlands | bewijs van, aanwijzing voor |
| impact hebben op | Anglicisme ("to have an impact on") | invloed hebben op, effect hebben op, gevolgen hebben voor |
| uiteraard (op zinsbegin) | Chatbot-opener — impliceert dat lezer het al weet | verwijder of herschrijf de zin zonder dit woord |

### Niveau 2 — Verdacht bij Hoge Dichtheid
Individueel acceptabel, maar alarmerend als ze clusteren. Beperk gebruik.

| AI-woord/uitdrukking | Probleem | Betere alternatieven |
|----------------------|----------|---------------------|
| bovendien | Overgebruikt connectief | ook, daarnaast, verder, en |
| tevens | Formeel en AI-achtig | ook, eveneens [spaarzaam] |
| echter | Contrasttransitie die AI overgebruikt | maar, toch, desondanks |
| desalniettemin | Pompeus | toch, maar, ondanks dit |
| voorts | Verouderd/AI-achtig | verder, ook, aanvullend |
| derhalve | Archaïsch | dus, daarom, om die reden |
| aldus | Verouderd | zo, op die manier — of weglaten |
| significant | Anglicisme in NL-teksten | betekenisvol, opvallend, noemenswaardig |
| dynamisch | Modebegrip | [beschrijf de eigenschap specifiek] |
| innovatief / innovatie | AI-modebegrip | nieuw, vernieuwend, [beschrijf wat nieuw is] |
| complexiteit | Nietszeggend | [beschrijf wat er complex is] |
| uitdaging | AI-omschrijving voor "probleem" | probleem, moeilijkheid, knelpunt, obstakel |
| in het kader van | Omslachtig | voor, binnen, bij |
| met betrekking tot | Omslachtig | over, voor, bij |
| ten aanzien van | Omslachtig | over, voor, bij |
| duidelijk | Vage stelligheid | [geef bewijs in plaats van dit woord] |
| evident | Idem | [geef bewijs] |
| genuanceerd | Wordt opvulwoord — zeg wàt genuanceerd is | [beschrijf de nuance concreet] |
| uitgebreid | Vage kwalificering ("comprehensive") | [beschrijf de reikwijdte specifiek] |
| proactief | Modebegrip | [beschrijf de concrete actie] |
| integraal | Containerbegrip | volledig, als geheel, [beschrijf wat erbij hoort] |
| zodoende | Archaïsch transitiewoord | zo, daardoor, daarmee |
| passie / passievol | Overgebruikt in AI-teksten | [beschrijf gedrag of motivatie concreet] |
| verheugd | Te formeel, AI-kenmerk | blij, tevreden, positief over |
| in veel gevallen | Vage kwantificeerder — ChatGPT-signaal | [geef een concrete context of percentage] |
| in sommige gevallen | Idem | in bepaalde situaties [omschrijf welke] |
| in zekere mate | Vage graadaanduiding | [beschrijf precies in welke mate] |
| biedt / bieden | Hoge dichtheid is ChatGPT-signaal | [kies specifieker: geeft, levert, maakt mogelijk] |

### Niveau 3 — Context-Afhankelijk
Acceptabel in kleine hoeveelheden. Verdacht als dichtheid boven 3% van de tekst uitkomt.

| AI-woord | Waarschuwing |
|----------|-------------|
| belangrijk | Wordt snel een opvulwoord — zeg waarom het belangrijk is |
| effectief | Zeg waarvoor of waarom |
| uniek | Leg uit wat er uniek aan is |
| waardevol | Vage loftuiting — geef concrete waarde |
| opmerkelijk | Zeg wat er opmerkelijk is |
| substantieel | Geef een maat |
| uiteraard | Impliceert dat de lezer het al weet — weglaten of toelichten |
| vanzelfsprekend | Idem |

---

## Categorie 2: Formulaïsche Structuren

AI gebruikt herkenbare opbouwpatronen. Vermijd deze in academische teksten.

### Verboden openingszinnen en -patronen

**Type 1 — Brede aanloop:**
- "In de huidige samenleving..."
- "Tegenwoordig is het duidelijk dat..."
- "In de afgelopen jaren is er veel veranderd op het gebied van..."
- "Het onderwerp van dit rapport is actueler dan ooit..."
- "In een wereld waar..."
- "In het huidige tijdperk..."
- "Het is belangrijker dan ooit..."
- "In de hedendaagse maatschappij..."
- "In een steeds veranderende wereld/samenleving/context..."
- "In deze tijd van [onderwerp]..."

**Type 2 — Aankondiging van wat je gaat doen:**
- "In dit rapport wordt onderzocht..."
- "Dit rapport richt zich op..."
- "Het doel van dit rapport is..."
- "In dit hoofdstuk zal ik bespreken..."
- "Hieronder volgt een overzicht van..."
- "Allereerst wordt ingegaan op..."

**Type 2b — Contextuele frames:**
Formuleringen die een zin inleiden als algemeen kader, zonder specifieke inhoud toe te voegen.
- "Tegen deze achtergrond..."
- "Vanuit een [bijvoeglijk naamwoord] perspectief..."
- "In brede zin kan worden gesteld dat..."
- "In het algemeen kan worden gesteld dat..."
- "In algemene zin wordt/kan worden..."

**Type 3 — Samenvatting van wat je net hebt gezegd:**
- "Kortom, het is duidelijk dat..."
- "Al met al kan gesteld worden dat..."
- "Zoals eerder vermeld..."
- "Op basis van het voorgaande kan geconcludeerd worden dat..."
- "Bovenstaande analyse toont aan dat..."
- "Aan de hand van het bovenstaande..."
- "Samenvattend kan worden gesteld dat..."
- "Vanuit een algemeen perspectief lijkt/is/kan..."
- "Het mag duidelijk zijn dat..."
- "Op basis van de geraadpleegde bronnen/de literatuur kan worden gesteld/geconcludeerd..."

**Waarom zijn dit problemen?**
Ze zeggen niets. Ze kondigen aan in plaats van te doen. Begin direct met de inhoud.

### Verdachte constructies (gebruik bewust, niet automatisch)
- Driedelige opsommingen als generiek vangnet: "X is van belang voor A, B en C" — vermoedelijk AI als de drie elementen ook voor alles anders zouden gelden
- "Enerzijds... anderzijds..." — niet verboden, maar AI gebruikt het altijd; gebruik het alleen als je er ook echt een standpunt aan koppelt
- Elke alinea begint met hetzelfde woord: Bovendien... / Tevens... / Daarnaast... — varieer

---

### Em Dash (—)

De em dash (—) is een Engels leesteken dat in Nederlandse teksten niet thuishoort.
Toch gebruiken AI-modellen het consequent, omdat ze voornamelijk op Engelstalige data zijn getraind.

**Regel:** Gebruik nooit een em dash in een Nederlands rapport.
- Vervang `—` door een komma, punt of gedachtestreepje met spaties (` - `)
- Meer dan één em dash in een tekst is een directe AI-indicator

**Voorbeelden:**
- Slecht: `Werkstress — een groeiend probleem — heeft gevolgen voor studenten.`
- Goed: `Werkstress, een groeiend probleem, heeft gevolgen voor studenten.`
- Goed: `Werkstress is een groeiend probleem. Het heeft gevolgen voor studenten.`

---

### Vage Bronvermelding

AI claimt feiten zonder bronnen te noemen. Dit is zowel een AI-patroon als een APA-overtreding.

**Verboden formuleringen (zonder citatie):**
- "Uit onderzoek blijkt dat..."
- "Experts stellen dat..."
- "Studies tonen aan dat..."
- "Het is algemeen bekend dat..."
- "Wetenschappers zijn het erover eens dat..."
- "Onderzoek wijst uit dat..."
- "Eerdere studies laten zien dat..."
- "In de literatuur wordt gesteld/beschreven/aangegeven dat..."
- "Studies laten zien dat..."
- "Onderzoeken tonen aan dat..."
- "Er is aangetoond/bewezen dat..." (zonder citatie)
- "Men stelt/weet/zegt dat..."
- "Het is aangetoond/bewezen dat..."
- "Eerder onderzoek laat zien/toont aan dat..."
- "Uit diverse/verschillende/meerdere studies blijkt..."

**Regel:** Elke feitelijke claim heeft een bronvermelding. Geen bron? Geen claim.

---

### Generieke Conclusies

AI eindigt alinea's en secties met vage afsluiters. Ze klinken concluderend maar zeggen niets.

**Verboden afsluiters:**
- "De toekomst ziet er rooskleurig uit."
- "De mogelijkheden zijn eindeloos."
- "Naar een hoger niveau tillen."
- "Er liggen grote kansen."
- "Dit vraagt om verdere aandacht." (zonder te specificeren welke)
- "Dit is slechts het begin."

**Regel:** Eindig met een concrete bevinding, cijfer of vraag — niet met een platitude.

---

## Categorie 3: Statistische Indicatoren

*Gebaseerd op Humanizer's burstiness, type-token ratio en n-gram analyse — taalkundig universeel, dus direct toepasbaar op Nederlands.*

### Zinslengtevariatie (Burstiness)

AI schrijft uniform. Mensen schrijven met variatie.

**AI-patroon (slecht):**
> Het klimaat verandert door menselijke activiteiten. De uitstoot van CO2 neemt toe. Dit heeft gevolgen voor de temperatuur. De zeespiegel stijgt als gevolg hiervan.

Alle zinnen: 8–12 woorden. Monotoon ritme.

**Menselijk patroon (goed):**
> Het klimaat verandert. Dat is geen nieuws meer — de wetenschap is er al decennia duidelijk over. Maar wat wél nieuw is, is de snelheid: CO2-uitstoot is de afgelopen twintig jaar verdubbeld, en de Arctische ijskappen smelten sneller dan zelfs de meest pessimistische modellen voorspelden.

Zinslengte: 3 woorden / 17 woorden / 29 woorden — hoge variatie.

**Richtlijn:**
- Kort (< 10 woorden): bewust inzetten voor nadruk of pauze
- Middellang (10–20 woorden): meest voorkomend
- Lang (20–35 woorden): voor complexe gedachten met subclaims
- **Na een lange zin: korte zin. Na een korte zin: middellange of lange.** Nooit vijf zinnen op rij van gelijke lengte.

### Woordenschatvariatie (Type-Token Ratio — TTR)

TTR = unieke woorden ÷ totaal woorden. Menselijk schrijven: 0.50–0.70. AI-schrijven: 0.30–0.50.
De tool waarschuwt bij TTR < 0.45.

AI herhaalt dezelfde woorden. Mensen gebruiken synoniemen en omschrijvingen.

**Slecht:**
> De organisatie heeft een duurzaam beleid. De organisatie implementeert dit beleid actief. Het beleid van de organisatie is gericht op...

**Goed:**
> Het bedrijf heeft duurzaamheid hoog op de agenda. Dit beleid omvat concrete maatregelen voor energiereductie. Het concern heeft daarvoor...

**Richtlijn:** Gebruik niet meer dan twee keer hetzelfde zelfstandig naamwoord in één alinea als er synoniemen beschikbaar zijn.

### N-gram Repetitie

AI-tekst bevat herhalende woordcombinaties.

**Controleer:**
- Begint elke alinea met hetzelfde woord? (Bovendien / Tevens / Daarnaast)
- Gebruik je steeds dezelfde bijvoeglijk naamwoord + zelfstandig naamwoord combinaties?
- Herhalen zinsopeningen zich over de tekst? ("Het is belangrijk dat... / Het is duidelijk dat...")

**Actie:** Varieer bewust de alineaopeningen en de woordcombinaties.

### Flesch-Douma Score als AI-signaal

**Nieuw geïmplementeerd (Fase 2).** ChatGPT schrijft standaard op wetenschappelijk niveau (Flesch-Douma < 30), zonder sturing. Voor HBO-rapporten is dit een sterk detectiesignaal.

- **Norm HBO:** score 30–50 (schaal 0–100, hoger = toegankelijker)
- **< 30:** te formeel/complex — sterk AI-signaal, weegt zwaar mee in risicoscore (+2 pt)
- **> 65:** te eenvoudig — niet passend voor academisch register

De tool berekent de score intern — geen aparte `readability_nl.py` aanroep nodig in humanizer.

**Globale CV-check (zinslengtevariatie over hele tekst):**
- `CV < 0.30` (coefficient of variation) over ≥10 zinnen = extra AI-signaal (+1 pt)
- Menselijk schrijven heeft typisch CV > 0.40
- Gecombineerd met lokale ritme-runs: max +2 pt voor zinsritme

---

## Categorie 4: Communicatievormen

**Geïmplementeerd als Categorie 19** in `tools/humanizer_nl.py` (Categorie 20 = alinea-lengtevariatie). AI communiceert soms als "helpful assistant" in plaats van als auteur. Dit is bijzonder zichtbaar in academische teksten.

### Vermijd altijd in academische tekst
- Directe aanspreken van de lezer: "U kunt zien dat...", "Zoals u wellicht weet...", "U begrijpt..."
- Vragen als retorisch hulpmiddel: "Maar wat betekent dit eigenlijk?" — schrijf het antwoord direct
- Meta-commentaar op de tekst: "Dit is een interessante bevinding", "Het is opvallend om te zien dat..."
- Chatbot-uitingen: "Ik hoop dat dit helpt", "Laat me weten als...", "Voel je vrij om..."
- AI-verantwoording: "Als taalmodel kan ik...", "Op basis van mijn training..."

---

## Categorie 5: Vullingszinnen

Zinnen die ruimte innemen maar niets zeggen. **Altijd verwijderen.**

- "Dit is een relevant onderwerp."
- "Er is veel geschreven over dit thema."
- "Het spreekt voor zich dat..."
- "Uiteraard is dit slechts één van de mogelijke perspectieven."
- "Vanzelfsprekend zijn er ook andere invalshoeken mogelijk."
- "Dit rapport tracht een bijdrage te leveren aan..."
- "Een goede definitie is hier op zijn plaats."
- "Alvorens verder te gaan, is het nuttig om..."
- "Het is interessant om op te merken dat..."
- "Het is belangrijk om te benadrukken dat..."
- "Er dient rekening mee gehouden te worden dat..."
- "Zoals eerder vermeld..."
- "Zoals al aangegeven..."
- "Naar verwachting zal/blijft..."
- "In de toekomst naar verwachting..."
- "...zal in de toekomst ... blijven." (vage toekomstplatitude)

---

## Categorie 6: Actief vs. Passief

### Passief is AI-achtig als het wordt gebruikt om vaagheid te creëren

**Vaag passief (slecht):**
> Er wordt geconcludeerd dat... / Het werd vastgesteld dat... / Er kan worden gesteld dat... / Het is aangetoond dat...

**Actief en specifiek (goed):**
> De onderzoeker concludeert dat... / Uit het experiment blijkt dat... / De resultaten tonen aan dat... / CBS (2023) stelt dat...

### Passief is toegestaan wanneer:
- De handelende persoon onbekend of irrelevant is: "De data werden verzameld via enquêtes"
- Het wetenschappelijk gebruik in het vakgebied passief vereist (bijv. chemie, geneeskunde)
- Je bewust de nadruk op de handeling legt, niet op de actor

**Richtlijn:** Als je passief gebruikt, vraag jezelf dan: weet ik wie of wat handelt? Als ja, schrijf dan actief.

---

## Risicoscore Drempelwaarden

De `tools/humanizer_nl.py` berekent een risicoscore op basis van gedetecteerde patronen. Elk patroon levert 1 punt op (Flesch-Douma < 30 = +2 pt).

| Score | Risiconiveau | Betekenis |
|-------|-------------|-----------|
| 0–2 | Laag | Weinig of geen AI-patronen — tekst kan worden ingediend |
| 3–6 | Gemiddeld | Meerdere AI-signalen — herschrijf gemarkeerde alinea's |
| 7+ | Hoog | Sterke AI-indicatie — structureel herschrijven aanbevolen |

**Let op:** De drempels zijn aangepast van de oorspronkelijke 6+ (Hoog) naar 7+ om ruimte te houden voor de extra detectiecategorieën (Type 2b, vage bronvermeldingen, alinea-variatie) zonder goede teksten te onterecht als "Hoog" te markeren.

---

## Snelcheck: Is Deze Zin AI?

Stel jezelf bij elke verdachte zin de volgende vijf vragen:

1. **Staat er een Niveau 1-woord in?** → Vervang het altijd
2. **Zegt de zin iets specifieks?** Als het ook over een compleet ander onderwerp zou kunnen gaan, is het te vaag → Concretiseer
3. **Is het een aanloopzin?** Kondigt het aan wat er gaat komen in dezelfde paragraaf? → Verwijder, begin direct
4. **Is dit de derde (of meer) zin op rij van ongeveer gelijke lengte?** → Varieer de zinslengte
5. **Begint de derde alinea op rij met hetzelfde woord?** (Bovendien / Tevens / Daarnaast) → Varieer de alineaopening

---

## Praktijkvoorbeeld: Voor en Na

### Originele tekst (AI-gegenereerd)
> In de huidige samenleving speelt duurzaamheid een cruciale rol. Het is duidelijk dat organisaties in toenemende mate aandacht besteden aan dit onderwerp. Bovendien biedt duurzaamheid kansen en uitdagingen voor bedrijven. Er dient rekening mee gehouden te worden dat de implementatie van duurzaam beleid aanzienlijke investeringen vereist.

**Geïdentificeerde problemen:**
- "In de huidige samenleving" — verboden openingszin (Type 1)
- "speelt een cruciale rol" — Niveau 1 AI-cliché
- "Het is duidelijk dat" — vullingszin
- "in toenemende mate" — vage tijdsindicator
- "Bovendien" — overgebruikt connectief aan het begin van een zin
- "biedt kansen en uitdagingen" — nietszeggend managementcliché (Niveau 1)
- "Er dient rekening mee gehouden te worden" — passieve vullingszin
- "aanzienlijke investeringen" — vage kwantificering (Niveau 1)
- Alle zinnen: 11–14 woorden — geen variatie

### Herschreven versie
> Duurzaamheid staat hoog op de agenda van Nederlandse bedrijven. Dat is geen toeval: de EU-taxonomie verplicht bedrijven vanaf 2025 om klimaatrisico's in hun jaarverslag op te nemen. Maar de kosten zijn reëel. Uit onderzoek van PwC (2023) blijkt dat een gemiddeld mkb-bedrijf tussen de €50.000 en €200.000 investeert bij de eerste stap naar een CO2-neutraal bedrijfsmodel.

**Verbeteringen:**
- Direct inhoudelijk begin (geen aanloop)
- Concrete reden (EU-taxonomie, 2025) vervangt vage tijdsindicator
- Actieve constructies
- Specifiek cijferbereik vervangt "aanzienlijk"
- Zinslengte: 9 / 22 / 6 / 26 woorden — hoge burstiness

---

## Nederlandse AI-Frases: Snelreferentie

Gebruik dit als woordenlijst voor automatische detectie (beschikbare `tools/humanizer_nl.py`).

### Frases om te vermijden (regex-detecteerbaar)

```
in de huidige samenleving
in de hedendaagse maatschappij
in een steeds veranderende (wereld|samenleving|context)
in het huidige tijdperk
tegenwoordig is het duidelijk dat
in de afgelopen jaren
speelt een (cruciale|centrale|sleutel|belangrijke|essentiële) rol
biedt kansen en uitdagingen
het is (duidelijk|evident|belangrijk|essentieel|cruciaal) (om|dat)
er dient rekening mee gehouden te worden
het spreekt voor zich
zoals eerder vermeld
op basis van het voorgaande
al met al kan (gesteld|geconcludeerd) worden
bovenstaande (analyse|bevindingen) (tonen|laten) aan
in toenemende mate
een breed scala aan
in het kader van
met betrekking tot
ten aanzien van
alvorens verder te gaan
het is interessant om op te merken
tegen deze achtergrond
vanuit een \w+ perspectief
samenvattend kan worden gesteld dat
het mag duidelijk zijn dat
eerdere studies laten zien dat
in de literatuur wordt (gesteld|beschreven|aangegeven)
naar verwachting zal
in de toekomst naar verwachting
```

### Losse woorden om te tellen (Niveau 1 — altijd vervangen)

```
cruciaal, essentieel, baanbrekend, toonaangevend, naadloos, optimaliseren,
benutten, ontsluiten, synergie, verdiepen, holistische, grondig, aanzienlijk,
inzichten, uitdaging, dynamisch, innovatief, landschap,
duiken, duiken in, scala, betekenisvol, diepgaand, transformatief, katalysator,
speerpunt, robuust, faciliteert, demonstreert, onderstreept, weerspiegelt, stroomlijnen,
fosteren, testament aan, impact hebben op
```

### Anglicismen (Categorie 7 — altijd vervangen)

```
duiken in, het landschap van, fosteren, stakeholders, impact hebben op,
testament aan, het speelveld, synergie creëren, leverage, benchmarken
```

### Oxford Comma patroon (Categorie 8 — altijd verwijderen)

```
Patroon: [woord], [woord], en [woord]
Detectie regex: \b\w{2,}\s*,\s*\w{2,}\s*,\s+en\s+\w{2,}\b
Correctie: verwijder de komma voor 'en'
```

### Losse woorden om te tellen (Niveau 2 — max 1x per 500 woorden)

```
bovendien, tevens, echter, desalniettemin, voorts, derhalve, aldus,
significant, duidelijk, evident, uiteraard, vanzelfsprekend, complexiteit,
genuanceerd, uitgebreid, proactief, integraal, zodoende, passie, verheugd,
in veel gevallen, in sommige gevallen, in zekere mate, biedt, bieden
```

---

## Aanvullende Detectiecategorieën

De beschikbare `tools/humanizer_nl.py` controleert naast de bovenstaande categorieën ook op:

### Alinea-lengtevariatie (Categorie 20)

**Nieuw geïmplementeerd.** ChatGPT genereert alinea's van gelijkmatige lengte. Menselijk schrijven varieert sterk per alinea.

De tool berekent de Coefficient of Variation (CV) over alle alinea's van ≥ 30 tekens, bij minimaal 4 alinea's.

- **CV < 0.25** over ≥ 4 alinea's → uniformiteitsignaal (+1 punt in risicoscore)
- **CV > 0.40** → gezonde variatie, geen signaal

**Interpretatie:** Als alle alinea's gemiddeld 60–80 woorden lang zijn met weinig onderlinge spreiding, wijst dat op AI-schrijven. Mensen variëren: een korte alinea van 2 zinnen na een uitgebreide van 10 zinnen is normaal.

**Actie bij signaal:** Voeg bewust een korte alinea toe (1–2 zinnen) voor nadruk, of splits een te lange alinea op in een substantieel deel en een samenvattende slotzin.

### Passief-dichtheid
AI genereert overmatig passieve constructies. De tool waarschuwt bij meer dan 40% passieve zinnen. Herschrijf passief naar actief waar de handelende persoon bekend is.

### Connector-dichtheid
AI begint zinnen overmatig met connectors (bovendien, tevens, daarnaast, echter, etc.). De tool waarschuwt als meer dan 30% van de zinnen met een connector begint. Varieer zinsopeningen.

### Zinsstarter-diversiteit
Binnen een alinea mogen niet meer dan drie opeenvolgende zinnen met hetzelfde woord beginnen. Specifiek "Daarnaast" als veelvuldig gebruikte opener wordt apart gesignaleerd.

### Bijvoeglijk-naamwoordstapeling
AI stapelt meerdere bijvoeglijke naamwoorden: "een innovatief, baanbrekend en transformatief project". Kies het belangrijkste bijvoeglijk naamwoord of beschrijf eigenschappen in aparte zinnen.

### Tricolon-detectie
Driedelige opsommingen ("A, B en C") zijn een AI-patroon bij herhaling (4+ keer in een tekst). Wissel af met twee- of vierdelige opsommingen.

### MATTR (Moving Average Type-Token Ratio)
Verbeterde versie van TTR die onafhankelijk is van tekstlengte. Venster van 50 woorden. Menselijk schrijven: 0.65-0.80. AI-schrijven: 0.50-0.65. Waarschuwing bij MATTR < 0.60.

---

## Categorie 7: Directe Engelse Vertalingen (Anglicismen)

AI-modellen zijn voornamelijk op Engelse data getraind. Ze vertalen Engelse constructies letterlijk naar het Nederlands. De tekst is grammaticaal correct maar klinkt on-Nederlands.

### Veelvoorkomende AI-anglicismen in Nederlandse teksten

| Anglicisme | Engelse bron | Correct Nederlands |
|---|---|---|
| duiken in / laten we duiken | "delve into / let's dive in" | analyseer, onderzoek, bekijk nader |
| het landschap van | "the landscape of" | de sector, het veld, de markt — of wees specifiek |
| fosteren | "to foster" | bevorderen, stimuleren, aanmoedigen |
| stakeholders | "stakeholders" | betrokkenen, belanghebbenden — of omschrijf de groep |
| impact hebben op | "to have an impact on" | invloed hebben op, effect hebben op |
| testament aan | "a testament to" | bewijs van, aanwijzing voor |
| het speelveld | "the playing field" | de sector, de markt — of wees specifiek |
| synergie creëren | "to create synergy" | samenwerken, combineren |
| leverage | "leverage" | hefboom, voordeel, gebruik |
| benchmarken | "to benchmark" | vergelijken met, afmeten aan |

**Waarom dit werkt als detectiesignaal:** Nederlanders schrijven geen "fosteren" of "testament aan" — dit zijn directe vertalingen die een native speaker niet zou gebruiken. Hoe meer van deze constructies in één tekst, hoe hoger de kans op AI-origine.

**Actie:** Vervang altijd door het Nederlandse equivalent. Bij twijfel: zou een HBO-student dit woord gebruiken als ze het zelf typen (niet als ze AI parafraseren)? Zo niet, vervang het.

---

## Categorie 8: Oxford Comma in Nederlands

### Wat is de Oxford comma?

In het Engels is de Oxford comma de komma vóór "and" in een driedelige opsomming: "cats, dogs, and birds". AI-modellen, getraind op Engelse data, gebruiken dit patroon consequent.

In het Nederlands bestaat deze conventie niet. De komma vóór "en" in een opsomming is on-gebruikelijk en klinkt direct on-Nederlands.

**Fout (AI-patroon):**
> De aanpak is gericht op efficiëntie, kwaliteit, en duurzaamheid.

**Correct (Nederlands):**
> De aanpak is gericht op efficiëntie, kwaliteit en duurzaamheid.

### Detectie

De `tools/humanizer_nl.py` detecteert automatisch het patroon "X, Y, en Z" (komma direct vóór "en" in een driedelige opsomming). Elke occurrence is een directe AI-indicator.

**Uitzondering:** In complexe opsommingen waarbij de elementen zelf komma's bevatten, is een komma vóór "en" soms nodig voor leesbaarheid. Maar in simpele driedelige opsommingen is het altijd fout.

---

## Categorie 9: Sectietype en Acceptabele Patronen

Niet alle patronen zijn in elke sectie even problematisch. Sommige detectiesignalen zijn legitiem in specifieke rapportonderdelen.

| Sectie | Passief OK? | Tricolon? | Connectors? | Opmerking |
|---|---|---|---|---|
| Methode | Ja — standaardpraktijk | Neutraal | Beperkt | "De data werden verzameld via enquêtes" is correct academisch Nederlands |
| Resultaten | Gedeeltelijk | Neutraal | Beperkt | Beschrijf wat data tonen, niet wie handelt |
| Inleiding | Nee | Neutraal | Beperkt | Schrijf actief, presenteer eigen perspectief |
| Literatuuroverzicht | Gedeeltelijk | Neutraal | Matig | Passief bij het beschrijven van andermans werk is toegestaan |
| Discussie | Nee | Laag | Beperkt | Analyseer actief, auteursstem staat centraal |
| Conclusie | Nee | Laag | Minimaal | Geen platitudes, eindig met concrete bevinding of aanbeveling |
| Abstract | Nee | Laag | Minimaal | Actief, compact, specifiek |

**Praktische toepassing:** Wanneer `humanizer_nl.py` passief-dichtheid signaleert, controleer dan eerst in welke sectie de tekst staat. In een methodesectie is dit normaal; in een inleiding is het een probleem.

### Sectietype-specifieke passiefregels

Gebruik deze regels bij het beoordelen van passief gebruik per sectietype:

**Inleiding**
- Passief: alleen als de handelende actor echt onbekend is.
- Actief schrijven is de norm: presenteer het onderwerp, de context en de eigen positie.
- Richtlijn: ≤ 20% passieve zinnen acceptabel.

**Conclusie**
- Passief: niet, tenzij de zin beschrijvend is over een extern feit.
- Schrijf actief: "Dit onderzoek toont aan dat..." niet "Er werd aangetoond dat..."
- Richtlijn: ≤ 15% passieve zinnen.

**Methode / Procedure**
- Passief is structureel acceptabel — het benadrukt objectiviteit en reproduceerbaarheid.
- "De data werden verzameld via enquêtes" is correct academisch Nederlands.
- Richtlijn: tot 60% passieve zinnen is normaal voor deze sectie.

**Resultaten**
- Actief voor interpretaties: "De data tonen een stijging van..."
- Passief voor vastgestelde feiten die onafhankelijk van de auteur zijn: "Er werd een positief verband gevonden."
- Richtlijn: 30–50% passief is gebruikelijk.

**Discussie**
- Actief als norm: de auteursstem staat centraal.
- Passief alleen bij beschrijving van andermans bevindingen: "Eerder werd aangetoond dat..." is toegestaan.
- Richtlijn: ≤ 30% passief.

**Reflectie**
- Eerste persoon enkelvoud ("ik") is niet alleen toegestaan maar gewenst.
- Passief in reflectieteksten klinkt afstandelijk en ondermijnt de persoonlijke toon.
- Richtlijn: maximaal 10% passief; voorkeur voor actief met "ik".

**Technische documentatie** (bijv. CTF-challenges, installatiehandleidingen, systeembeschrijvingen)
- Passief is structureel in dit sectietype — instructies en procedures zijn beschrijvend van aard.
- Flag NIET als probleem wanneer de sectie technische stappen beschrijft: "De scan werd uitgevoerd met Nmap."
- Richtlijn: passief-dichtheid van 50–70% is normaal en acceptabel.

**Literatuuroverzicht**
- Passief bij het beschrijven van andermans werk is toegestaan.
- Actief bij het geven van eigen interpretatie of vergelijking.
- Richtlijn: 30–50% passief.

**Vaktermen:** Bepaalde wetenschappelijke termen bevatten woorden uit de Niveau 1-lijst maar zijn vakinhoudelijk correct. Zie Categorie 10 voor de whitelist.

---

## Categorie 10: Whitelist en Uitzonderingen

De `tools/humanizer_nl.py` gebruikt een whitelist om valse positieven te voorkomen. Bepaalde vaktermen bevatten Niveau 1-woorden maar zijn vakinhoudelijk legitiem.

### Huidige whitelist-items (worden niet als AI-patroon gemeld)

| Term | Reden voor uitzondering |
|---|---|
| `scala-programmeertaal` | Programmeertaal, geen vage kwantificering |
| `essentiële aminozuren` | Biochemische vakterm |
| `robuuste optimalisatie` | Wiskundig/statistisch vakterm |
| `robuuste schatting` | Statistisch vakterm |
| `essentieel hypertensie` | Medische diagnose |
| `dynamisch programmeren` | Informatica-algoritme |
| `kritieke pad` | Projectmanagement-vakterm |

### Eigen uitzonderingen toevoegen

Als een Niveau 1-woord in jouw domein een vaste technische betekenis heeft, kun je dat melden. De whitelist in het script is uitbreidbaar. Overleg met de beheerder of voeg de term toe aan het script onder `WHITELIST_NIVEAU1`.

### Wat de whitelist NIET dekt

De whitelist geldt alleen voor exacte vaktermcombinaties. Als je schrijft "de robuuste aanpak van het bedrijf", wordt "robuust" wel geflagged — want hier is het geen vakterm maar een vage kwalificering.

---

## Categorie 11: Leesbaarheid vs. Humanisering

### De tradeoff

Agressief humaniseren kan de leesbaarheid verminderen. Kortere zinnen verhogen de burstiness (AI-score verbetert) maar kunnen de tekst gefragmenteerd laten klinken. Dit is de tradeoff die bewust gemanaged moet worden.

**Doel:** burstiness (variatie in zinslengte), niet puur kortheid.

| Aanpak | Effect op AI-score | Effect op leesbaarheid |
|---|---|---|
| Alle zinnen korter maken | Verbetert (meer variatie) | Verslechtert (te gefragmenteerd) |
| Bewust korte + lange zinnen afwisselen | Verbetert | Gelijk of beter |
| Niveau 1-woorden vervangen door alternatieven | Verbetert | Neutraal tot beter |
| Passieven actief maken | Verbetert | Gelijk of beter |
| Anglicismen verwijderen | Verbetert | Beter (authentieker) |

### Richtlijn

- Streef naar een Flesch-Douma score van 30–50 voor HBO-rapporten (schaal 0–100, hoger = makkelijker)
- Controleer na humanisering altijd ook de Flesch-Douma score via `tools/readability_nl.py`
- Als de Flesch-Douma score daalt terwijl de humanizer-score verbetert, zijn de zinnen te kort of te gefragmenteerd geworden
- Gebruik `--compare` mode in `humanizer_nl.py` om voor/na te vergelijken: `python3 tools/humanizer_nl.py --compare origineel.txt herschreven.txt`
