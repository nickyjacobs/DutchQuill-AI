<p align="right"><b>🇬🇧 English</b> · <a href="../nl/handleiding/templates.md">🇳🇱 Dutch</a></p>

# Templates

DutchQuill has two kinds: a **Word template** decides how a Word or PDF file looks, a **template per kind of text**
decides what goes into that kind of text.

## Word templates

Built in:

| Template | For |
|---|---|
| `apa-hbo` | APA 7 the way Dutch universities of applied sciences want it: title page, table of contents, hanging indent in the reference list, figure and table labels |
| `zakelijk` (business) | Reports and documents for work |
| `notitie` (note) | Short pieces, process documents |

**Your own house style:** put a .docx in `templates/` in your workspace, or upload it in the Studio. DutchQuill checks
which styles it contains (Normal, Heading 1 to 5, Caption, List Bullet, Bibliography) and translates Dutch style names
("Kop 1") by itself. If something is missing, the check says what.

**Adjusting without Word:** just say it ("headings in Arial 14, dark blue") or use the "Adjust a template" block in the
Studio. DutchQuill makes a copy with your font, colours, line spacing and margins, and leaves the original alone.

**PDFs:** with LibreOffice (free) the PDF is an exact copy of the Word file. Without LibreOffice DutchQuill makes the
PDF through Chrome or Edge, in its own clean layout, or as a last resort in a simple layout. `dq doctor` shows which
route you have.

## Templates per kind of text

There are twelve: email, LinkedIn post, other social post, short text, report (hbo), research report, advisory report,
business report, process document (SOP), research note, memo and README. A template describes the structure: which
parts belong in an email or an SOP, and in which order.

Making your own version:

- **In the Studio:** Templates → Templates per kind of text → Adjust, or Upload (.md or .txt).
- **Yourself:** put a file `templates/genres/<kind>.md` in your workspace.

Your template wins over the built-in one. **Back to default** restores the built-in template and keeps your own
version in `templates/genres/oud/`.
