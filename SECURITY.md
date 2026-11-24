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

Dit beleid geldt voor de code in deze repository: de plugin (skills, agents, hook), de Python-scripts en DutchQuill Studio. Het geldt niet voor Anthropic's API of Claude Code zelf.

## Wat DutchQuill zelf doet

- DutchQuill Studio luistert alleen op 127.0.0.1, met een eenmalig token, en controleert Host en Origin.
- Webverzoeken gaan alleen naar de hosts in `.claude-plugin/plugin.json` (`network.hosts`): PyPI (de eenmalige
  installatie van de Python-pakketten), LanguageTool (alleen als je die aanzet) en de bronnen van
  `/dutchquill:bijwerken`.
- Interne adressen (localhost, privé-IP's) in je materiaal worden nooit automatisch opgehaald.

## Dependencies

De Python-pakketten staan in `requirements.txt` en worden in een eigen venv in de datamap van de plugin
geïnstalleerd. Dependabot scant ze op bekende kwetsbaarheden.

## Verantwoorde openbaarmaking

Maak een kwetsbaarheid niet publiek voordat er een fix beschikbaar is. Na de fix wordt de kwetsbaarheid vermeld in de release notes van de eerstvolgende versie.
