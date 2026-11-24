---
titel: Markdown-afspraken voor de export
versie: 1
gecontroleerd: 2026-11-24
---

# Markdown-afspraken voor de export

`dq export` maakt van één Markdown-bron een .docx, .pdf, .html, .md of .txt. Schrijf de bron zo:

## Metadata (frontmatter, optioneel)

```yaml
---
titel: Fietsgebruik onder studenten
ondertitel: Een verkennend onderzoek          # optioneel
auteur: Jan Jansen                             # standaard: de naam uit de config (student) of leeg
organisatie: Hogeschool Utrecht                # zakelijk: bedrijf of opdrachtgever
datum: 24 november 2026                        # standaard: vandaag
versie: "1.0"                                  # zakelijk, optioneel
classificatie: Intern                          # zakelijk, optioneel
# alleen APA/student (worden anders uit de config gehaald):
instelling: Hogeschool Utrecht
opleiding: Bedrijfskunde
studentnummer: "1234567"
vak: Onderzoeksvaardigheden (OZV2)
begeleider: dr. A. de Vries
---
```

## Koppen

- `#` hoofdstuk, `##` paragraaf, `###` subparagraaf, `####` daaronder.
- **Geen nummers in koppen** (`## Methode`, niet `## 2. Methode`). De template nummert als dat zo hoort.
- Koppen in zinsvorm.

## Lopende tekst

- Alinea's gescheiden door een witregel. `*cursief*` en `**vet**` mogen, met mate.
- Opsommingen met `-` of `1.`.
- Citaten van meer dan 40 woorden als blokcitaat (`> ...`).
- Code (README, SOP) in een codeblok met taal: ```` ```bash ````.

## Figuren

```markdown
In figuur 1 is te zien dat het aantal fietsers in de winter daalt.

![Aantal fietsende studenten per maand, 2025](pad/naar/fietsers.png)
```

- Het bijschrift tussen de haken, zonder "Figuur 1": de export nummert zelf.
- Verwijs in de tekst vóór de figuur ("in figuur 1", "zie figuur 2").
- Het pad is absoluut, of relatief aan `bron.md`. Gebruik de genormaliseerde beelden uit de materiaalmap.
- Bij APA: zet de bron onder de figuur als notitie: `*Noot.* Overgenomen van ... (CBS, 2025).`

## Tabellen

```markdown
**Tabel 1**
*Fietsgebruik per opleiding*

| Opleiding | Dagelijks | Wekelijks |
|---|---|---|
| Bedrijfskunde | 31% | 22% |
```

## Vaste secties bij APA (rapport, onderzoeksrapport, adviesrapport)

```markdown
# Samenvatting
<150-250 woorden>

*Sleutelwoorden:* fietsgebruik, studenten, mobiliteit

# Inleiding
...
# Methode
...
# Literatuurlijst
Jansen, J. (2024). *Titel van het boek*. Uitgever.

# Bijlage A
Vragenlijst enquête

<inhoud>
```

- `# Inleiding` is verplicht: de export vervangt die kop door de titel (APA 7).
- Een afkortingenlijst als `# Afkortingen` met een tabel `| Afkorting | Betekenis |`.
- Bijlagen staan na de literatuurlijst. Het label staat op een eigen regel (`# Bijlage A`), de titel op de
  volgende regel als platte tekst. Geen streepje tussen label en titel.

## Zakelijk rapport en SOP

Geen vaste secties. Begin met een korte samenvatting voor de lezer die maar één alinea leest. Gebruik
`# Samenvatting` als het rapport langer is dan twee pagina's.
