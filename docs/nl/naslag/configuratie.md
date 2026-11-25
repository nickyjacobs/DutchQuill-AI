<p align="right"><a href="../../reference/configuration.md">🇬🇧 English</a> · <b>🇳🇱 Dutch</b></p>

# Configuratie

Alle instellingen staan in `dutchquill.yaml` in je werkmap. Je past ze aan in DutchQuill Studio, door het tegen
Claude te zeggen (`/dutchquill:instellen`), of in het bestand zelf. `dq config valideer` controleert het bestand;
DutchQuill weigert op te slaan wat niet klopt, en bewaart je commentaar en een `.bak`.

## Voorrang

Van laag naar hoog: de standaardwaarden, `dutchquill.yaml`, het actieve profiel (met zijn `basis`-keten), een
`.dutchquill.yaml` in je project, en wat je in je vraag zegt ("zonder APA", "luchtiger").

Een meegeleverd profiel (student, zakelijk, social, techniek) blijft altijd zoals het is. Pas je een controle, de
toon of de uitvoer aan terwijl zo'n profiel actief is, dan maakt DutchQuill een eigen kopie `<naam>-eigen` en zet
die actief.

## Per project

Een `.dutchquill.yaml` in een projectmap (bijvoorbeeld een repository waarvoor je README's schrijft) mag deze
sleutels bevatten: `werkmap`, `profiel`, `taal`, `controles`, `toon`, `uitvoer`. Voorbeeld:

```yaml
taal: en
profiel: techniek
toon: { niveau: neutraal }
```

## Alle sleutels

Gegenereerd uit `config/schema.json`.

<!-- tabel:begin -->
| Sleutel | Waarden | Standaard | Betekenis |
|---|---|---|---|
| `versie` | integer | `1` | Configversie. |
| `taal` | `nl` \| `en` \| `auto` | `"nl"` | Taal. auto volgt de taal van je materiaal of je vraag. |
| `profiel` | string | `"zakelijk"` | Actief profiel. Meegeleverd: student, zakelijk, social, techniek. Of een eigen profiel hieronder. |
| `profielen` | object | `{}` | Eigen profielen. |
| `genre_profielen` | object | `{}` | Automatisch profiel per genre. Bijvoorbeeld mail: zakelijk. Wint van het actieve profiel als het genre klopt. |
| `mappen.input` | string | `"1-input"` |  |
| `mappen.output` | string | `"2-output"` |  |
| `mappen.notities` | string | `"notities"` |  |
| `mappen.rapporten` | string | `"rapporten"` |  |
| `mappen.beeld` | string | `"beeld"` |  |
| `mappen.bronnen` | string | `"bronnen"` |  |
| `mappen.mijn_stijl` | string | `"mijn-stijl"` |  |
| `mappen.schrijven` | string | `"schrijven"` |  |
| `mappen.herschrijven` | string | `"herschrijven"` |  |
| `mappen.reviewen` | string | `"reviewen"` |  |
| `mappen.humaniseren` | string | `"humaniseren"` |  |
| `mappen.templates` | string | `"templates"` |  |
| `versies` | boolean | `true` | Versies bijhouden. Elke nieuwe ronde over dezelfde titel komt in een nieuwe map (v2, v3 enzovoort). |
| `privacy.languagetool` | boolean | `false` | Online taalcheck (LanguageTool). Een extra, automatische spelling- en grammaticacheck naast de taalronde die elke tekst krijgt. Stuurt de tekst naar api.languagetool.org. Uit = alleen de taalronde, er gaat niets extra naar buiten. |
| `stem.gebruiken` | boolean | `true` | Schrijf in mijn stem. Gebruikt je eigen teksten uit de map mijn-stijl als voorbeeld voor ritme, woordkeus en zinsopbouw. |
| `student` | object |  | Studentgegevens (optioneel). Voor de titelpagina van een hbo-rapport. |
| `professioneel.naam` | string |  | Naam. |
| `professioneel.functie` | string |  | Functie. |
| `professioneel.organisatie` | string |  | Organisatie. |
| `professioneel.afdeling` | string |  | Afdeling of team. |
| `professioneel.telefoon` | string |  | Telefoon. |
| `professioneel.email` | string |  | E-mail. |
| `professioneel.website` | string |  | Website. |
| `professioneel.linkedin` | string |  | LinkedIn. |
| `professioneel.groet` | string | `"Met vriendelijke groet,"` | Afsluitende groet. Standaard voor zakelijke mails; DutchQuill past hem aan op de toon. |
| `professioneel.handtekening` | string |  | Handtekening (afbeelding). |
| `professioneel.banner` | string |  | Mailbanner (afbeelding). |
| `templates` | object | `{}` | Eigen templates. |
| `stijlen` | object | `{}` | Stijlnamen in je template. Alleen nodig als je template andere stijlnamen gebruikt, bijvoorbeeld kop1: Kop 1 in een Nederlandse Word. |
| `bijwerken.herinnering_dagen` | integer | `30` | Herinnering na (dagen). |

**In een profiel** (`profielen.<naam>.…`):

| Sleutel | Waarden | Standaard | Betekenis |
|---|---|---|---|
| `controles.apa` | boolean | `false` | APA 7. Bronvermelding, literatuurlijst, titelpagina, figuren en tabellen volgens APA 7 (Scribbr NL). |
| `controles.academische_stijl` | boolean | `false` | Academische stijl. Formeel en onderbouwd: geen spreektaal, geen ik/je, werkwoordstijden per hoofdstuk. |
| `controles.taalregels` | boolean | `true` | Taal en spelling. Spelling, d/t, hoofdletters, komma's, samenstellingen, leesbaarheid. |
| `controles.humaniseren` | boolean | `true` | Humaniseren. AI-patronen eruit en klinken als jij: ritme, concrete details, je eigen stem. |
| `toon.niveau` | `formeel` \| `zakelijk` \| `neutraal` \| `informeel` \| `luchtig` | `"neutraal"` | Hoe klinkt het?. Van formeel (u, lange zinnen, geen humor) tot luchtig (je, korte zinnen, humor mag). |
| `toon.aanspreekvorm` | `auto` \| `je` \| `u` \| `geen` | `"auto"` | Aanspreekvorm. auto kiest per genre en lezer; geen betekent: de lezer niet aanspreken (academisch). |
| `toon.mix` | string | `""` | Eigen mix (vrij). Bijvoorbeeld: zakelijk, maar met een luchtige afsluiting. |
| `uitvoer.formaten` | lijst van `docx` \| `pdf` \| `md` \| `txt` \| `html` | `["docx"]` | Bestandsformaten. |
| `uitvoer.chat_voor` | lijst van `rapport` \| `onderzoeksrapport` \| `adviesrapport` \| `zakelijk-rapport` \| `sop` \| `research-notitie` \| `mail` \| `linkedin` \| `social` \| `readme` \| `memo` \| `kort` | `["mail", "linkedin", "social", "kort"]` | Alleen in de chat (geen bestand). Deze soorten tekst komen alleen in de chat, tenzij je zegt: sla op. |
| `uitvoer.template` | string | `"zakelijk"` | Template. Naam van een meegeleverde of eigen template. |
| `basis` | profielnaam |  | Bouwt voort op. Naam van een ander profiel. Alles wat je hier niet zet, komt daarvandaan. |
| `taal` | `nl` \| `en` \| `auto` |  | Overschrijft de algemene taal voor dit profiel. |
<!-- tabel:eind -->

`student` bevat `voornaam`, `tussenvoegsel`, `achternaam`, `studentnummer`, `instelling`, `faculteit`,
`opleiding`, `docenten` (lijst met `naam`, `rol`, `vak`) en `vakken` (lijst met `naam`, `code`). Inlevereisen en
beoordelingscriteria per vak staan in `templates/vakken/<CODE>/quick-scan.md` en `beoordelingscriteria.md`.

## Stijlnamen van een eigen template

Gebruikt je template andere stijlnamen dan Word standaard heeft, vertaal ze dan met `stijlen`. Sleutels:
`titel`, `ondertitel`, `kop1` tot `kop4`, `normaal`, `lijst_bullet`, `lijst_nummer`, `bijschrift`, `citaat`,
`code`, `tabel`. `dq template check <naam>` stelt de vertaling voor.

```yaml
stijlen:
  kop1: "Kop 1"
  normaal: "Standaard"
```
