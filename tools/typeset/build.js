const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Header, Footer, AlignmentType, LevelFormat,
  PageNumber, Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  FootnoteReferenceRun, TabStopType,
} = (() => { try { return require('docx'); } catch { return require('/opt/node-tools/node_modules/docx'); } })();

const content = JSON.parse(fs.readFileSync(process.env.CONTENT, 'utf8'));

const FONT = 'Gentium Book Plus';
const BODY = 22;            // 11 pt
const INK = '1A1A1A';
const ACCENT = '5A2A1E';    // deep oxblood for headings
const RULE = 'B8A99A';
const LINE = 288;           // 1.2 line spacing
const INDENT = 340;         // ~0.6 cm first-line indent
const TEXT_W = 9026 - 2 * 0; // A4 width 11906 minus margins (1440 each) = 9026

// ---- inline markup: ***bi***, **b**, *i*, {FN1} ----
function runs(text, base = {}) {
  const out = [];
  let b = false, i = false, buf = '';
  const flush = () => {
    if (buf) out.push(new TextRun({ text: buf, bold: b || base.bold, italics: i !== !!base.italics, ...base.extra }));
    buf = '';
  };
  for (let k = 0; k < text.length;) {
    if (text.startsWith('{FN1}', k)) { flush(); out.push(new FootnoteReferenceRun(1)); k += 5; continue; }
    if (text.startsWith('***', k)) { flush(); b = !b; i = !i; k += 3; continue; }
    if (text.startsWith('**', k)) { flush(); b = !b; k += 2; continue; }
    if (text[k] === '*') { flush(); i = !i; k += 1; continue; }
    buf += text[k]; k += 1;
  }
  flush();
  return out;
}

const children = [];
let prev = null;
let numInstance = 0;

function bodyPara(x, first, keep) {
  return new Paragraph({
    style: 'Body', keepNext: !!keep,
    indent: first ? undefined : { firstLine: INDENT },
    children: runs(x),
  });
}

// ---- title block ----
const titleBlock = content.shift();
const [mainTitle, subTitle] = titleBlock.sub ? [titleBlock.x, titleBlock.sub] : titleBlock.x.split(': ');
children.push(
  new Paragraph({ spacing: { before: 1200, after: 120 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: mainTitle, size: 44, color: ACCENT })] }),
  new Paragraph({ spacing: { after: 360 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: subTitle, italics: true, size: 27, color: INK })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 560 },
    children: [new TextRun({ text: '❧', font: 'DejaVu Serif', size: 28, color: ACCENT })] }),
);

