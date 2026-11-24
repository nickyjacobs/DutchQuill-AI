---
titel: Toon
module: altijd (toon.niveau, toon.aanspreekvorm en toon.mix in de config)
versie: 1
gecontroleerd: 2026-11-24
bronnen:
  - https://www.nngroup.com/articles/tone-of-voice-dimensions/
  - https://www.vlaanderen.be/intern/werkplek/ondersteuning/heerlijk-helder/u-of-je
  - https://www.vlaanderen.be/team-taaladvies/taaladviezen/teksten-schrijven/brieven-en-e-mails/brieven-en-e-mails-structuur-en-stijl
---

# Toon

De toon komt uit de config (`toon.niveau`, `toon.aanspreekvorm`, `toon.mix`). De gebruiker kan hem per
opdracht overschrijven ("maak het wat luchtiger"). Een stemprofiel bepaalt *hoe* iemand klinkt; de toon bepaalt
hoe formeel dat moet zijn voor deze lezer. Bij een conflict wint de toon voor de vorm (je/u, emoji) en de
stem voor de rest (ritme, woordkeus).

## 1. De vijf niveaus

| | Formeel | Zakelijk | Neutraal | Informeel | Luchtig |
|---|---|---|---|---|---|
| **Aanspreekvorm** | u (of de lezer niet aanspreken) | u of je, vast binnen de tekst | je | je, jij, we | je, direct |
| **Zinslengte (gem.)** | 18-25 woorden | 14-20 | 12-18 | 8-15 | wisselend, ook fragmenten |
| **Spreektaal** | nee | nee | zelden | ja ("even", "best wel") | ja |
| **Verkorte woorden** | nee | nee | nee | mag ('s, 'n) | mag |
| **Emoji** | nooit | nooit | nooit | hooguit één | hooguit twee |
| **Humor** | nee | nee | licht, droog | ja | duidelijk aanwezig |
| **Uitroeptekens** | nee | nee | zelden | mag | mag |
| **Ik-vorm** | nee (academisch) of beperkt | mag | ja | ja | ja |
| **Typisch voor** | scriptie, officiële brief, beleid | rapport voor werk, klantmail, SOP | README, kennisbank, nieuwsbrief | mail aan collega, post | post, uitnodiging, vrijdagmail |

Bij het academische profiel staat de aanspreekvorm op `geen`: de lezer wordt niet aangesproken, en de ik-vorm
alleen waar de opleiding dat toestaat (bijvoorbeeld in een reflectie).

## 2. Je of u

- `auto` kiest zo:
  - u voor onbekenden, klanten (tenzij hun eigen huisstijl je zegt), ouderen en officiële instanties;
  - je voor collega's, studiegenoten, een breed online publiek en README's.
- Gebruikt de ander in een mail al "je", dan mag jij dat ook.
- **Nooit mengen** binnen één tekst. Ook niet "u" in de aanhef en "je" in de afsluiting.
- In het Engels speelt dit niet. Daar verschuift de formaliteit naar woordkeus en contracties.

## 3. Dezelfde boodschap op vijf niveaus

Een team verplaatst een overleg en vraagt of de lezer kan.

- **Formeel:** "Het overleg van donderdag 28 november is verplaatst naar vrijdag 29 november om 10.00 uur.
  Wij verzoeken u te bevestigen of dit tijdstip u schikt."
- **Zakelijk:** "We verplaatsen het overleg van donderdag naar vrijdag 29 november, 10.00 uur. Kunt u laten
  weten of dat past?"
- **Neutraal:** "Het overleg schuift van donderdag naar vrijdag 29 november, 10.00 uur. Past dat voor je?"
- **Informeel:** "Het overleg van donderdag wordt vrijdag, om tien uur. Lukt dat bij jou?"
- **Luchtig:** "Donderdag wordt vrijdag: zelfde overleg, tien uur, verse koffie. Ben je erbij?"

## 4. Mix

`toon.mix` is vrije tekst voor wat niet in één niveau past. Lees het als een opdracht aan jezelf, bijvoorbeeld:

- "zakelijk, maar met een luchtige afsluiting": de hoofdtekst zakelijk, de laatste zin mag een knipoog zijn.
- "informeel, maar zonder emoji".
- "neutraal, met mijn eigen ervaring erin": ik-vorm en één concreet voorbeeld van de gebruiker.
- "formeel richting de klant, maar niet stijf": u, volledige zinnen, geen ambtelijke woorden ("middels",
  "teneinde", "dient te").

## 5. Standaardtoon per genre

Geldt als het profiel geen toon vastlegt en de gebruiker niets zegt.

| Genre | Niveau | Aanspreekvorm |
|---|---|---|
| Rapport (hbo), onderzoeksrapport | formeel | geen |
| Adviesrapport, zakelijk rapport, SOP, memo | zakelijk | auto |
| Research-notitie | neutraal | geen |
| README | neutraal | je |
| Mail | volgt de lezer: zakelijk naar buiten, neutraal of informeel intern | auto |
| LinkedIn | informeel | je |
| Social, kort | informeel | je |

## 6. Engels

Dezelfde vijf niveaus, maar de formaliteit zit in andere dingen:

- **Formeel en zakelijk:** geen contracties, geen phrasal verbs waar een gewoon werkwoord kan.
- **Neutraal:** contracties mogen.
- **Informeel en luchtig:** contracties, kortere zinnen, mag een grap.

Een zakelijke Engelse mail begint vaak met "Hi <naam>," en eindigt met "Best," of "Kind regards,".
