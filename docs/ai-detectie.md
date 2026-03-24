# AI-detectie — Hoe het werkt

DutchQuill AI detecteert AI-schrijfpatronen in Nederlandse tekst via `tools/humanizer_nl.py`. Dit document legt uit wat de tool meet, hoe de risicoscore werkt en hoe je de uitkomsten leest.

---

## Wat de detector meet

AI-gegenereerde tekst is herkenbaar omdat het dezelfde woorden, dezelfde zinsstructuren en dezelfde patronen herhaalt. Dat is niet omdat AI slecht schrijft, maar omdat het statistische patronen volgt. Docenten en detectietools pikken dit op.

De detector gebruikt drie soorten signalen:

1. **Woordherkenning** — AI-typische woorden en uitdrukkingen die menselijke schrijvers niet snel zouden kiezen
2. **Structuurpatronen** — formulaïsche openers, aankondigingszinnen, vage afsluiters
3. **Statistieken** — zinslengtevariatie, woordenschatvariatie, alinealengtespreiding

Al deze signalen zitten in de 20 detectiecategorieën van `humanizer_nl.py`.

---

## Risicoscore

De tool telt gevonden patronen en kent een risiconiveau toe.

| Score | Niveau | Wat het betekent |
|-------|--------|-----------------|
| 0–2 | Laag | Weinig of geen AI-patronen. De tekst kan worden ingediend. Kleine aanpassingen zijn optioneel. |
| 3–6 | Gemiddeld | Meerdere AI-signalen gevonden. Herschrijf de gemarkeerde alinea's. |
| 7+ | Hoog | Sterke AI-indicatie. Structureel herschrijven is nodig. |

Elk gevonden patroon telt als 1 punt. Uitzondering: een Flesch-Douma score onder 30 telt als 2 punten omdat dit een sterk AI-signaal is. Een te lage variatie in zinslengte over de hele tekst telt als 1 extra punt.

---

## De 20 detectiecategorieën

### Categorieën 1–3: Woordenlijsten

**Categorie 1 — Niveau 1-woorden (directe AI-verraders)**

47 woorden en uitdrukkingen die vrijwel zeker op AI-schrijven wijzen. Altijd vervangen.

Voorbeelden: cruciaal, faciliteert, inzichten, baanbrekend, naadloos, speerpunt, transformatief, testament aan, fosteren, robuust, demonstreert, weerspiegelt, onderstreept, stroomlijnen, scala, betekenisvol, diepgaand, optimaliseren, holistische, toonaangevend.

De tool geeft bij elk gevonden woord een concreet alternatief.

**Categorie 2 — Niveau 2-woorden (verdacht bij clustering)**

44 woorden die individueel acceptabel zijn maar alarmerend worden als ze veel voorkomen. Drempel: meer dan 1 keer per 500 woorden.

Voorbeelden: bovendien, tevens, echter, desalniettemin, voorts, derhalve, aldus, significant, genuanceerd, uitgebreid, proactief, integraal, zodoende.

**Categorie 3 — Niveau 3-woorden (context-afhankelijk)**

6 woorden die verdacht zijn als ze meer dan 3% van de tekst uitmaken.

Voorbeelden: belangrijk, effectief, uniek, waardevol, opmerkelijk, substantieel.

---

### Categorieën 4–5: Formulaïsche structuren

**Categorie 4 — Formulaïsche openers**

AI begint alinea's en secties met herkenbare patronen. De tool detecteert vier types:

- **Type 1** — brede aanloop: "In de huidige samenleving...", "In het huidige tijdperk...", "In een wereld waar..."
- **Type 2** — aankondiging: "In dit rapport wordt onderzocht...", "Het doel van dit rapport is...", "Hieronder volgt een overzicht van..."
- **Type 2b** — contextueel kader: "Tegen deze achtergrond...", "Vanuit een [X] perspectief...", "In brede zin kan worden gesteld dat..."
- **Type 3** — samenvatting van wat je net schreef: "Kortom, het is duidelijk dat...", "Al met al kan gesteld worden dat...", "Op basis van het voorgaande..."

**Categorie 5 — Opvulzinnen**

28 patronen die ruimte innemen maar niets zeggen. Altijd verwijderen. Voorbeelden: "Dit is een relevant onderwerp.", "Het spreekt voor zich dat...", "Zoals eerder vermeld...", "Naar verwachting zal dit in de toekomst..."

---

### Categorieën 6–9: Stijlpatronen

**Categorie 6 — Em-dashes**

De em-dash (—) en het gedachtestreepje (` - `) horen niet in lopende Nederlandse tekst. AI gebruikt ze consequent omdat het op Engelstalige data is getraind. Vervang door een komma, punt of splits de zin.

