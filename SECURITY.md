# Beveiligingsbeleid

## Kwetsbaarheden melden

Heb je een beveiligingsprobleem gevonden in DutchQuill AI? Meld het dan via een **privébericht** in plaats van een publiek issue.

### Hoe melden

Stuur een e-mail naar de beheerder of gebruik [GitHub Security Advisories](https://github.com/nickyjacobs/DutchQuill-AI/security/advisories/new) om een privémelding te doen. Beschrijf:

- Wat het probleem is
- Hoe je het kunt reproduceren
- Welke bestanden of tools betrokken zijn

### Wat je kunt verwachten

- Bevestiging van ontvangst binnen 7 dagen
- Een inschatting van de impact en een oplossingsvoorstel
- Een update zodra de fix beschikbaar is

### Scope

Dit beleid geldt voor de code in deze repository: Python-tools, workflows, Claude Code configuratie en exportscripts. Het geldt niet voor Anthropic's API of Claude Code zelf.

## Dependencies

DutchQuill AI gebruikt de volgende externe packages (zie `requirements.txt`):

- python-docx
- requests
- matplotlib
- numpy
- reportlab

Dependabot scant deze dependencies automatisch op bekende kwetsbaarheden.

## Verantwoorde openbaarmaking

Maak een kwetsbaarheid niet publiek voordat er een fix beschikbaar is. Na de fix wordt de kwetsbaarheid vermeld in de release notes van de eerstvolgende versie.
