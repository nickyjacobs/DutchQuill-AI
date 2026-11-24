# Changelog

Alle wijzigingen aan DutchQuill AI. Versies volgen [semver](https://semver.org/lang/nl/), de opbouw volgt
[Keep a Changelog](https://keepachangelog.com/nl/1.1.0/). Hoe een release gaat: [docs/project/releasen.md](docs/nl/project/releasen.md).

| Release | Datum | Kort gezegd |
|---|---|---|
| [2.0.0](#200---2026-11-24) | 2026-11-24 | Van hbo-projectmap naar Claude Code-plugin voor iedereen die tekst maakt |
| [1.2](#12---2026-03-24) | 2026-03-24 | Laatste versie als projectmap voor hbo-rapporten |

## [Unreleased]

### ✨ Nieuw

- Privacybeleid in het Nederlands en Engels ([docs/privacy.md](docs/nl/privacy.md)): wat op je computer blijft en welke
  gegevens wanneer naar welke host gaan.
- `plugin.json` heeft de velden voor de Claude Directory: documentatie, privacybeleid, support en licentie.

### 🔧 Veranderd

- Engels is de standaardtaal van de documentatie: `README.md` en `docs/` zijn Engels, de Nederlandse versies staan
  in `README.nl.md` en `docs/nl/`. Rechtsboven op elke pagina wissel je tussen English en Dutch.
- Het pad naar het icoon in `plugin.json` begint met `./`, zoals de manifestreferentie voorschrijft.

---

## [2.0.0] - 2026-11-24

> **Kort gezegd:** DutchQuill is nu een Claude Code-plugin voor iedereen die tekst maakt: rapporten, mails, posts,
> procesdocumenten en README's, met een visuele Studio voor de instellingen.

### 🧭 Voor jou

- **Installeren:** `/plugin marketplace add nickyjacobs/DutchQuill-AI`, dan
  `/plugin install dutchquill@dutchquill` en `/dutchquill:instellen`.
- **Kwam je van v1?** Je oude projectmap blijft werken zoals hij was. Zet je rapporten in de nieuwe werkmap
  (`1-input/rapporten/`) en vul je studentgegevens in via `/dutchquill:instellen`.
- **Pdf's die precies op je Word-bestand lijken:** installeer LibreOffice. `dq doctor` zegt of het nodig is.

### ✨ Nieuw

- Plugin met eigen marketplace: zes commando's (`schrijven`, `herschrijven`, `reviewen`, `humaniseren`,
  `instellen`, `bijwerken`) en drie subagents.
- Eén werkmap op een plek naar keuze, met invoermappen (notities, rapporten, beeld, bronnen, mijn-stijl) en
  uitvoer per actie, per titel en per versie (`v1`, `v2`, ...). Een vervolgronde komt als nieuwe versie bij
  dezelfde tekst, in dezelfde formaten.
- Eén configuratiebestand `dutchquill.yaml` met profielen (student, zakelijk, social, techniek en eigen profielen),
  controles die los aan of uit kunnen (APA, academische stijl, taal, humaniseren), een toonschaal met vijf niveaus
  en een vrije mix, uitvoerformaten, templates en privacy.
- DutchQuill Studio: een lokale, visuele pagina voor installatie en instellingen, in het Nederlands en Engels, licht
  en donker.
- Professionele gegevens (naam, functie, organisatie, contact, groet) voor de afsluiting van je mails, plus een
  handtekening of mailbanner als afbeelding.
- Twaalf genres met eigen sjabloon, waaronder mail, LinkedIn, SOP en README. Elk sjabloon is aan te passen of te
  vervangen door je eigen versie. Mails, posts en korte teksten komen in de chat.
- Invoer uit .docx, .pdf, .pptx, .xlsx, .csv, .md, .txt, .html en links; beelden worden klaargemaakt en met
  bijschrift in het document gezet. Subagent `bronnen-lezer` voor veel materiaal.
- Export naar docx, pdf, html, md en txt vanuit één bron, met de opmaak uit een .docx-template. Meegeleverd:
  `apa-hbo`, `zakelijk`, `notitie`. Eigen templates toevoegen, controleren en aanpassen.
- Humaniseren voor 2026: woordenlijsten per modelgeneratie (NL en EN), clusters in plaats van losse woorden,
  overcorrectie als patroon, drempels per genre, stemkalibratie op eigen teksten (`dq stem`, subagent
  `stem-analist`) en een feitencontrole na elke herschrijfronde (`dq feiten`).
- `/dutchquill:bijwerken` en een maandelijkse herinnering: de gidsen worden gecontroleerd tegen Scribbr NL, APA
  Style, Wikipedia en blader/humanizer, en alleen na akkoord bijgewerkt.
- Engelse gidsen (`en/humanize`, `en/style`) en een toongids.
- AI citeren volgens het APA-formaat van september 2025, met een AI-verantwoording.
- `dq doctor` controleert de omgeving en zegt hoe de pdf gemaakt wordt.
- Documentatie in het Nederlands en het Engels: een handleiding, naslag en projectdocs, met één beginpunt
  (`docs/README.md`).
- `dq tells` meet AI-patronen in Nederlandse en Engelse tekst, en rapporteert in de taal van de tekst.

### 🔧 Veranderd

- De gidsen zijn gesplitst in een kern (geldt altijd) en modules. De lijst met 26 "verboden woorden" is vervangen
  door sterke en zwakke patronen.
- De APA-export haalt de opmaak uit een template in plaats van uit de code.
- Documentmetadata is eerlijk: jouw titel en naam en het echte tijdstip van maken, zonder namen van gereedschap.
- Leesbaarheid (Flesch-Douma) wordt overal op dezelfde manier berekend: lopende tekst en opsommingen, zonder koppen
  en code.

### 🗑️ Verwijderd

- Verzonnen documentmetadata (willekeurige revisienummers, teruggedateerde tijdstempels, verzonnen bewerkingstijd).
- De Stop-hook met verboden woorden (vuurde op elk antwoord; de controle zit nu in de skills).
- De koppeling met kie.ai voor illustraties (komt mogelijk terug in 2.1).

---

## [1.2] - 2026-03-24

> **Kort gezegd:** laatste versie als projectmap voor hbo-rapporten (APA 7, AI-patronen, .docx-export).

[Unreleased]: https://github.com/nickyjacobs/DutchQuill-AI/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/nickyjacobs/DutchQuill-AI/compare/v1.2...v2.0.0
[1.2]: https://github.com/nickyjacobs/DutchQuill-AI/releases/tag/v1.2
