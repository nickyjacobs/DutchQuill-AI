<p align="right"><a href="../../guide/costs.md">🇬🇧 English</a> · <b>🇳🇱 Dutch</b></p>

# Kosten en modellen

DutchQuill zelf is gratis en kost niets per gebruik. Wat wel kost, is wat Claude leest en schrijft: tokens. Met
een Pro- of Max-abonnement tellen die mee voor je gebruikslimiet; met een API-sleutel betaal je per token
([prijzen van Anthropic](https://www.anthropic.com/pricing)). Deze pagina legt uit waar de tokens heen gaan en hoe
je ze laag houdt.

## Waar de tokens heen gaan

| Onderdeel | Tokens | Waarom |
|---|---|---|
| De gidsen | het meeste | Elke opdracht leest de werkwijze en de gidsen van de controles die aan staan. Dat is bewust: Claude volgt de actuele regels, niet wat het zich herinnert. |
| Je materiaal | wisselt | Notities, bronnen en eerdere versies die Claude leest. Veel materiaal gaat via de subagent `bronnen-lezer`, die één samenvatting teruggeeft. |
| De tekst zelf | het kleinste deel | Een mail schrijven kost weinig; een rapport van 5000 woorden meer, en elke herstelronde leest hem opnieuw. |
| De scripts (`dq`) | bijna niets | `dq tells`, `dq feiten`, de export en de andere scripts draaien op je computer. Claude leest alleen hun korte uitvoer. |

Een schatting uit de grootte van de gidsen (ongeveer vier tekens per token): een mail of LinkedIn-post leest
ruwweg 15.000 tot 20.000 tokens aan gidsen, een rapport met APA en academische stijl ruwweg 30.000 tot 40.000.
Daar komen je materiaal, de tekst en de herstelrondes (hooguit drie) bij.

## Welk model

- **De skills** (`schrijven`, `herschrijven`, `reviewen`, `humaniseren`, `instellen`, `bijwerken`) hebben geen
  vast model: ze draaien op het model dat je in Claude Code koos (`/model`). Schrijven en humaniseren vragen
  taalgevoel, dus DutchQuill kiest daar geen kleiner model voor je. In v1 draaide humaniseren op Haiku; v2 laat
  die keuze bij jou.
- **De subagents** hebben wel een vast model, omdat hun taak vastligt:

  | Subagent | Model | Taak |
  |---|---|---|
  | `tekst-analist` | Haiku | Draait de scripts en vat hun uitvoer samen |
  | `bronnen-lezer` | Sonnet | Leest veel materiaal en maakt er één overzicht van |
  | `stem-analist` | Sonnet | Leest je eigen teksten en beschrijft je stem |

## Zuinig aan

- **Sonnet is genoeg** voor bijna alles. Opus voor een lang rapport of een lastige herschrijving, als je het hebt.
- **Zet uit wat je niet nodig hebt.** Een controle die uit staat (APA, academische stijl, humaniseren) is een gids
  die niet gelezen wordt. Een profiel per soort tekst helpt: `social` voor posts leest geen APA.
- **Chat in plaats van een bestand** voor korte teksten: geen export en geen versiemap.
- **Laat de subagent lezen** bij meer dan een paar bestanden materiaal; je hoofdgesprek blijft dan klein.
- **Begin een nieuw gesprek** voor een nieuwe tekst. Een lang gesprek sleept alles van eerder mee.
- Met een API-sleutel laat `/cost` in Claude Code zien wat een sessie kostte.
