<p align="right"><b>🇬🇧 English</b> · <a href="../nl/naslag/configuratie.md">🇳🇱 Dutch</a></p>

# Configuration

All settings are in `dutchquill.yaml` in your workspace. Change them in DutchQuill Studio, by telling Claude
(`/dutchquill:instellen`), or in the file itself. `dq config valideer` checks the file; DutchQuill refuses to save
anything that doesn't fit, and keeps your comments and a `.bak`.

The keys are Dutch (they are the same in every language); the meaning is explained below.

## Precedence

From low to high: the defaults, `dutchquill.yaml`, the active profile (with its `basis` chain), a `.dutchquill.yaml`
in your project, and what you say in your question ("without APA", "lighter").

A built-in profile (student, zakelijk, social, techniek) always stays as it is. If you change a check, the tone or
the output while such a profile is active, DutchQuill makes its own copy `<name>-eigen` and makes it active.

## Per project

A `.dutchquill.yaml` in a project folder (for example a repository you write READMEs for) may contain these keys:
`werkmap`, `profiel`, `taal`, `controles`, `toon`, `uitvoer`. Example:

```yaml
taal: en
profiel: techniek
toon: { niveau: neutraal }
```

## All keys

Generated from `config/schema.json`.

<!-- tabel:begin -->
| Key | Values | Default | Meaning |
|---|---|---|---|
| `versie` | integer | `1` | Config version. |
| `taal` | `nl` \| `en` \| `auto` | `"nl"` | Language. auto follows the language of your material or request. |
| `profiel` | string | `"zakelijk"` | Active profile. Built in: student, zakelijk, social, techniek. Or one of your own below. |
| `profielen` | object | `{}` | Custom profiles. |
| `genre_profielen` | object | `{}` | Automatic profile per genre. For example mail: zakelijk. Overrides the active profile for that genre. |
| `mappen.input` | string | `"1-input"` |  |
| `mappen.output` | string | `"2-output"` |  |
| `mappen.notities` | string | `"notities"` |  |
| `mappen.rapporten` | string | `"rapporten"` |  |
| `mappen.beeld` | string | `"beeld"` |  |
| `mappen.bronnen` | string | `"bronnen"` |  |
| `mappen.mijn_stijl` | string | `"mijn-stijl"` |  |
| `mappen.schrijven` | string | `"schrijven"` |  |
| `mappen.herschrijven` | string | `"herschrijven"` |  |
| `mappen.reviewen` | string | `"reviewen"` |  |
| `mappen.humaniseren` | string | `"humaniseren"` |  |
| `mappen.templates` | string | `"templates"` |  |
| `versies` | boolean | `true` | Keep versions. Every new round on the same title goes into a new folder (v2, v3 and so on). |
| `privacy.languagetool` | boolean | `false` | Online grammar check (LanguageTool). An extra, automatic spelling and grammar check on top of the language round every text gets. Sends the text to api.languagetool.org. Off = only the language round, nothing extra leaves your computer. |
| `stem.gebruiken` | boolean | `true` | Write in my voice. Uses your own texts in the my-style folder as the model for rhythm and word choice. |
| `student` | object |  | Student details (optional). For the title page of an academic report. |
| `professioneel.naam` | string |  | Name. |
| `professioneel.functie` | string |  | Job title. |
| `professioneel.organisatie` | string |  | Organisation. |
| `professioneel.afdeling` | string |  | Department or team. |
| `professioneel.telefoon` | string |  | Phone. |
| `professioneel.email` | string |  | Email. |
| `professioneel.website` | string |  | Website. |
| `professioneel.linkedin` | string |  | LinkedIn. |
| `professioneel.groet` | string | `"Met vriendelijke groet,"` | Closing. Default for business emails; adapted to the tone. |
| `professioneel.handtekening` | string |  | Signature (image). |
| `professioneel.banner` | string |  | Email banner (image). |
| `templates` | object | `{}` | Custom templates. |
| `stijlen` | object | `{}` | Style names in your template. Only needed if your template uses other style names. |
| `bijwerken.herinnering_dagen` | integer | `30` | Reminder after (days). |

**In a profile** (`profielen.<name>.…`):

| Key | Values | Default | Meaning |
|---|---|---|---|
| `controles.apa` | boolean | `false` | APA 7. Citations, reference list, title page, figures and tables per APA 7. |
| `controles.academische_stijl` | boolean | `false` | Academic style. Formal and evidence-based: no colloquialisms, consistent tenses per section. |
| `controles.taalregels` | boolean | `true` | Language and spelling. Spelling, grammar, punctuation, readability. |
| `controles.humaniseren` | boolean | `true` | Humanize. Remove AI patterns and sound like you: rhythm, concrete detail, your own voice. |
| `toon.niveau` | `formeel` \| `zakelijk` \| `neutraal` \| `informeel` \| `luchtig` | `"neutraal"` | How should it sound?. From formal to light-hearted. |
| `toon.aanspreekvorm` | `auto` \| `je` \| `u` \| `geen` | `"auto"` | Form of address. auto picks per genre and reader; geen means: do not address the reader (academic). |
| `toon.mix` | string | `""` | Custom mix (free text). For example: businesslike, with a light closing line. |
| `uitvoer.formaten` | list of `docx` \| `pdf` \| `md` \| `txt` \| `html` | `["docx"]` | File formats. |
| `uitvoer.chat_voor` | list of `rapport` \| `onderzoeksrapport` \| `adviesrapport` \| `zakelijk-rapport` \| `technisch-rapport` \| `sop` \| `research-notitie` \| `mail` \| `linkedin` \| `social` \| `readme` \| `memo` \| `kort` | `["mail", "linkedin", "social", "kort"]` | Chat only (no file). These kinds of text only appear in the chat unless you say: save it. |
| `uitvoer.template` | string | `"zakelijk"` | Template. Name of a built-in or custom template. |
| `basis` | profile name |  | Based on. Name of another profile. Anything you do not set here comes from that one. |
| `taal` | `nl` \| `en` \| `auto` |  | Overrides the general language for this profile. |
<!-- tabel:eind -->
