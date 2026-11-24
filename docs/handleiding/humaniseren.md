<p align="right"><b>🇳🇱 Nederlands</b> · <a href="../en/guide/humanizing.md">🇬🇧 English</a></p>

# Humaniseren

Humaniseren betekent bij DutchQuill: een tekst laten klinken alsof iemand hem schreef die het onderwerp kent. Meestal
is dat de schrijver zelf. Het resultaat is een betere tekst: preciezer, persoonlijker, prettiger om te lezen. De
inhoud verandert niet.

## Wat DutchQuill doet

- **Je eigen stem.** Zet een paar teksten die je zelf schreef in `mijn-stijl/` en klik in de Studio op "Meet mijn
  stem" (of vraag het Claude). De subagent `stem-analist` maakt er een stemprofiel van: zinslengte, variatie,
  hoe je zinnen begint, je leestekens, je of u. Wat jij zelf doet, gaat voor elke algemene regel.
- **De AI-patronen van 2026,** in het Nederlands en het Engels: woorden per modelgeneratie, formules als "niet
  alleen X, maar ook Y", lege openers en afsluiters, vage bronnen, en overcorrectie (te veel korte, afgekapte
  zinnen). DutchQuill scoort op clusters, niet op losse woorden: "cruciaal" in één zin is geen probleem.
- **Specifiek in plaats van vaag.** Een algemene zin wordt een concreet voorbeeld uit je eigen materiaal.
- **Een feitencontrole.** Na elke herschrijfronde controleert `dq feiten` dat er geen getal, naam, datum, citaat
  of bron verdwenen of bijgekomen is. DutchQuill verzint niets; ontbreekt er iets, dan staat er `[bron nodig]`.
- **Drempels per soort tekst.** Een LinkedIn-post mag luchtiger dan een rapport; bij informele tekst grijpt
  DutchQuill minder snel in.

## Zelf meten

`dq tells` meet de AI-patronen in een tekst. Dit is de voor- en na-tekst uit de README:

![dq tells op de voor- en na-tekst](../img/tells-nl.gif)

Met `--compare origineel.md nieuw.md` zie je voor en na naast elkaar, met `--json` de volledige uitvoer. Zie
[Commando's](../naslag/commandos.md).

## Wat DutchQuill niet doet

DutchQuill belooft niet dat een tekst "onzichtbaar" is voor AI-detectoren. Het optimaliseert niet op
detectorscores en verandert geen documentmetadata om iets te verbergen: geen verzonnen bewerkingstijd, geen
verzonnen revisies, geen teruggedateerde tijdstempels. Een document krijgt jouw naam als auteur en het echte
tijdstip van maken.

Gebruik je AI voor een studieopdracht, houd je dan aan de regels van je opleiding. DutchQuill helpt met de
verantwoording: AI citeren volgens het APA-formaat van september 2025, en desgewenst een AI-verantwoording bij je
rapport.

## Waar de regels vandaan komen

De patronen staan in `gidsen/nl/humaniseren.md` en `gidsen/en/humanize.md`, de woordenlijsten in
`gidsen/data/tells_*.yaml`. Bronnen: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
[blader/humanizer](https://github.com/blader/humanizer) (MIT) en eigen onderzoek naar Nederlandse tekst. Hoe die
bijgehouden worden: [Gidsen en bronnen](../naslag/gidsen-en-bronnen.md).