for (const blk of content) {
  switch (blk.t) {
    case 'h1': {
      const m = blk.x.match(/^(\d+)\.\s+(.*)$/);
      const kids = m
        ? [new TextRun({ text: m[1] + '.', color: ACCENT }), new TextRun({ text: '\t' }), ...runs(m[2])]
        : runs(blk.x);
      children.push(new Paragraph({ heading: 'Heading1',
        tabStops: m ? [{ type: TabStopType.LEFT, position: 454 }] : undefined,
        indent: m ? { left: 454, hanging: 454 } : undefined, children: kids }));
      break;
    }
    case 'h2': children.push(new Paragraph({ heading: 'Heading2', children: runs(blk.x) })); break;
    case 'h3': children.push(new Paragraph({ heading: 'Heading3', children: runs(blk.x) })); break;
    case 'p': children.push(bodyPara(blk.x, prev !== 'p', blk.keep)); break;
    case 'bullets':
      blk.items.forEach((it, idx) => children.push(new Paragraph({
        style: 'ListBody', numbering: { reference: 'bullets', level: 0 },
        spacing: { before: idx === 0 ? 100 : 0, after: idx === blk.items.length - 1 ? 160 : 60 }, children: runs(it) })));
      break;
    case 'numbers':
      numInstance += 1;
      blk.items.forEach((it, idx) => children.push(new Paragraph({
        style: 'ListBody', numbering: { reference: 'numbers', level: 0, instance: numInstance },
        spacing: { before: idx === 0 ? 100 : 0, after: idx === blk.items.length - 1 ? 160 : 60 }, children: runs(it) })));
      break;
    case 'gelug_table': {
      const colW = [4513, 4513];
      const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
      const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
      const cell = (txt, head) => new TableCell({
        width: { size: 4513, type: WidthType.DXA },
        shading: head ? { type: ShadingType.CLEAR, fill: 'F1EBE4', color: 'auto' } : undefined,
        margins: { top: 100, bottom: 100, left: 140, right: 140 },
        borders: { top: border, bottom: border, left: none, right: none },
        children: [new Paragraph({ style: head ? 'TableHead' : 'TableBody', children: runs(txt) })],
      });
      children.push(new Paragraph({ style: 'Caption', children: [new TextRun('Table 1. The Gelug distinction on the common basis')] }));
      children.push(new Table({
        width: { size: 9026, type: WidthType.DXA }, columnWidths: colW,
        rows: [
          new TableRow({ tableHeader: true, children: [cell('What Gelug Strictly Negates', true), cell('What Gelug Conventionally Accepts', true)] }),
          new TableRow({ children: [
            cell('An intrinsically established common basis (*gzhi mthun rang bzhin gyis grub pa*): a mind-independent physical substance possessing its own ontological identity prior to perception.'),
            cell('A mere nominal observed basis (*dmigs gzhi tsam* / *snang gzhi tsam*): a dependently designated convergence point where different karmic appearances meet.'),
          ] }),
        ],
      }));
      children.push(new Paragraph({ spacing: { after: 80 }, children: [] }));
      prev = 'table';
      continue;
    }
    case 'diagram':
      blk.lines.forEach((ln, idx) => children.push(new Paragraph({
        style: 'Diagram', keepNext: idx < blk.lines.length - 1,
        shading: { type: ShadingType.CLEAR, fill: 'F6F2EC', color: 'auto' },
        spacing: { before: idx === 0 ? 200 : 0, after: idx === blk.lines.length - 1 ? 220 : 0 },
        children: [new TextRun({ text: ln.length ? ln : ' ' })] })));
      prev = 'diagram';
      continue;
    case 'quote':
      children.push(new Paragraph({ style: 'Quote', children: runs(blk.x) }));
      break;
    case 'table': {
      const n = blk.rows[0].length;
      const first = n === 2 ? 4513 : 1700, rest = Math.floor((9026 - first) / (n - 1));
      const colW = [first, ...Array(n - 1).fill(rest)];
      colW[n - 1] += 9026 - colW.reduce((a, b) => a + b, 0);
      const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
      const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
      const cell = (txt, head, w) => new TableCell({
        width: { size: w, type: WidthType.DXA },
        shading: head ? { type: ShadingType.CLEAR, fill: 'F1EBE4', color: 'auto' } : undefined,
        margins: { top: 90, bottom: 90, left: 110, right: 110 },
        borders: { top: border, bottom: border, left: none, right: none },
        children: [new Paragraph({ style: head ? 'TableHead' : 'TableBody', alignment: AlignmentType.LEFT, children: runs(txt) })],
      });
      if (blk.caption) children.push(new Paragraph({ style: 'Caption', children: [new TextRun(blk.caption)] }));
      children.push(new Table({ width: { size: 9026, type: WidthType.DXA }, columnWidths: colW,
        rows: blk.rows.map((r, ri) => new TableRow({ tableHeader: ri === 0, cantSplit: true,
          children: r.map((t, ci) => cell(t, ri === 0, colW[ci])) })) }));
      children.push(new Paragraph({ spacing: { after: 80 }, children: [] }));
      prev = 'table';
      continue;
    }
    case 'mmk_quote':
      children.push(
        new Paragraph({ style: 'Verse', spacing: { before: 200, after: 40 },
          children: [new TextRun({ text: 'sarvaṃ ca yujyate tasya śūnyatā yasya yujyate', italics: true })] }),
        new Paragraph({ style: 'Verse', spacing: { after: 40 },
          children: [new TextRun('“For whom emptiness is possible, everything is possible.”')] }),
        new Paragraph({ style: 'Verse', spacing: { after: 240 },
          children: [new TextRun({ text: '— ', color: '6B6B6B' }), new TextRun({ text: 'Mūlamadhyamakakārikā', italics: true, color: '6B6B6B', size: 20 }), new TextRun({ text: ' 24.14', color: '6B6B6B', size: 20 })] }),
      );
      break;
  }
  prev = blk.t;
}

