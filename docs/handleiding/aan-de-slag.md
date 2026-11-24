<p align="right"><b>🇳🇱 Nederlands</b> · <a href="../en/guide/getting-started.md">🇬🇧 English</a></p>

# Aan de slag

Van installeren tot je eerste document, in ongeveer tien minuten.

## 1. Installeren

Je hebt Claude Code nodig (versie 2.1.275 of nieuwer) en Python 3.10 of nieuwer, of [uv](https://docs.astral.sh/uv/).
Typ in Claude Code:

```text
/plugin marketplace add nickyjacobs/DutchQuill-AI
/plugin install dutchquill@dutchquill
```

Start Claude Code daarna opnieuw. Je ziet één keer de melding dat DutchQuill nog niet is ingesteld.

## 2. Instellen

Typ `/dutchquill:instellen`. Je kiest zelf hoe:

- **Visueel:** DutchQuill Studio opent in je browser. Dat is een pagina op je eigen computer; er gaat niets naar
  internet. Zie [De Studio](studio.md).
- **In de chat:** Claude stelt je een paar vragen.

Bij de eerste keer kies je drie dingen: waar je [werkmap](werkmap.md) komt (bijvoorbeeld op je bureaublad), welk
[profiel](profielen-en-toon.md) bij je past, en of de online taalcheck aan mag. DutchQuill installeert dan zijn
Python-pakketten in de datamap van de plugin. Dat duurt ongeveer een minuut, en gebeurt maar één keer.

## 3. Een korte tekst

Vraag gewoon wat je nodig hebt:

```text
Schrijf een korte mail aan mijn teamlead dat ik vrijdag een dag vrij wil nemen
```

Mails, posts en korte teksten komen in de chat. Er komt geen bestand, tenzij je "sla op" zegt.

## 4. Een document

Zet je materiaal in `1-input/` in je werkmap: notities, een half rapport, screenshots, pdf's. Vraag daarna
bijvoorbeeld:

```text
/dutchquill:schrijven Maak een procesdocument op basis van mijn notities en screenshots. Lever het als Word en pdf.
```

Dit gebeurt er:

1. Claude laat zien welk materiaal hij vond en vraagt wat erbij hoort.
2. Je krijgt eerst een opzet. Pas na jouw akkoord schrijft hij.
3. Het concept gaat langs de controles die aan staan (taal, AI-patronen, APA).
4. Het resultaat staat in `2-output/schrijven/<titel>/v1/`: het document in de formaten die je koos, plus
   `bron.md` (de Markdown-bron) en `wat-is-er-veranderd.md`.

Wil je iets veranderen, zeg het dan ("maak de inleiding korter"). Dat wordt `v2` in dezelfde map, in dezelfde
formaten. `v1` blijft staan.

## 5. Controleren of alles werkt

In een terminal, vanuit de pluginmap of via Claude:

```text
dq doctor
```

`dq doctor` laat zien welke Python er draait, of alle pakketten er zijn, waar je werkmap staat en hoe pdf's worden
gemaakt. Staat er een tip over LibreOffice, dan lijkt je pdf nu niet precies op je Word-bestand. Met LibreOffice
(gratis) wel.

## Verder

- [Je werkmap](werkmap.md): welke map waarvoor is en hoe versies werken.
- [Humaniseren](humaniseren.md): wat DutchQuill aan AI-patronen doet, en wat niet.
- [Vragen](vragen.md): privacy, pdf's, Windows, verwijderen.
