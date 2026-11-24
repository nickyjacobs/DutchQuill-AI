<p align="right"><a href="../../guide/templates.md">🇬🇧 English</a> · <b>🇳🇱 Dutch</b></p>

# Templates en sjablonen

DutchQuill kent twee soorten: een **template** bepaalt hoe een Word- of pdf-bestand eruitziet, een **sjabloon**
bepaalt wat er in een soort tekst hoort.

## Word-templates

Meegeleverd:

| Template | Voor |
|---|---|
| `apa-hbo` | APA 7 zoals een hogeschool het wil: titelpagina, inhoudsopgave, hangende inspringing in de literatuurlijst, figuur- en tabellabels |
| `zakelijk` | Rapporten en documenten voor werk |
| `notitie` | Korte stukken, procesdocumenten |

**Je eigen huisstijl:** zet een .docx in `templates/` in je werkmap, of upload hem in de Studio. DutchQuill
controleert welke stijlen erin zitten (Normal, Heading 1 tot 5, Caption, List Bullet, Bibliography) en vertaalt
Nederlandse stijlnamen ("Kop 1") zelf. Ontbreekt er iets, dan zegt de controle wat.

**Aanpassen zonder Word:** zeg het ("koppen in Arial 14, donkerblauw") of gebruik het blok "Een template
aanpassen" in de Studio. DutchQuill maakt een kopie met jouw lettertype, kleuren, regelafstand en marges, en laat
het origineel staan.

**Pdf's:** met LibreOffice (gratis) wordt de pdf een exacte kopie van het Word-bestand. Zonder LibreOffice maakt
DutchQuill de pdf via Chrome of Edge, in een eigen nette opmaak, of als laatste via een eenvoudige opmaak.
`dq doctor` laat zien welke route je hebt.

## Sjablonen per soort tekst

Er zijn twaalf sjablonen: mail, LinkedIn-post, andere social post, korte tekst, rapport (hbo), onderzoeksrapport,
adviesrapport, zakelijk rapport, procesdocument (SOP), research-notitie, memo en README. Een sjabloon beschrijft de
opbouw: welke onderdelen er in een mail of een SOP horen, en in welke volgorde.

Je eigen versie maken:

- **In de Studio:** Templates → Sjablonen per soort tekst → Aanpassen, of Uploaden (.md of .txt).
- **Zelf:** zet een bestand `templates/genres/<soort>.md` in je werkmap.

Jouw sjabloon gaat voor het meegeleverde. **Terug naar standaard** zet het meegeleverde terug en bewaart je eigen
versie in `templates/genres/oud/`.
