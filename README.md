<p align="center"><img src="assets/banner.jpg" alt="DutchQuill AI: schrijven, herschrijven, reviewen en humaniseren, in jouw stem"></p>

<p align="center">
  <a href="https://github.com/nickyjacobs/DutchQuill-AI/releases/latest"><img src="https://img.shields.io/github/v/release/nickyjacobs/DutchQuill-AI?label=release&color=1f4e5f" alt="Laatste release"></a>
  <a href="https://github.com/nickyjacobs/DutchQuill-AI/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/nickyjacobs/DutchQuill-AI/ci.yml?branch=main&label=tests&labelColor=2b2b2b" alt="Tests"></a>
  <img src="https://img.shields.io/badge/Claude_Code-plugin-D97757?logo=claude&logoColor=white" alt="Claude Code-plugin">
  <img src="https://img.shields.io/badge/taal-NL_%2B_EN-2a9daf" alt="Nederlands en Engels">
  <a href="LICENSE"><img src="https://img.shields.io/badge/licentie-MIT-yellow" alt="Licentie: MIT"></a>
</p>

<p align="center"><b>Schrijven, herschrijven, reviewen en humaniseren in Claude Code.<br>Nederlands eerst, Engels volwaardig, in jouw stem.</b></p>

<p align="center">
  <a href="#installeren">Installeren</a> ·
  <a href="#wat-je-ermee-doet">Wat je ermee doet</a> ·
  <a href="#dutchquill-studio">Studio</a> ·
  <a href="#je-werkmap">Werkmap</a> ·
  <a href="#humaniseren-eerlijk-gezegd">Humaniseren</a> ·
  <a href="#het-verhaal">Het verhaal</a> ·
  <a href="CHANGELOG.md">Changelog</a> ·
  <a href="README.en.md">English</a>
</p>

DutchQuill is een schrijfassistent voor Claude Code. Hij schrijft, herschrijft, reviewt en humaniseert je teksten:
een hbo-rapport, een procesbeschrijving, een mail, een LinkedIn-post of een README. Jij bepaalt waarop hij let, hoe
het klinkt en in welke vorm het terugkomt.

<p align="center"><img src="docs/img/toon-nl.gif" width="800" alt="DutchQuill Studio: dezelfde mail op vijf toonniveaus, van formeel tot luchtig"></p>

## Installeren

In Claude Code (versie 2.1.275 of nieuwer):

```text
/plugin marketplace add nickyjacobs/DutchQuill-AI
/plugin install dutchquill@dutchquill
```

Typ daarna `/dutchquill:instellen`. Je kiest dan zelf: DutchQuill Studio in je browser (een lokale pagina, er
gaat niets naar internet), of een paar vragen in de chat. De eerste keer installeert DutchQuill zijn
Python-pakketten in de datamap van de plugin; dat duurt ongeveer een minuut.

**Nodig:** Python 3.10 of nieuwer, of [uv](https://docs.astral.sh/uv/). **Voor pdf's:** LibreOffice (beste
resultaat), of Google Chrome of Microsoft Edge. Zonder die programma's maakt DutchQuill een eenvoudige pdf.

## Wat je ermee doet

| Commando | Wat het doet |
|---|---|
| `/dutchquill:schrijven` | Nieuwe tekst schrijven, vanuit je vraag of je materiaal in de werkmap |
| `/dutchquill:herschrijven` | Verbeteren, inkorten, formeler of luchtiger maken, vertalen NL↔EN, zonder dat er een feit verandert |
| `/dutchquill:reviewen` | Nakijken op taal, structuur, toon, AI-patronen en (als dat aan staat) APA en de rubric van je vak |
| `/dutchquill:humaniseren` | AI-patronen eruit, in je eigen stem; of alleen een scan |
| `/dutchquill:instellen` | Werkmap, profielen, controles, toon, templates en privacy, visueel of in de chat |
| `/dutchquill:bijwerken` | De referentiegidsen controleren tegen hun bronnen (je krijgt er één keer per maand een melding voor) |

Je hoeft de commando's niet te onthouden. "Schrijf een mail aan Sanne dat ik vrijdag later begin" of "klinkt dit
als AI?" werkt ook.

**Mails, posts en korte teksten** komen gewoon in de chat. **Documenten** gaan naar je werkmap, per titel en per
versie, in de formaten die je kiest: Word, pdf, Markdown, tekst of html.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/zo-werkt-het-nl-donker.png">
  <img src="docs/img/zo-werkt-het-nl-licht.png" alt="Zo werkt DutchQuill: jouw materiaal in 1-input, DutchQuill schrijft, herschrijft, reviewt of humaniseert met de controles die jij kiest, en het resultaat komt in de chat of in 2-output per titel en versie.">
</picture>

## DutchQuill Studio