**Categorie 7 — Vage bronverwijzingen**

17 patronen als "Uit onderzoek blijkt dat...", "Studies tonen aan dat...", "Experts stellen dat..." zonder concrete citatie. Dit is tegelijk een AI-patroon en een APA-overtreding.

**Categorie 8 — Uniforme zinslengte**

Als 5 of meer opeenvolgende zinnen allemaal binnen 30% van elkaar liggen in woordlengte, geeft de tool een signaal. AI schrijft monotoon; mensen variëren.

**Categorie 9 — Herhalende alineastarters**

Als dezelfde opener (bijv. "Bovendien", "Tevens", "Daarnaast") bij meerdere alinea's terugkomt.

---

### Categorieën 10–16, 20: Technische detectie

**Categorie 10 — Zinsstarterdiversiteit**

Binnen een alinea mogen niet meer dan drie opeenvolgende zinnen met hetzelfde woord beginnen.

**Categorie 11 — Passieve dichtheid**

De tool waarschuwt bij meer dan 40% passieve zinnen. De grens verschilt per sectietype: in een methodesectie is 60% passief normaal, in een inleiding niet meer dan 20%.

**Categorie 12 — Connectordichtheid**

Als meer dan 30% van de zinnen begint met een connector (bovendien, tevens, daarnaast, echter, voorts), geeft de tool een signaal.

**Categorie 13 — Bijvoeglijk naamwoordstapeling**

Drie of meer bijvoeglijke naamwoorden vóór een zelfstandig naamwoord. "Een innovatief, baanbrekend en transformatief project" is een AI-patroon.

**Categorie 14 — Tricolon**

Driedelige opsommingen (A, B en C) zijn een AI-patroon bij herhaling. De tool signaleert dit bij 4 of meer voorkomens in één tekst.

**Categorie 15 — MATTR (Moving Average Type-Token Ratio)**

Maat voor woordenschatvariatie die onafhankelijk is van tekstlengte. Berekend over een venster van 50 woorden.

| MATTR | Interpretatie |
|-------|---------------|
| 0.65–0.80 | Menselijk schrijven |
| 0.50–0.65 | Grensgebied |
| < 0.60 | Waarschuwing: te weinig woordvarieteit |

**Categorie 16 — Proportionele Niveau 1-scoring**

Schaalt de Niveau 1-score mee met de documentlengte. Een tekst van 100 woorden met één Niveau 1-woord scoort anders dan een tekst van 1.000 woorden met hetzelfde woord.

**Categorie 17 — Oxford comma**

De komma vóór "en" in driedelige opsommingen is Engels en on-Nederlands. AI gebruikt hem consequent.

- Fout (AI): "De aanpak is gericht op efficiëntie, kwaliteit, en duurzaamheid."
- Goed: "De aanpak is gericht op efficiëntie, kwaliteit en duurzaamheid."

**Categorie 18 — Anglicismen**

9 directe vertalingen uit het Engels die een native speaker niet zou schrijven: duiken in, het landschap van, fosteren, testament aan, stakeholders, leverage, het speelveld, synergie creëren, benchmarken.

**Categorie 19 — Communicatievormen**

9 chatbotpatronen die in academische tekst niet horen: directe aanspreken van de lezer ("U kunt zien dat..."), retorische vragen, meta-commentaar ("Dit is een interessante bevinding"), chatbotuiting ("Laat me weten als...").

**Categorie 20 — Alinealengtevariatie**

ChatGPT schrijft alle alinea's even lang. De tool berekent de Coefficient of Variation (CV) over alle alinea's van 30+ tekens bij minimaal 4 alinea's.

| CV | Signaal |
|----|---------|
| < 0.25 | Uniformiteitsignaal (+1 punt in risicoscore) |
| > 0.40 | Gezonde variatie, geen signaal |

---

## Flesch-Douma leesbaarheidsindex

De tool berekent ook de leesbaarheid van de tekst via de Flesch-Douma formule.

```
Score = 206,835 − 0,93 × (woorden / zinnen) − 77 × (lettergrepen / woorden)
```

ChatGPT schrijft standaard op wetenschappelijk niveau (score onder 30) zonder sturing. Voor HBO-rapporten is dit een sterk detectiesignaal.

| Score | Niveau | Geschikt voor HBO? |
|-------|--------|-------------------|
| 0–30 | Zeer moeilijk | Mogelijk te complex — score telt als +2 pt in risico |
| 30–50 | Moeilijk | Streefniveau voor HBO |
| 50–65 | Redelijk | Aan de bovengrens |
| 65–80 | Standaard | Te eenvoudig |
| 80+ | Eenvoudig | Niet geschikt voor academisch |

