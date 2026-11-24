<p align="right"><b>🇬🇧 English</b> · <a href="../nl/handleiding/aan-de-slag.md">🇳🇱 Dutch</a></p>

# Getting started

From installing to your first document, in about ten minutes.

## 1. Install

You need Claude Code (2.1.275 or later) and Python 3.10 or later, or [uv](https://docs.astral.sh/uv/). In Claude Code,
type:

```text
/plugin marketplace add nickyjacobs/DutchQuill-AI
/plugin install dutchquill@dutchquill
```

Then restart Claude Code. You'll see a one-time notice that DutchQuill hasn't been set up yet.

## 2. Set up

Type `/dutchquill:instellen` ("set up"). You choose how:

- **Visually:** DutchQuill Studio opens in your browser. It's a page on your own computer; nothing goes to the
  internet. See [The Studio](studio.md).
- **In the chat:** Claude asks you a few questions.

The first time, you choose three things: where your [workspace](workspace.md) goes (for example on your desktop),
which [profile](profiles-and-tone.md) suits you, and whether the online language check may be used. Choose English
as the language and the folders get English names. DutchQuill then installs its Python packages in the plugin's data
folder. That takes about a minute and happens only once.

## 3. A short text

Just ask for what you need:

```text
Write a short email to my team lead saying I'd like to take Friday off
```

Emails, posts and short texts appear in the chat. No file is made, unless you say "save it".

## 4. A document

Put your material in `1-input/` in your workspace: notes, a half-finished report, screenshots, PDFs. Then ask, for
example:

```text
/dutchquill:schrijven Make a process document from my notes and screenshots. Deliver it as Word and PDF.
```

This is what happens:

1. Claude shows which material it found and asks what belongs to this task.
2. You first get an outline. It only writes after you agree.
3. The draft goes through the checks that are switched on (language, AI patterns, APA).
4. The result is in `2-output/write/<title>/v1/`: the document in the formats you chose, plus `bron.md` (the
   Markdown source) and `wat-is-er-veranderd.md` (what changed).

Want something changed? Say so ("make the introduction shorter"). That becomes `v2` in the same folder, in the same
formats. `v1` stays.

## 5. Check that everything works

In a terminal, from the plugin folder or through Claude:

```text
dq doctor
```

`dq doctor` shows which Python runs, whether all packages are there, where your workspace is and how PDFs are made.
If it shows a tip about LibreOffice, your PDF doesn't look exactly like your Word file right now. With LibreOffice
(free) it does.

## Next

- [Your workspace](workspace.md): which folder is for what and how versions work.
- [Humanizing](humanizing.md): what DutchQuill does about AI patterns, and what it doesn't.
- [FAQ](faq.md): privacy, PDFs, Windows, removing it.