`/dutchquill:instellen` opent desgewenst DutchQuill Studio: een pagina in je browser die alleen op je eigen computer
draait. Je kiest er je werkmap, profiel, toon, controles, uitvoer en templates, zonder één regel YAML. Licht of
donker, Nederlands of Engels. Niets wordt opgeslagen voordat je het overzicht van je wijzigingen hebt gezien.

<p align="center">
  <img src="docs/img/studio-werkmap.png" width="49%" alt="DutchQuill Studio: de werkmap als plaatje, van 1-input naar 2-output">
  <img src="docs/img/studio-uitvoer.png" width="49%" alt="DutchQuill Studio: bestandsformaten als kaarten en wat alleen in de chat komt">
</p>

## Je werkmap

Eén map voor alles, op de plek die jij kiest: het bureaublad, Documenten, of een Obsidian-vault.

```text
DutchQuill/
  dutchquill.yaml        je instellingen (met uitleg per regel)
  1-input/
    notities/            ruwe ideeën, aantekeningen van colleges of meetings
    rapporten/           bestaande of halve rapporten
    beeld/               screenshots, afbeeldingen, infographics
    bronnen/             artikelen en pdf's, of een links.md met URL's
    mijn-stijl/          een paar teksten die je zelf schreef
  2-output/
    schrijven/  herschrijven/  reviewen/  humaniseren/
      <titel>/v1/  v2/  ...
  templates/             je eigen Word-templates
  eigen-regels.md        woorden die je nooit (of juist wel) wilt
```

DutchQuill leest .docx, .pdf (ook gescand), .pptx, .xlsx, .csv, .md, .txt, .html en links. Beelden worden
klaargemaakt (oriëntatie goed, metadata eruit) en met een bijschrift op de juiste plek in je document gezet.

## Profielen en controles

Een profiel is een startpunt:

| Profiel | Voor | Controles | Toon | Uitvoer |
|---|---|---|---|---|
| student | hbo-rapporten, scripties | APA, academische stijl, taal, humaniseren | formeel | docx en pdf, template apa-hbo |
| zakelijk | werkdocumenten, rapporten, mails | taal, humaniseren | zakelijk | docx, template zakelijk |
| social | posts en korte teksten | taal, humaniseren | informeel | in de chat |
| techniek | README's, SOP's | taal, humaniseren | neutraal | Markdown |

Elke controle staat los aan of uit, de toon heeft vijf niveaus (formeel, zakelijk, neutraal, informeel, luchtig)
plus een vrij veld voor je eigen mix, en je maakt eigen profielen die op een ander profiel voortbouwen:

```yaml
profiel: mijn-scriptie
profielen:
  mijn-scriptie: { basis: student, controles: { humaniseren: false } }
  mijn-linkedin: { basis: social, toon: { niveau: luchtig, mix: "persoonlijk, één concreet voorbeeld" } }
genre_profielen: { mail: zakelijk, linkedin: mijn-linkedin }
```

Voor je mails vul je eenmalig je professionele gegevens in (naam, functie, organisatie, contact, groet), plus
eventueel een handtekening of mailbanner. Voor de titelpagina van een hbo-rapport zijn er studentgegevens. Alles
staat in [docs/configuratie.md](docs/configuratie.md).

<p align="center"><img src="docs/img/studio-controles.png" width="880" alt="DutchQuill Studio: controles los aan of uit, met een voorbeeld per controle"></p>

## Templates

Drie templates worden meegeleverd: `apa-hbo` (APA 7, zoals een hogeschool het wil), `zakelijk` en `notitie`.
Je eigen huisstijl voeg je toe door een .docx in `templates/` te zetten. DutchQuill controleert welke stijlen
erin zitten en vertaalt Nederlandse stijlnamen ("Kop 1") zelf. Andere koppen of een ander lettertype? Zeg het,
of gebruik de Studio: DutchQuill maakt een aangepaste kopie en laat het origineel staan.

Naast de Word-templates (hoe het eruitziet) is er per soort tekst een sjabloon (wat erin hoort): twaalf in totaal,
van mail en memo tot onderzoeksrapport en README. Pas een sjabloon aan in de Studio of upload je eigen versie;
terug naar de standaard kan altijd.

## Humaniseren, eerlijk gezegd

DutchQuill maakt tekst beter en persoonlijker:

- je eigen stem (gemeten aan je teksten in `mijn-stijl`);
- de AI-patronen van 2026 in het Nederlands en het Engels;
- specifiek in plaats van vaag;
- een feitencontrole: na elke herschrijfronde wordt nagegaan dat er geen getal, naam, citaat of bron
  verdwenen of bijgekomen is. DutchQuill verzint niets. Ontbreekt er iets, dan staat er `[bron nodig]`.

DutchQuill belooft niet dat een tekst "onzichtbaar" is voor AI-detectoren, en verandert geen
documentmetadata om iets te verbergen. Gebruik je AI voor een studieopdracht, houd je dan aan de regels van je
opleiding. DutchQuill helpt je met de verantwoording en de bronvermelding (APA, formaat van september 2025).

