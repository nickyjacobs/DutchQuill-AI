<!-- Titel: "Prefix: zin in de gebiedende wijs", bijvoorbeeld "Add: sjabloon voor offertes". Prefixen: Add, Fix,
Update, Refactor, Docs. -->

## Wat en waarom

Wat verandert er, en welk probleem lost het op? Verwijs naar een issue als dat er is: closes #...

## Soort

- [ ] Fix
- [ ] Nieuw (commando, genre, sjabloon, AI-patroon, instelling)
- [ ] Documentatie
- [ ] Brekend: gebruikers moeten iets aanpassen in hun werkmap of `dutchquill.yaml`

## Voor gebruikers

Merken gebruikers dit? Zo ja: in één of twee zinnen wat ze zien of moeten doen. Dit komt in de CHANGELOG onder
"🧭 Voor jou".

## Checklist

- [ ] Gericht op `develop`
- [ ] `pytest` en `ruff check scripts hooks tests` zijn groen; nieuwe code in `scripts/` heeft een test
- [ ] Een regel onder `[Unreleased]` in CHANGELOG.md
- [ ] Nieuwe instellingen staan in `config/schema.json` met labels in NL en EN
- [ ] Geen persoons-, klant- of werkgeversgegevens, ook niet in voorbeelden of tests
