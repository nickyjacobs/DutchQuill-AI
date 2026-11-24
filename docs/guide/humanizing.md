<p align="right"><b>🇬🇧 English</b> · <a href="../nl/handleiding/humaniseren.md">🇳🇱 Dutch</a></p>

# Humanizing

For DutchQuill, humanizing means making a text sound as if someone wrote it who knows the subject. Usually that's the
writer. The result is a better text: more precise, more personal, more pleasant to read. The content doesn't change.

## What DutchQuill does

- **Your own voice.** Put a few texts you wrote yourself in `my-style/` and click "Measure my voice" in the Studio (or
  ask Claude). The subagent `stem-analist` turns them into a voice profile: sentence length, variety, how you start
  sentences, your punctuation, informal or formal address. What you do yourself wins over any general rule.
- **The AI patterns of 2026,** in Dutch and English: words per model generation, formulas like "not just X, but Y",
  empty openers and closers, vague sources, and overcorrection (too many short, clipped sentences). DutchQuill scores
  clusters, not single words: "crucial" in one sentence isn't a problem.
- **Specific instead of vague.** A general sentence becomes a concrete example from your own material.
- **A fact check.** After every rewrite round `dq feiten` checks that no number, name, date, quote or source has
  disappeared or appeared. DutchQuill makes nothing up; if something is missing, it marks it with `[bron nodig]`
  ("source needed").
- **Thresholds per kind of text.** A LinkedIn post may be lighter than a report; with informal text DutchQuill steps
  in less quickly.

## Measuring it yourself

`dq tells` measures the AI patterns in a text. These are the before and after texts from the README:

![dq tells on the before and after texts](../img/tells-en.gif)

With `--compare original.md new.md` you see before and after side by side, with `--json` the full output. See
[Commands](../reference/commands.md).

## What DutchQuill doesn't do

DutchQuill doesn't promise that a text is "invisible" to AI detectors. It doesn't optimise for detector scores and
doesn't change document metadata to hide anything: no invented editing time, no invented revisions, no backdated
timestamps. A document gets your name as author and the real time it was made.

If you use AI for a study assignment, follow the rules of your programme. DutchQuill helps with the disclosure: citing
AI in the APA format of September 2025, and if you like, an AI disclosure with your report.

## Where the rules come from

The patterns are in `gidsen/nl/humaniseren.md` and `gidsen/en/humanize.md`, the word lists in
`gidsen/data/tells_*.yaml`. Sources: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
[blader/humanizer](https://github.com/blader/humanizer) (MIT) and our own research into Dutch text. How they are kept
up to date: [Guides and sources](../reference/guides-and-sources.md).
