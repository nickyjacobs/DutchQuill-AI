---
titel: Humanize (English)
module: humaniseren
geldt: when controles.humaniseren is on and the text is English
versie: 1
gecontroleerd: 2026-11-25
data: gidsen/data/tells_en.yaml
bronnen:
  - https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
  - https://github.com/blader/humanizer
  - https://arxiv.org/html/2412.11385v1
  - https://news.linkedin.com/2026/keeping-conversations-real-on-linkedin
---

# Humanize (English)

Make the text read like someone who knows the subject and has something to say wrote it, ideally the user. The
meaning never changes: facts, numbers, names, quotes and sources stay exactly as they are. The word lists live
in `gidsen/data/tells_en.yaml` and drive `dq tells --taal en`; this guide covers what a script cannot see.

## 1. Method

1. **Voice first.** If there is a voice profile (`stemprofiel.md`, `.dutchquill/stem.json`), read it before
   changing anything. What the writer does in their own texts overrides every rule below.
2. **Mark** with `dq tells --taal en --genre <genre>`, then read it yourself.
3. **Rewrite** the strongest patterns first. Leave a good sentence with one weak word alone.
4. **Check** with `dq tells --compare` and `dq feiten`: nothing lost, nothing added. Also check you did not
   overcorrect into a string of short, clipped sentences.
5. **Final read** as the intended reader.

## 2. When not to act

- Text written before December 2022.
- Informal text with a single tell.
- Fixed technical terms ("robust regression", "essential oils").
- The writer's own quirks: odd word choices, asides, mixed feelings. Those are signs of a human.
- Anything inside quotation marks.

## 3. Patterns

### A. Vocabulary (changes by model era)

| Era | Words |
|---|---|
| GPT-4 (2023-2024) | delve, tapestry, testament, underscore, pivotal, intricate, realm |
| GPT-4o (2024-2025) | align with, enhance, showcasing, fostering, serves as, stands as, boasts |
| GPT-5 (2025) | emphasizing, highlighting |
| mid-2026 onward | leverage, multifaceted, quietly, dependable, plus more full stops and shorter sentences |

Strong tells count on sight (delve, tapestry, testament to, seamless, game-changer). Weak tells (crucial,
robust, comprehensive, leverage, insights) only matter in a **cluster**: three or more different ones close
together.

**Avoiding "is"**: "serves as", "stands as", "boasts", "features" where "is" or "has" works.
**Vague connection** (a top sign in 2026): "in connection with", "associated with". Say what the connection is.

### B. Formulas

- **Run-ups**: "In today's fast-paced world", "In an era of", "It's no secret that".
- **Text about the text**: "This article explores", "Let's dive in", "Below is an overview".
- **Empty closers**: "In conclusion", "Ultimately,", "The future looks bright", "Only time will tell",
  "Despite these challenges".
- **Filler**: "It's important to note that", "plays a key role", "a wide range of".
- **Vague authority**: "Experts say", "Studies show" (without the study), "Some argue".
- **Chatbot residue**: "I hope this helps", "Great question", "Certainly!", "Would you like me to", "As of my
  last update", "Based on available information" (2026), "All information has been preserved" (2026).

### C. Structures

- **Negative parallelism**: "It's not just X, it's Y", "not X but Y", "not because X but because Y". Say what
  it is.
- **Rhetorical set-up**: "The result? A faster app." Write the sentence.
- **Rule of three** everywhere. Use two, four or one when that is the real number.
- **Stacked adjectives**: three in a row before one noun ("a robust, scalable and innovative platform"): the
  promotional tone Wikipedia's Signs of AI writing lists for older models (2023-2025). Keep the one that matters, or show why.
- **Inflated significance**: "marks a turning point", "has shaped the discourse", "invaluable".
- **Trailing -ing clause**: "..., highlighting the importance of teamwork." Cut it or make it a claim with
  evidence.
- **Repeated openers** and **connectors** (Moreover, Furthermore, Additionally) starting many sentences.
- **Heading echoed** in the first sentence.

### D. Rhythm

- **Too uniform**: every sentence 15-20 words, every paragraph four sentences.
- **Overcorrected** (new in 2026): clipped. Short. Sentences. Everywhere. Rejoin sentences where the thought
  continues.
- **Elegant variation**: rotating synonyms (the car, the vehicle, the automobile) to avoid repetition is itself
  a tell. Repeating a noun or using "it" is fine.

### E. Formatting

- Em dashes as all-purpose punctuation (weak since 2026, but still worth checking if the writer does not use them).
- Bold scattered through sentences, emoji in headings or bullets, Title Case headings where the style guide
  says sentence case, curly and straight quotes mixed.
- LinkedIn: one-sentence paragraphs ("broetry"), emoji bullet lists, hashtag blocks, the "hook, here's what I
  learned, three bullets, question" template. LinkedIn says it limits reach for posts without original substance.

## 4. What makes text human

- Specifics from the material or the user (names, numbers, dates). **Never invent** an anecdote, example or
  figure; ask, or mark `[example needed]`.
- A position: choose, and say why. Hedge only where there is real uncertainty.
- Plain verbs (is, has, does, says). "There is" is fine.
- Past tense and sequence where the genre allows it: what happened, in what order.
- Some irregularity: a longer sentence that runs on a little, a short reaction, an aside in brackets.

## 5. Score

Same scale as Dutch: points per 1000 words. Strict genres (report, SOP, README, memo): low under 4, medium
4-9. Technical reports (pentest, audit) and loose genres (email, LinkedIn, social, short): low under 6, medium
6-12. Under 100 words the figures are unreliable and `dq tells` says so: read short texts yourself. Aim for low; the number matters
less than whether the strong tells and clusters are gone and the fact check passes.

## 6. About detectors

Detectors measure much the same signals: vocabulary, predictability, rhythm. Independent studies show they
are often wrong, especially for non-native writers. DutchQuill aims at the text, not at a detector score.
If AI was used for coursework, see `gidsen/nl/ai-gebruik.md` (APA format, September 2025) on how to disclose it.