Een score onder 30 telt als twee extra punten in de risicoscore omdat het een sterk AI-signaal is.

---

## Whitelist voor vakspecifieke termen

De tool heeft een ingebouwde whitelist voor termen die Niveau 1-woorden bevatten maar vakinhoudelijk correct zijn. Die termen worden niet meegeteld in de score.

| Term | Vakgebied |
|------|-----------|
| `scala-programmeertaal` | Informatica |
| `essentiële aminozuren` | Biochemie |
| `robuuste optimalisatie` | Wiskunde / statistiek |
| `robuuste schatting` | Statistiek |
| `essentieel hypertensie` | Geneeskunde |
| `dynamisch programmeren` | Informatica |
| `kritieke pad` | Projectmanagement |

**Hoe de whitelist werkt:** Alleen exacte combinaties worden vrijgesteld. "Robuuste schatting" staat op de whitelist, maar "de robuuste aanpak van het bedrijf" niet. Schrijf je in een vakgebied met andere vaste termen? Dan kun je die toevoegen aan `WHITELIST_NIVEAU1` in het script, of melden bij de beheerder.

---

## Voor- en naversie vergelijken

Gebruik `--compare` om de risicoscore voor en na het herschrijven naast elkaar te zien:

```bash
python3 tools/humanizer_nl.py --compare origineel.txt herschreven.txt
```

De output toont per categorie hoeveel patronen zijn verdwenen, bijgekomen of gelijk gebleven. Zo zie je direct of het herschrijven effect heeft gehad.

---

## Wanneer `/humaniseer` en wanneer `/herschrijven`

| Situatie | Skill |
|----------|-------|
| Je wilt weten of tekst AI-achtig klinkt | `/humaniseer` |
| Je wilt de tekst ook daadwerkelijk verbeteren | `/herschrijven` met doel `humaniseren` |
| Je wilt een volledige kwaliteitscheck op taal, APA en structuur | `/reviewen` |

`/humaniseer` analyseert en rapporteert. `/herschrijven` past de tekst aan. Gebruik `/humaniseer` eerst om te zien hoe hoog de score is, en `/herschrijven` als je wil dat de tekst daadwerkelijk verandert.

---

## Leesbaarheid vs. humanisering

Agressief humaniseren kan de leesbaarheid verminderen. Te veel korte zinnen verhogen de burstiness maar maken de tekst gefragmenteerd. Bewust afwisselen werkt beter dan puur inkorten.

| Aanpak | Effect op AI-score | Effect op leesbaarheid |
|--------|-------------------|----------------------|
| Alle zinnen korter | Verbetert | Verslechtert (te gefragmenteerd) |
| Kort + lang afwisselen | Verbetert | Gelijk of beter |
| Niveau 1-woorden vervangen | Verbetert | Neutraal tot beter |
| Passief naar actief | Verbetert | Gelijk of beter |
| Anglicismen verwijderen | Verbetert | Beter (authentieker) |

Controleer na het herschrijven altijd ook de Flesch-Douma score via `tools/readability_nl.py`. Als die daalt terwijl de AI-score verbetert, zijn de zinnen te kort of te gefragmenteerd geworden.

---

## Praktijkvoorbeeld

**Originele tekst (score: Hoog)**
> In de huidige samenleving speelt duurzaamheid een cruciale rol. Het is duidelijk dat organisaties in toenemende mate aandacht besteden aan dit onderwerp. Bovendien biedt duurzaamheid kansen en uitdagingen voor bedrijven. Er dient rekening mee gehouden te worden dat de implementatie van duurzaam beleid aanzienlijke investeringen vereist.

Gevonden patronen: verboden opener (Type 1), "cruciale rol" (Niveau 1), "Het is duidelijk dat" (opvulzin), "in toenemende mate" (Niveau 1), "kansen en uitdagingen" (Niveau 1), passieve opvulzin, "aanzienlijke" (Niveau 1). Alle zinnen: 11–14 woorden (geen variatie).

**Herschreven versie (score: Laag)**
> Duurzaamheid staat hoog op de agenda van Nederlandse bedrijven. Dat is geen toeval: de EU-taxonomie verplicht bedrijven vanaf 2025 om klimaatrisico's in hun jaarverslag op te nemen. Maar de kosten zijn reëel. Uit onderzoek van PwC (2023) blijkt dat een gemiddeld mkb-bedrijf tussen de €50.000 en €200.000 investeert bij de eerste stap naar een CO2-neutraal bedrijfsmodel.

Zinslengte: 9 / 22 / 6 / 26 woorden. Directe inhoud, concrete cijfers, actieve constructies, geen Niveau 1-woorden.
