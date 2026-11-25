<p align="right"><b>🇬🇧 English</b> · <a href="../nl/handleiding/vragen.md">🇳🇱 Dutch</a></p>

# FAQ

## What goes to the internet?

- Your texts stay on your computer and in your conversation with Claude.
- The online language check (LanguageTool) is off by default. Switch it on and your text goes to
  api.languagetool.org.
- `/dutchquill:bijwerken` only fetches public pages (the Scribbr NL sitemap, Wikipedia, GitHub), and only when you
  run it.
- The first time, DutchQuill installs its Python packages from PyPI, in the plugin's data folder.
- DutchQuill Studio only runs on your own computer (127.0.0.1).

The hosts the plugin may reach are listed in `.claude-plugin/plugin.json` under `network.hosts`. The full overview
is in the [privacy policy](../privacy.md).

## Does DutchQuill check my spelling without LanguageTool?

Yes. Every text gets a language round as the last step: Claude reads it sentence by sentence for spelling,
grammar (in Dutch also d/t), commas and consistency, and fixes what it finds; a review lists it as findings. The
online check with LanguageTool comes on top of that and catches more small slips, but sends your text to
api.languagetool.org. That is why it is off by default.

## What metadata does DutchQuill put in my file?

By default the title and the author from your text or profile, and nothing about the tool: a PDF has no creator
or producer. In Word the creation time and revision are the ones python-docx sets (now, and 1). DutchQuill never
invents metadata such as an editing time, a number of revisions or an earlier date.

Want nothing traceable in the file, for example for a document that goes outside? Set **Document properties** to
**Empty** in the Studio (Output), or `dq config zet uitvoer.metadata leeg`. Then author, last modified by, title,
subject, keywords, comments, company, manager and the program stay empty in Word, and title and author stay empty
in the PDF. Nothing is filled in instead.

## Does it cost anything?

DutchQuill itself is free (MIT). It runs in Claude Code, so you use your own Claude subscription or API credit.

## My PDF doesn't look like my Word file

Without LibreOffice DutchQuill makes the PDF through your browser, in its own layout. With APA on, that PDF still has
the title page (course, supervisor, student number), a table of contents, page numbers and the APA line spacing,
but no page numbers in the table of contents. Install LibreOffice (free) for a PDF that looks exactly like the Word
file. `dq doctor` shows which route you have and how to install LibreOffice.

## Does it work on Windows?

Yes. The tests run on Windows, macOS and Linux. On Windows you need Python 3.10 or later, or uv.

## Does it work in English?

Yes. Set the language to English or `auto` (DutchQuill then follows the language of your material). The guides for
humanizing and style exist in both languages, `dq tells` reports in the language of the text, and the Studio has an
English version. The APA rules and academic style are aimed at Dutch higher education.

## How do I keep DutchQuill up to date?

Type `/plugin` in Claude Code and choose update for DutchQuill. What changed per version is in the
[CHANGELOG](../../CHANGELOG.md) (Dutch). You check the reference guides separately with `/dutchquill:bijwerken`; you
get a reminder for that once a month.

## How do I remove DutchQuill?

Type `/plugin` in Claude Code, choose DutchQuill and remove it. Your workspace stays; it's yours. DutchQuill's Python
environment is in the plugin's data folder, under `~/.claude/plugins/data/`; you can delete that folder afterwards.

## I'm coming from v1

Version 1 was a folder you opened in Claude Code. Version 2 is a plugin. Your old folder keeps working as it was.
Bring your reports along by putting them in the new workspace (`1-input/reports/`), and fill in your student details
with `/dutchquill:instellen`.

## Something doesn't work

Run `dq doctor` and open an [issue](https://github.com/nickyjacobs/DutchQuill-AI/issues/new/choose) with the output.
Remove anything private first.
