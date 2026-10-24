# Programme Spec: Writing Ebooks and Bonus Articles

Follow this spec whenever you write an ebook chapter or a bonus article, or revise one. It describes the method used for the plain-English version of *The Illusion of the Given*.

## 1. The goal

Write in simple, easy-to-understand English **without losing any content or changing any meaning.** A plain version is a translation into everyday words, not a summary. Every argument, qualification and conclusion in the source must still be there.

Writing comes first. Do **not** start citation-checking or reference-verification rounds unless the author asks for one. Keep references light: a name and a text (for example "Candrakīrti, *Entering the Middle Way*", "MMK 24.14") is enough in the body.

## 2. Plain-English style

- Short sentences. One idea per sentence where possible.
- Everyday words first. Introduce a technical term only when the argument needs it, and say what it means in plain words the first time.
- Concrete examples (the bowl of liquid, the tick, the river) carry the argument. Keep them.
- Use headings, short bullet lists and numbered steps to show structure. Use one table at most where a contrast really needs it.
- Keep the author's voice and the article's own conclusions. Do not add new claims, new sources or new sections.
- Keep diacritics (ā, ī, ṃ, ś, ṣ). Use UTF-8 throughout.
- Never label the text as a plain-English version. Do not write "A Plain English Version" (or similar) as the subtitle, in the running header, in the text, or on video title slides. Use the article's own title and subtitle.

## 3. Content must survive: the checklist

Before delivering, compare the plain version with the source section by section and check each of these.

**Nothing dropped**
- Every section and subsection of the source is still present.
- Every objection and its reply is still present (for example the "wet-and-moist" objection).
- Every example, and every name tied to it, is kept: who says it, and in which text.
- Hedges and qualifications are kept: "much as", "on the order of", "in this article's own terms", "the author's working terms". Never harden a hedge into a flat claim. For example, "much as" must not become "exactly like".
- Cautions and caveats are kept: the scope of a claim, the limits of an analogy, the warnings about pure vision.
- The conclusion is complete, with its closing quotation and its last line.

**Meaning not changed**
- Attributions are kept exactly. Do not move a quotation or an example from one thinker to another.
- Negations keep their strength. "Empty" is never softened to "open". "Enables nothing and explains nothing" stays as it is.
- Do not turn a conventional claim into an ultimate one, or the other way round.

## 4. Canon terms that must not drift

These come from the CanonView canon (`JohnTLM/CanonView`, `canon/`). The plain wording is allowed only where the meaning is the same.

| Keep | Do not write |
|---|---|
| empty / emptiness | open, openness (as a property), void-stuff |
| emptiness enables nothing and explains nothing | emptiness makes things possible (as a cause) |
| relations are empty too | relations are what is really real |
| the basis, primordially pure (*ka dag*) | the Ground, a cosmic mind, a starting point |
| display, with nothing behind it | a projection of a hidden mind |
| rigpa: the knowing of the basis | a super-consciousness, a universal mind |
| *thugs rje* (left untranslated) | a single English gloss for it |
| non-implicative negation: nothing put in its place | negation that implies a hidden positive |
| conventional existence does not wait on a present act of designating (canon Part I, point 27) | things exist only while someone is labelling them |
| Mipham accepts self-knowing awareness conventionally (canon Part II, point 7) | Mipham rejects self-knowing awareness outright |

If a passage seems to need a term outside this table, check the canon file before inventing new wording.

## 5. Process

1. Read the full source and the relevant CanonView canon entries.
2. Write the plain version in Markdown, with front matter:
   ```
   ---
   title: "Title"
   subtitle: "Subtitle"
   ---
   ```
   The subtitle is the article's own subtitle, never "A Plain English Version".
   Use `##` for numbered sections, `###` for subsections, `- ` for bullets, `1. ` for numbered lists, `> ` for a block quotation, and a `|` table where needed. Use `*italic*` and `**bold**`.
3. Run the checklist in Section 3. Fix anything lost or shifted.
4. Typeset (Section 6).
5. Look at every page of the PDF (a contact sheet is enough). Check headings, the table, lists, the quotation and the final page.
6. Deliver the PDF, the DOCX and the Markdown source. In the reply, list briefly what was restored or kept. Do not repeat the whole text.
7. Store the files in this repo in the article's folder (for example `intersubjectivity-and-dependent-arising/`). Open a PR to `main` when the author asks.

## 6. Typesetting (house style)

One command:

```
tools/typeset/typeset.sh article.md Output_Name "Running Header"
```

This writes `Output_Name.docx` and `Output_Name.pdf`. It needs `node` with the `docx` package, `python3`, LibreOffice (`soffice`) and `pdfinfo`.

House style, already built into `tools/typeset/`:
- A4 paper. Body text in Gentium Book Plus, 11 pt, justified, 1.2 line spacing, with a first-line indent on paragraphs that follow a paragraph.
- Headings in deep oxblood (`#5A2A1E`). Numbered section headings use a hanging number.
- A centred title, an italic subtitle and a ❧ ornament on the first page.
- An italic running header with a thin rule. Centred page numbers.
- Tables with rules above and below only, and a tinted header row. A two-column table gets equal columns.
- Block quotations indented. ASCII diagrams in DejaVu Sans Mono on a tinted ground.
- Fonts embedded in the DOCX, so it looks the same on any computer. Gentium Book Plus is under the SIL Open Font License.
