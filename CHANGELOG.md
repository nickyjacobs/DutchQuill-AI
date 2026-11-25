# Changelog

Every change to DutchQuill AI. Versions follow [semver](https://semver.org/), the layout follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). How a release works:
[docs/project/releasing.md](docs/project/releasing.md).

| Release | Date | In short |
|---|---|---|
| [2.0.2](#202---2026-11-25) | 2026-11-25 | LinkedIn posts no longer invent a lesson you didn't give |
| [2.0.1](#201---2026-11-25) | 2026-11-25 | Ready for the Claude Directory: privacy policy, English first, a cleaned git history |
| [2.0.0](#200---2026-11-24) | 2026-11-24 | From a project folder for Dutch higher education reports to a Claude Code plugin for anyone who writes |
| [1.2](#12---2026-03-24) | 2026-03-24 | Last version as a project folder for Dutch higher education reports |

## [Unreleased]

### 🔒 Security

- The privacy policy now says which personal data `dutchquill.yaml` can hold (student and professional profile), that
  it stays in that file and how to remove it.

---

## [2.0.2] - 2026-11-25

> **In short:** LinkedIn posts stick to what you told DutchQuill: no lesson or opinion you didn't give.

### 🐛 Fixed

- LinkedIn posts no longer draw a lesson or opinion you didn't give. The post leaves the step out or marks it with
  `[voorbeeld nodig]` and a short question, so you fill it in yourself.
- A LinkedIn post with only a few facts reads as one or two flowing paragraphs instead of a row of one-liners.

---

## [2.0.1] - 2026-11-25

> **In short:** DutchQuill is ready for the Claude Directory: a privacy policy, English-first documentation and a
> cleaned git history. The plugin itself works exactly as in 2.0.0.

### 🧭 For you

- **Nothing to do** if DutchQuill keeps updating. The commands, settings and workspace are unchanged.
- **Added the marketplace before 2026-11-25 and it no longer updates?** Remove it with `/plugin`, then add it again:
  `/plugin marketplace add nickyjacobs/DutchQuill-AI`. The reason is the history rewrite under 🔒 Security.
- **Reading in Dutch?** Every documentation page has a switch at the top right; the Dutch versions are in
  `docs/nl/` and `README.nl.md`.

### ✨ Added

- Privacy policy in English and Dutch ([docs/privacy.md](docs/privacy.md)): what stays on your computer and which
  data goes to which host, and when.
- `plugin.json` has the fields the Claude Directory needs: documentation, privacy policy, support and license.

### 🔧 Changed

- English is the default language of the documentation: `README.md` and `docs/` are in English, the Dutch versions
  are in `README.nl.md` and `docs/nl/`. Switch between English and Dutch at the top right of every page.
- `CONTRIBUTING.md`, `SECURITY.md` and `CODE_OF_CONDUCT.md` are in English, with a Dutch version next to each
  (`*.nl.md`).
- The CHANGELOG is in English, including the earlier releases. The section headings changed with it
  (`🧭 For you`, `✨ Added`, ...).
- The plugin and marketplace descriptions are in English, so the Claude Directory shows them in English.
- The icon path in `plugin.json` starts with `./`, as the manifest reference prescribes.

### 🔒 Security

- The git history was rewritten on 2026-11-25 to remove the fabricated-metadata code from v1, a private network
  range and personal contact details. The code of every release is unchanged, but all commit hashes and the tags
  `v1.0` to `v2.0.0` are new. Cloned the repo before that date? Clone it again. Added DutchQuill as a marketplace
  before that date and it no longer updates? Remove the marketplace and add it again.

---

## [2.0.0] - 2026-11-24

> **In short:** DutchQuill is now a Claude Code plugin for anyone who writes: reports, emails, posts, process
> documents and READMEs, with a visual Studio for the settings.

### 🧭 For you

- **Install:** `/plugin marketplace add nickyjacobs/DutchQuill-AI`, then
  `/plugin install dutchquill@dutchquill` and `/dutchquill:instellen`.
- **Coming from v1?** Your old project folder keeps working as it was. Put your reports in the new workspace
  (`1-input/rapporten/`) and fill in your student details with `/dutchquill:instellen`.
- **PDFs that look exactly like your Word file:** install LibreOffice. `dq doctor` tells you whether you need it.

### ✨ Added

- Plugin with its own marketplace: six commands (`schrijven`, `herschrijven`, `reviewen`, `humaniseren`,
  `instellen`, `bijwerken`) and three subagents.
- One workspace in a place of your choice, with input folders (notes, reports, images, sources, my style) and
  output per action, per title and per version (`v1`, `v2`, ...). A follow-up round becomes a new version of the
  same text, in the same formats.
- One configuration file, `dutchquill.yaml`, with profiles (student, business, social, technical and your own),
  checks you switch on or off one by one (APA, academic style, language, humanizing), a tone scale with five levels
  and a free mix, output formats, templates and privacy.
- DutchQuill Studio: a local, visual page for installation and settings, in Dutch and English, light and dark.
- Professional details (name, role, organization, contact, sign-off) to close your emails, plus a signature or
  email banner as an image.
- Twelve genres with their own template, including email, LinkedIn, SOP and README. You can adjust each template
  or replace it with your own. Emails, posts and short texts appear in the chat.
- Input from .docx, .pdf, .pptx, .xlsx, .csv, .md, .txt, .html and links; images are prepared and placed in the
  document with a caption. Subagent `bronnen-lezer` for large amounts of material.
- Export to docx, pdf, html, md and txt from one source, with the layout from a .docx template. Included:
  `apa-hbo`, `zakelijk`, `notitie`. Add, check and adjust your own templates.
- Humanizing for 2026: word lists per model generation (Dutch and English), clusters instead of single words,
  overcorrection as a pattern, thresholds per genre, voice calibration on your own texts (`dq stem`, subagent
  `stem-analist`) and a fact check after every rewrite round (`dq feiten`).
- `/dutchquill:bijwerken` and a monthly reminder: the guides are checked against Scribbr NL, APA Style, Wikipedia
  and blader/humanizer, and only updated after your approval.
- English guides (`en/humanize`, `en/style`) and a tone guide.
- Citing AI in the APA format of September 2025, with an AI statement.
- `dq doctor` checks the environment and tells you how the PDF is made.
- Documentation in Dutch and English: a guide, reference and project docs, with one starting point
  (`docs/README.md`).
- `dq tells` measures AI patterns in Dutch and English text, and reports in the language of the text.

### 🔧 Changed

- The guides are split into a core (always applies) and modules. The list of 26 "forbidden words" is replaced by
  strong and weak patterns.
- The APA export takes its layout from a template instead of from the code.
- Document metadata is honest: your title and name and the real time of creation, without tool names.
- Readability (Flesch-Douma) is calculated the same way everywhere: running text and lists, without headings and
  code.

### 🗑️ Removed

- Fabricated document metadata (random revision numbers, backdated timestamps, made-up editing time).
- The Stop hook with forbidden words (it fired on every answer; the check now lives in the skills).
- The kie.ai integration for illustrations (may return in 2.1).

---

## [1.2] - 2026-03-24

> **In short:** last version as a project folder for Dutch higher education reports (APA 7, AI patterns, .docx export).

[Unreleased]: https://github.com/nickyjacobs/DutchQuill-AI/compare/v2.0.2...HEAD
[2.0.2]: https://github.com/nickyjacobs/DutchQuill-AI/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/nickyjacobs/DutchQuill-AI/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/nickyjacobs/DutchQuill-AI/compare/v1.2...v2.0.0
[1.2]: https://github.com/nickyjacobs/DutchQuill-AI/releases/tag/v1.2
