"""Build the print PDF of The Observer and the Taste of Presence from ebook-combined.md.

Usage (from this folder):  python build-ebook-pdf.py
Needs:  pip install markdown-it-py playwright pypdf   (then: python -m playwright install chromium)

What it does, so the PDF stays clean:
  - drops the repeated book title and "Assembled draft" status line at the top of each part
  - drops the "# Front Matter" heading and the "---" separators
  - drops author-facing lines (*Notes: ...*, *Check: ...*, the appendices opening note,
    and the closing "Check before publication" paragraph); they stay in the Markdown chapters,
    and verification-log.md records what was confirmed
  - turns each "Part X: bridge to ..." section into an unheaded closing passage
  - converts straight quotes and apostrophes to typographic ones
  - lays out a 6 x 9 in book: title page, copyright page, contents with page numbers,
    part title pages, each chapter on a new page, page numbers in the footer
Outputs: ebook-print.html (for preview) and the-observer-and-the-taste-of-presence.pdf
"""
import html
import re
import sys
from pathlib import Path

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE / "ebook-combined.md"
HTML_OUT = HERE / "ebook-print.html"
PDF_OUT = HERE / "the-observer-and-the-taste-of-presence.pdf"

TITLE = "The Observer and the Taste of Presence"
AUTHOR = "John Tan (Thusness)"
EDITION = "Draft edition, October 2026."

AUTHOR_ONLY = ("*Notes:", "*Check:", "*Appendix A is an index", "**Check before publication.**")


def curly(text):
    """Typographic quotes for text placed in raw HTML (headings), where the typographer does not run."""
    text = re.sub(r'(^|[\s(\[])"', r"\1“", text)
    text = text.replace('"', "”")
    text = re.sub(r"(^|[\s(\[])'", r"\1‘", text)
    return text.replace("'", "’")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def preprocess(md_text):
    """Turn the combined Markdown into Markdown + structural HTML, and collect the contents."""
    lines = md_text.splitlines()
    out, toc = [], []
    in_section = False
    skip_status = False
    i = 0

    def close_section():
        nonlocal in_section
        if in_section:
            out.extend(["", "</section>", ""])
            in_section = False

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        # Repeated book title + its status line at the top of each part file.
        if s == f"# {TITLE}":
            skip_status = True
            i += 1
            continue
        if skip_status and s.startswith("*Assembled draft"):
            skip_status = False
            i += 1
            continue
        if s and not s.startswith("*Assembled draft"):
            skip_status = False

        if s == "# Front Matter" or s == "---":
            i += 1
            continue

        # Author-facing paragraphs.
        if s.startswith(AUTHOR_ONLY):
            i += 1
            while i < len(lines) and lines[i].strip():
                i += 1
            continue

        m_part = re.match(r"^# (Part [IVX]+): (.+)$", s)
        if m_part or s == "# Appendices":
            close_section()
            label, name = (m_part.group(1), m_part.group(2)) if m_part else ("", "Appendices")
            pid = slug(label or name)
            toc.append(("part", pid, label, curly(name)))
            label_html = f'<div class="part-label">{label}</div>' if label else ""
            out.extend(["", f'<section class="part-title" id="{pid}">{label_html}'
                            f"<h1>{html.escape(curly(name), quote=False)}</h1></section>", ""])
            i += 1
            continue

        if re.match(r"^## Part [IVX]+: bridge", s):
            close_section()
            out.extend(["", '<section class="bridge">', '<div class="ornament">·&#8195;·&#8195;·</div>', ""])
            in_section = True
            i += 1
            continue

        m_h2 = re.match(r"^## (.+)$", s)
        if m_h2:
            close_section()
            heading = m_h2.group(1)
            m_num = re.match(r"^((?:Chapter|Appendix) [0-9A-Z]+): (.+)$", heading)
            label, name = (m_num.group(1), m_num.group(2)) if m_num else ("", heading)
            cid = slug(heading)
            extra = " glossary" if "Glossary" in name else " references" if name == "References" else ""
            toc.append(("chapter", cid, label, curly(name)))
            label_html = f'<span class="chapter-label">{label}</span>' if label else ""
            out.extend(["", f'<section class="chapter{extra}" id="{cid}">',
                        f'<h2>{label_html}{html.escape(curly(name), quote=False)}</h2>', ""])
            in_section = True
            i += 1
            continue

        out.append(line)
        i += 1

    close_section()
    return "\n".join(out), toc