const footnoteText = process.env.FN ? process.env.FN : ' While Kant never conceived the thing-in-itself as an empirical efficient cause, and while Prāsaṅgikas accept *arthakriyā* (functional efficacy) only provisionally within unanalyzed worldly convention without adopting Dharmakīrti’s criterion of ultimate reality, the epistemological point holds: a substrate stripped of all relational determinations can provide neither causal purchase nor explanatory leverage.';

const doc = new Document({
  title: process.env.HDR,
  description: process.env.DESC,
  styles: {
    default: { document: { run: { font: FONT, size: BODY, color: INK, language: { value: 'en-GB' } } } },
    paragraphStyles: [
      { id: 'Body', name: 'Body Text', basedOn: 'Normal', quickFormat: true,
        paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { line: LINE, after: 0 } } },
      { id: 'ListBody', name: 'List Body', basedOn: 'Normal',
        paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { line: LINE } } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Body', quickFormat: true,
        run: { font: FONT, size: 30, bold: true, color: ACCENT },
        paragraph: { spacing: { before: 480, after: 200, line: 264 }, keepNext: true, keepLines: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Body', quickFormat: true,
        run: { font: FONT, size: 24, bold: true, color: INK },
        paragraph: { spacing: { before: 320, after: 120, line: 264 }, keepNext: true, keepLines: true, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Body', quickFormat: true,
        run: { font: FONT, size: 22, italics: true, color: ACCENT },
        paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, outlineLevel: 2 } },
      { id: 'TableHead', name: 'Table Head', basedOn: 'Normal',
        run: { bold: true, size: 20, color: ACCENT }, paragraph: { spacing: { line: 252 } } },
      { id: 'TableBody', name: 'Table Body', basedOn: 'Normal',
        run: { size: 20 }, paragraph: { spacing: { line: 264 } } },
      { id: 'Caption', name: 'Caption', basedOn: 'Normal',
        run: { size: 19, italics: true, color: '6B6B6B' }, paragraph: { spacing: { before: 200, after: 100 }, keepNext: true } },
      { id: 'Verse', name: 'Verse Quotation', basedOn: 'Normal',
        run: { size: 23 }, paragraph: { alignment: AlignmentType.CENTER, indent: { left: 720, right: 720 }, keepNext: true, keepLines: true } },
      { id: 'Diagram', name: 'Diagram', basedOn: 'Normal',
        run: { font: 'DejaVu Sans Mono', size: 16, color: '3A3A3A' },
        paragraph: { alignment: AlignmentType.LEFT, indent: { left: 240, right: 240 }, spacing: { line: 220, lineRule: 'exact' }, keepLines: true } },
      { id: 'Quote', name: 'Block Quotation', basedOn: 'Normal',
        run: { italics: true, size: 21 },
        paragraph: { alignment: AlignmentType.JUSTIFIED, indent: { left: 720, right: 720 }, spacing: { before: 160, after: 200, line: 276 } } },
      { id: 'FootnoteText', name: 'footnote text', basedOn: 'Normal',
        run: { size: 18 }, paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { line: 240 } } },
    ],
  },
  numbering: {
    config: [
      { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
          style: { run: { color: ACCENT }, paragraph: { indent: { left: 567, hanging: 283 } } } }] },
      { reference: 'numbers', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
          style: { run: { color: ACCENT }, paragraph: { indent: { left: 567, hanging: 340 } } } }] },
    ],
  },
  hyphenation: { autoHyphenation: true, hyphenationZone: 357, consecutiveHyphenLimit: 2 },
  footnotes: process.env.NOFN ? undefined : { 1: { children: [new Paragraph({ style: 'FootnoteText', children: runs(footnoteText) })] } },
  sections: [{
    properties: {
      titlePage: true,
      page: { size: { width: 11906, height: 16838 }, margin: { top: 1531, bottom: 1474, left: 1440, right: 1440, header: 794, footer: 737 } },
    },
    headers: {
      first: new Header({ children: [new Paragraph({ children: [] })] }),
      default: new Header({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE, space: 4 } },
        children: [new TextRun({ text: process.env.HDR, italics: true, size: 18, color: '6B6B6B' })] })] }),
    },
    footers: {
      first: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '6B6B6B' })] })] }),
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '6B6B6B' })] })] }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(process.env.OUT, buf);
  console.log('ok', children.length, 'blocks');
});
