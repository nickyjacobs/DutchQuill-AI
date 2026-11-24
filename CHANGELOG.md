# Changelog

Alle wijzigingen aan DutchQuill AI. Versies volgen [semver](https://semver.org/lang/nl/).

## [2.0.0] - nog niet uitgebracht

DutchQuill wordt een Claude Code-plugin voor iedereen die tekst maakt, niet alleen voor hbo-studenten.

### Nieuw

- Plugin met eigen marketplace: `/plugin install dutchquill@dutchquill`.
- Eén werkmap op een plek naar keuze, met invoermappen (notities, rapporten, beeld, bronnen, mijn-stijl) en
  uitvoer per actie, per titel en per versie (`v1`, `v2`, ...).
- Eén configuratiebestand `dutchquill.yaml` met profielen (student, zakelijk, social, techniek en eigen profielen),
  controles die los aan of uit kunnen (APA, academische stijl, taal, humaniseren), een toonschaal met vijf niveaus
  en een vrije mix, uitvoerformaten, templates en privacy.
- DutchQuill Studio: een lokale, visuele wizard voor installatie en instellingen.
- Professionele gegevens (naam, functie, organisatie, contact, afsluitende groet) voor de afsluiting van je mails,
  plus een handtekening of mailbanner als afbeelding.
- Eigen sjablonen per soort tekst: het meegeleverde sjabloon voor bijvoorbeeld een mail of notitie aanpassen in de
  Studio of je eigen versie uploaden. Terugzetten naar de standaard bewaart je eigen versie.
- Twaalf genres met eigen sjabloon, waaronder mail, LinkedIn, SOP en README. Mails, posts en korte teksten komen in
  de chat.
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

### Veranderd

- De gidsen zijn gesplitst in een kern (geldt altijd) en modules. De lijst met 26 "verboden woorden" is vervangen
  door sterke en zwakke patronen.
- De APA-export haalt de opmaak uit een template in plaats van uit de code.
- Documentmetadata is eerlijk: titel, auteur en het echte tijdstip van maken.

### Verwijderd

- Verzonnen documentmetadata (willekeurige revisienummers, teruggedateerde tijdstempels, verzonnen bewerkingstijd).
- De Stop-hook met verboden woorden (vuurde op elk antwoord; de controle zit nu in de skills).
- De koppeling met kie.ai voor illustraties (komt mogelijk terug in 2.1).

## [1.2] - 2026-03-24

Laatste versie als projectmap voor hbo-rapporten (APA 7, AI-patronen, .docx-export).