def toc_html(toc, pages=None):
    rows = []
    for kind, cid, label, name in toc:
        num = (pages or {}).get(cid, "")
        text = f"{label}. {name}" if (label and kind == "chapter") else (f"{label}: {name}" if label else name)
        rows.append(f'<li class="toc-{kind}"><a href="#{cid}"><span class="toc-text">{html.escape(text, quote=False)}</span>'
                    f'<span class="toc-dots"></span><span class="toc-num">{num}</span></a></li>')
    return '<section class="contents"><h2>Contents</h2><ol>' + "".join(rows) + "</ol></section>"


CSS = """
@page { size: 6in 9in; }
:root { --ink:#191c21; --muted:#5b6068; --rule:#d8d8d0; --accent:#2c3b6b; }
html { -webkit-print-color-adjust: exact; }
body { margin:0; color:var(--ink); background:#fff;
       font-family:'Source Serif 4', Georgia, serif; font-size:10.4pt; line-height:1.5;
       text-align:justify; hyphens:auto; font-kerning:normal;
       font-variant-ligatures: common-ligatures; }
p { margin:0; orphans:2; widows:2; }
p + p { text-indent:1.3em; }
em { font-style:italic; }
a { color:inherit; text-decoration:none; }

.title-page { height:7.3in; display:flex; flex-direction:column; justify-content:center;
              text-align:center; break-after:page; }
.title-page h1 { font-family:'Cormorant Garamond', Georgia, serif; font-weight:600;
                 font-size:32pt; line-height:1.1; margin:0 0 .35in; }
.title-page .rule { width:.8in; height:1px; background:var(--accent); margin:0 auto .35in; }
.title-page .author { font-size:10pt; letter-spacing:.18em; text-transform:uppercase; color:var(--muted); }
.copyright { height:7.3in; display:flex; flex-direction:column; justify-content:flex-end;
             font-size:8.5pt; line-height:1.55; color:var(--muted); text-align:left; break-after:page; }
.copyright p + p { text-indent:0; margin-top:.6em; }

.contents { break-after:page; }
.contents h2 { font-family:'Cormorant Garamond', Georgia, serif; font-weight:600; font-size:20pt;
               margin:.3in 0 .25in; text-align:left; }
.contents ol { list-style:none; margin:0; padding:0; font-size:9.3pt; line-height:1.4; }
.contents li a { display:flex; align-items:baseline; }
.contents .toc-dots { flex:1; border-bottom:1px dotted #9aa0a8; margin:0 .4em; transform:translateY(-.25em); }
.contents .toc-num { min-width:1.6em; text-align:right; font-variant-numeric:oldstyle-nums; }
.contents .toc-part { margin-top:.75em; font-weight:600; break-after:avoid; }
.contents .toc-chapter { padding-left:1em; }
.contents li:first-child { margin-top:0; }

.part-title { break-before:page; break-after:page; text-align:center; padding-top:2.4in; }
.part-label { font-size:9pt; letter-spacing:.25em; text-transform:uppercase; color:var(--accent); margin-bottom:.15in; }
.part-title h1 { font-family:'Cormorant Garamond', Georgia, serif; font-weight:600; font-size:26pt;
                 line-height:1.15; margin:0; }

.chapter { break-before:page; }
.chapter h2 { font-family:'Cormorant Garamond', Georgia, serif; font-weight:600; font-size:21pt;
              line-height:1.15; text-align:left; margin:.55in 0 .3in; hyphens:manual; }
.chapter-label { display:block; font-family:'Source Serif 4', Georgia, serif; font-weight:400;
                 font-size:8.5pt; letter-spacing:.25em; text-transform:uppercase; color:var(--accent);
                 margin-bottom:.12in; }
h3 { font-family:'Cormorant Garamond', Georgia, serif; font-weight:600; font-size:13.5pt;
     line-height:1.2; text-align:left; margin:1.1em 0 .4em; break-after:avoid; hyphens:manual; }
h3 + p, h2 + p { text-indent:0; }
strong { font-weight:600; }

.bridge { margin-top:1.6em; font-style:italic; break-inside:avoid; }
.bridge p { text-indent:0; }
.ornament { text-align:center; font-style:normal; color:var(--accent); font-size:13pt; margin-bottom:.8em; }

table { width:100%; border-collapse:collapse; margin:1em 0; font-size:8.3pt; line-height:1.35;
        text-align:left; hyphens:auto; }
thead { display:table-header-group; }
th { font-weight:600; border-bottom:1px solid var(--ink); padding:.35em .4em; vertical-align:bottom; }
td { border-bottom:.5px solid var(--rule); padding:.35em .4em; vertical-align:top; }
tr { break-inside:avoid; }

ul, ol { margin:.6em 0 .8em; padding-left:1.2em; }
li { margin:.2em 0; }
li p + p { text-indent:0; }
.chapter ul + p, .chapter ol + p, table + p { text-indent:0; }

.glossary p { text-indent:0; padding-left:1.2em; text-indent:-1.2em; margin-bottom:.45em;
              text-align:left; }
.references ul { list-style:none; padding-left:0; }
.references li { padding-left:1.4em; text-indent:-1.4em; text-align:left; font-size:9.3pt; }
.references p { text-indent:0; margin-top:1em; break-after:avoid; }
"""

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&'
         'family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=block">')


