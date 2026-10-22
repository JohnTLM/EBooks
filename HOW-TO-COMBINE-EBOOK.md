# How to combine the ebook files

The ebook is written in five Markdown files. Combine them in the order below to make one document.

## The files, in order

1. `ebook-assembled-1-front-matter-and-part-I.md`: front matter (Preface, Note on Method, How to Read This Book), then Part I
2. `ebook-assembled-2-part-II.md`: Part II (Chapters 3 to 9)
3. `ebook-assembled-3-part-III.md`: Part III (Chapters 10 to 15)
4. `ebook-assembled-4-part-IV.md`: Part IV (Chapters 16 to 22)
5. `ebook-assembled-5-appendices.md`: Appendices A to D

Each file already has its own title line and a short status line at the top. You can keep them or delete them when combining. Keep the one title at the very top of the combined file.

## Option 1: Combine with PowerShell (Windows)

1. Put all five files in the same folder, for example `website\bonus-articles`.
2. Open PowerShell in that folder: click the address bar in File Explorer, type `powershell`, and press Enter.
3. Run this command:

```powershell
Get-Content -Encoding UTF8 ebook-assembled-1-front-matter-and-part-I.md, ebook-assembled-2-part-II.md, ebook-assembled-3-part-III.md, ebook-assembled-4-part-IV.md, ebook-assembled-5-appendices.md | Set-Content -Encoding UTF8 ebook-combined.md
```

4. The combined file `ebook-combined.md` appears in the same folder.

The `-Encoding UTF8` part matters. Without it, diacritics such as ā, ṃ and ś can be garbled.

## Option 2: Combine with Claude Code

If the five files are in a folder Claude Code can reach, you can ask it:

> Combine these five files in this order into ebook-combined.md, keeping UTF-8 encoding and leaving the content unchanged: ebook-assembled-1-front-matter-and-part-I.md, ebook-assembled-2-part-II.md, ebook-assembled-3-part-III.md, ebook-assembled-4-part-IV.md, ebook-assembled-5-appendices.md

Claude Code can also check that no part is missing and that the headings are in order.

## Option 3: Combine by hand

1. Open each file in a text editor (Notepad, VS Code, or a Word processor).
2. Copy the whole file, then paste it at the end of a new file, in the order above.
3. Save the new file as `ebook-combined.md`, with UTF-8 encoding.

## After combining

- Check that the bridge sentence at the end of each part is followed directly by the next part's heading.
- Check that the status line at the bottom of Part IV is removed or updated.
- Remove the status lines at the top of each file if you don't want them in the final text.
- The "Notes" lines in each chapter are for the author. Remove them before publication.
- The verification record is `verification-log.md`. Its "Still open" section lists anything not yet closed.

The PDF build below does the first four of these for you in the PDF only. `ebook-combined.md` itself is left unchanged.

## Making the PDF

Always make the PDF with `build-ebook-pdf.py`. Don't print the Markdown straight from an editor or browser, and don't use a generic Markdown-to-PDF converter: that is how the earlier PDF ended up with repeated titles, status lines and author notes in the text.

### One-time setup

Install Python 3, then run once in PowerShell:

```powershell
pip install markdown-it-py playwright pypdf
python -m playwright install chromium
```

### Build

1. Combine the five files into `ebook-combined.md` (above).
2. In the same folder, run:

```powershell
python build-ebook-pdf.py
```

3. It writes `the-observer-and-the-taste-of-presence.pdf`, replacing the previous one. It also writes `ebook-print.html`, a preview of the same layout that opens in a browser.
4. The script should print `Wrote the-observer-and-the-taste-of-presence.pdf: N pages, 34 contents entries.` and no warnings. If it warns that a page was not found, a heading has changed form. Check that headings follow the patterns below.

The fonts (Cormorant Garamond and Source Serif 4, the same as the website) load from Google Fonts, so build while online. Offline, the PDF falls back to Georgia.

### What the PDF looks like (the house style)

- Page: 6 × 9 in book trim, page numbers centred in the footer.
- Opening pages: a title page, a copyright page ("Draft edition…"), then the Contents, with dotted leaders and page numbers filled in automatically.
- Each Part opens on its own page with a "PART I" label and the part title. The Appendices get the same kind of page.
- Each chapter, front-matter section and appendix starts on a new page, with a small spaced capital label ("CHAPTER 11", "APPENDIX B") above the title.
- Body text: Source Serif 4 at about 10.4 pt, justified and hyphenated. The first paragraph after a heading is flush left and later paragraphs are indented.
- Headings: Cormorant Garamond.
- Quotes and apostrophes are converted to curly ones (“ ” ’), and diacritics (ā, ṃ, ś) are kept.
- Tables: full width with light rules, the header row repeated if a table runs onto the next page.
- Glossary: hanging indent. References: no bullets, hanging indent.
- Each "Part X: bridge to …" section prints without its heading, as an italic closing passage after a small three-dot divider.

### What the build leaves out of the PDF

These stay in the Markdown but don't print:

- the repeated book title and the "*Assembled draft, step N of 6…*" line at the top of each part
- the `# Front Matter` heading and the `---` separators
- author-only paragraphs: lines starting `*Notes:` or `*Check:`, the italic note under `# Appendices`, and the closing "**Check before publication.**" paragraph. These are kept in `ebook-notes-and-checks.md`. Update that file when you change a chapter's Notes line.

Inline "(check)" marks inside sentences and tables do print, because this is still a draft edition.

### Heading patterns the build relies on

Keep these exact forms in the Markdown so the layout and Contents work:

- `# Part I: The Observer` (a Part, with Roman numerals) and `# Appendices`
- `## Chapter 3: Two Logics`, `## Appendix A: Title`, or a plain `## Preface` for front matter
- `## Part I: bridge to Part II` for the closing passage of a part
- `###` for subheadings inside a chapter

To change the style itself (fonts, sizes, trim), edit the `CSS` block near the top of `build-ebook-pdf.py`. To change the title, author or edition line, edit `TITLE`, `AUTHOR` and `EDITION` there.
