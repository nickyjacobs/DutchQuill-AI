#!/usr/bin/env bash
# Een werkmap met het profiel student, één vak met een quick scan, en een kort rapport om na te kijken.
set -euo pipefail
source "$(dirname "$0")/../scaffold-dq.sh"
dq werkmap init --pad "$PWD/DutchQuill" --taal nl --profiel student --languagetool nee >/dev/null
dq config zet student.vakken '[{naam: Onderzoeksvaardigheden, code: OV1}]' >/dev/null
mkdir -p "$PWD/DutchQuill/templates/vakken/OV1"
cat > "$PWD/DutchQuill/templates/vakken/OV1/quick-scan.md" <<'QS'
# Quick scan Onderzoeksvaardigheden (OV1)

## Rapportage

- [ ] Het rapport heeft een inleiding met een hoofdvraag.
- [ ] De methode beschrijft wie er is bevraagd en hoe.
- [ ] De conclusie beantwoordt de hoofdvraag.
- [ ] Er is een literatuurlijst volgens APA 7.

## Praktijk

- [ ] De enquête is afgenomen bij minstens twintig studenten.
QS
cat > "$PWD/rapport.md" <<'RAPPORT'
# Fietsgebruik onder studenten van de hogeschool

## Inleiding

Steeds meer studenten komen met de fiets naar de campus. Dit rapport onderzoekt de vraag: waarom kiezen studenten
van de hogeschool voor de fiets, en wat houdt anderen tegen?

## Methode

In oktober 2026 vulden 42 studenten van drie opleidingen een korte enquête in. De vragen gingen over afstand,
weer, kosten en de fietsenstalling. Daarnaast spraken we vijf studenten die nooit fietsen.

## Resultaten

Van de 42 studenten fietsen er 27 dagelijks. Zij noemen vooral de kosten en de vrijheid. De studenten die niet
fietsen wonen gemiddeld 18 kilometer van de campus. Twee van de vijf geinterviewden vinden de stalling onveilig.

## Conclusie

Studenten kiezen voor de fiets omdat het goedkoop is en ze zelf hun tijd bepalen. Afstand houdt de rest tegen.
Een betere stalling kan helpen, maar lost het afstandsprobleem niet op.
RAPPORT