def build_html(body, toc, pages=None):
    front = (f'<section class="title-page"><h1>{TITLE}</h1><div class="rule"></div>'
             f'<div class="author">{AUTHOR}</div></section>'
             f'<section class="copyright"><p>{TITLE}. By {AUTHOR}.</p>'
             f'<p>© {AUTHOR}. Free to read and share.</p><p>{EDITION}</p></section>')
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{TITLE}</title>'
            f"{FONTS}<style>{CSS}</style></head><body>{front}{toc_html(toc, pages)}{body}</body></html>")


FOOTER = ('<div style="width:100%;text-align:center;font-family:Georgia,serif;font-size:8pt;color:#5b6068;">'
          '<span class="pageNumber"></span></div>')


def render(page, doc_html):
    HTML_OUT.write_text(doc_html, encoding="utf-8")
    page.goto(HTML_OUT.as_uri(), wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.pdf(path=str(PDF_OUT), width="6in", height="9in", print_background=True,
             display_header_footer=True, header_template="<div></div>", footer_template=FOOTER,
             margin={"top": "0.7in", "bottom": "0.75in", "left": "0.72in", "right": "0.68in"})


def find_pages(toc):
    """Find the page each contents entry starts on, from the rendered PDF."""
    import unicodedata
    from pypdf import PdfReader

    def plain(t):  # compare without accents or curly quotes, which PDF text extraction can mangle
        t = unicodedata.normalize("NFKD", t)
        t = "".join(c for c in t if c.isascii() and not unicodedata.combining(c))
        return " ".join(t.upper().split())

    texts = [plain(p.extract_text() or "") for p in PdfReader(str(PDF_OUT)).pages]
    pages, start = {}, 3  # skip title, copyright and the first contents page
    for kind, cid, label, name in toc:
        for n in range(start, len(texts)):
            head = texts[n][:160].replace(" ", "")
            words = [w for w in plain(name).split() if len(w) > 3][:3] or plain(name).split()[:1]
            if all(w in head for w in words) and (not label or plain(label).replace(" ", "") in head):
                pages[cid] = n + 1
                start = n + 1 if kind == "chapter" else n
                break
    return pages, len(texts)


def main():
    if not SRC.exists():
        sys.exit(f"{SRC.name} not found. Combine the five parts first (see HOW-TO-COMBINE-EBOOK.md).")
    body_md, toc = preprocess(SRC.read_text(encoding="utf-8"))
    md = MarkdownIt("commonmark", {"html": True, "typographer": True}).enable(["table", "smartquotes"])
    body = md.render(body_md)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        render(page, build_html(body, toc, {cid: "000" for _, cid, _, _ in toc}))  # pass 1: measure
        pages, _ = find_pages(toc)
        render(page, build_html(body, toc, pages))                                # pass 2: final
        pages2, total = find_pages(toc)
        browser.close()

    missing = [name for _, cid, _, name in toc if cid not in pages2]
    print(f"Wrote {PDF_OUT.name}: {total} pages, {len(toc)} contents entries.")
    if pages != pages2:
        print("Warning: page numbers shifted between passes; run again.")
    if missing:
        print("Warning: page not found for:", ", ".join(missing))


if __name__ == "__main__":
    main()
