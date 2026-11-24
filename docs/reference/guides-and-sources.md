<p align="right"><b>🇬🇧 English</b> · <a href="../nl/naslag/gidsen-en-bronnen.md">🇳🇱 Dutch</a></p>

# Guides and sources

The rules DutchQuill follows are in guides in the `gidsen/` folder. Claude only reads the guides that belong to a
task (`dq gids voor`), so an email doesn't have to go through the APA rules.

## The guides

| Guide | When | Contents |
|---|---|---|
| `nl/kern.md` | always (Dutch text) | Basic rules for good Dutch: active, concrete, numbers, sentence length |
| `en/style.md` | always (English text) | Basic rules for good English, instead of `nl/kern.md` |
| `nl/taal.md` | language check (Dutch) | Spelling, verb endings, capitals, commas, compounds |
| `nl/academische-stijl.md` | academic style check | Formal, well-founded, tense per chapter |
| `nl/apa.md` | APA check | APA 7 according to Scribbr NL |
| `nl/ai-gebruik.md` | APA check | Citing AI (September 2025 format) and the AI disclosure |
| `nl/humaniseren.md`, `en/humanize.md` | humanize check | AI patterns and how to fix them |
| `toon.md` | always | What each tone level means |
| `data/tells_nl.yaml`, `data/tells_en.yaml` | `dq tells` | The word lists and formulas behind the AI patterns |
| `werkwijze/` | always | The shared workflow of the skills and the Markdown conventions for export |

Every guide starts with `bronnen:` (the URLs it relies on), `gecontroleerd:` (last checked) and `versie:`. The guides
contain rules in our own words with a reference, no copied text.

## The sources

- **Scribbr NL** for APA 7 and Dutch language rules, compared through its sitemap (one request, no crawling).
- **APA Style** for citing AI. That site refuses automated requests; Claude searches it for new posts itself.
- **[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)**, compared by
  revision number.
- **[blader/humanizer](https://github.com/blader/humanizer)** (MIT), compared by its latest release.

The list is in `gidsen/bronnen.yaml`.

## Updating

Once a month DutchQuill mentions at the start of a session that the guides can be checked again. With
`/dutchquill:bijwerken` (or the "Check now" button in the Studio):

1. `dq bronnen check` compares the sources with last time.
2. For each changed source Claude reads the page and puts it next to the guide.
3. You get a proposal with a diff per guide. Nothing is written until you agree.
4. Updated guides go to the plugin's data folder and win over the built-in ones, until a newer plugin version brings a
   newer guide.

Without changes only the date of the last check is updated, and the reminder is gone for another month.