**Voor (AI):**

> In de huidige digitale wereld speelt kunstmatige intelligentie een cruciale rol in het onderwijs. Het is niet
> alleen een hulpmiddel, maar een transformatieve kracht. Kortom, de toekomst ziet er rooskleurig uit.

**Na (met een gegeven uit de notities van de schrijver):**

> Sinds januari mogen leerlingen op onze school AI gebruiken, als ze opschrijven waarvoor. De meesten gebruiken
> het om bronnen te ordenen of uitleg te krijgen bij een begrip dat ze niet snappen.

DutchQuill meet dat ook zelf. Dit is `dq tells` op precies deze twee teksten:

<p align="center"><img src="docs/img/tells-nl.gif" width="880" alt="dq tells op de voor-tekst: AI-patronen hoog, met vijf bevindingen; op de na-tekst: laag, geen patronen"></p>

## Privacy

- Je teksten blijven op je computer en in je gesprek met Claude.
- De online taalcheck (LanguageTool) staat standaard uit. Zet je hem aan, dan gaat je tekst naar
  api.languagetool.org.
- `/dutchquill:bijwerken` haalt alleen openbare pagina's op (Scribbr NL, Wikipedia, GitHub), en alleen als jij
  het commando geeft.
- DutchQuill Studio draait alleen op je eigen computer (127.0.0.1), met een eenmalige sleutel.

## Gidsen en bronnen

De regels komen uit gidsen in deze repository: APA 7 en taal volgens [Scribbr NL](https://www.scribbr.nl), AI
citeren volgens [APA Style](https://apastyle.apa.org) (september 2025), en AI-patronen volgens
[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
[blader/humanizer](https://github.com/blader/humanizer) (MIT) en eigen onderzoek naar Nederlandse tekst. De gidsen
bevatten eigen geformuleerde regels met bronverwijzing.

## Van v1 naar v2

Versie 1 was een map die je opende in Claude Code. Versie 2 is een plugin. Je oude rapporten en profielgegevens
neem je mee door ze in de nieuwe werkmap te zetten (`1-input/rapporten/`) en je gegevens in te vullen via
`/dutchquill:instellen`. Wat er veranderd is: [CHANGELOG.md](CHANGELOG.md).

## Het verhaal

<p align="center"><img src="assets/brandfoto.jpg" width="880" alt="Een laptop met DutchQuill AI op het scherm, naast een vulpen op handgeschreven notities"></p>

DutchQuill begon op de hogeschool. Mijn rapporten moesten volgens APA en op academisch niveau, en ik wilde precies weten wat dat betekende. Dat werd een flinke rabbit hole. De meeste mensen denken bij APA alleen aan bronvermelding, maar het gaat ook over de marges van je pagina, hoe je titelblad eruitziet, hoe je tabellen, figuren en bijlagen opneemt, het inspringen van elke alinea (ook de eerste) en de hangende inspringing in je literatuurlijst. En dan heb je nog de vraag wat academisch schrijven echt is, en hoe je AI daarbij gebruikt zonder jezelf voorbij te lopen.

Het begon met een Word-template die alles meteen goed zette. Daarna liet ik mijn rapporten nakijken, en met wat daaruit kwam maakte ik er volwaardige rapporten van.

Toen wilde ik meer. Sneller mails beantwoorden, makkelijker een LinkedIn-post schrijven, procesdocumentatie voor mijn werk of de README van een repo, allemaal vanuit ruwe notities, tekst en screenshots die ik al had verzameld. DutchQuill maakt daar een mooi eindresultaat van.

Op het eerste gezicht lijkt het misschien een tool van iemand die alles makkelijk wil. Deels klopt dat ook wel 😉 Maar voor mij was het vooral een leerproject. Ik weet nu meer over APA dan ik ooit had verwacht; soms wist ik dingen over inspringen, het juiste gebruik van bijlagen en andere APA-regels die docenten en medestudenten ook niet wisten. Ik leerde hoe AI tekst maakt, hoe plagiaatcontrole werkt en wat goed academisch schrijven is. Er zit veel tijd in, en het resultaat deel ik graag.

*Nicky Jacobs*

## Feedback

DutchQuill is gemaakt door één persoon en wordt beter van wat jij tegenkomt. Een fout of een idee? Open een
[issue](https://github.com/nickyjacobs/DutchQuill-AI/issues/new/choose) of start een
[discussie](https://github.com/nickyjacobs/DutchQuill-AI/discussions). Zelf meebouwen: [CONTRIBUTING.md](CONTRIBUTING.md)
en [docs/ontwikkelen.md](docs/ontwikkelen.md).

## Licentie

[MIT](LICENSE) © Nicky Jacobs
