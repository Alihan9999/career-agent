// Convert a markdown resume or cover letter to ATS-friendly DOCX.
// Used when the ATS profile (Workday, Taleo) prefers .docx over .pdf.
//
// Usage: node scripts/to-docx.js <path-to-markdown-file>

const fs = require('fs');
const path = require('path');
const { marked } = require('marked');

let HTMLtoDOCX;
try {
  HTMLtoDOCX = require('html-to-docx');
} catch (e) {
  console.error('Missing dependency: html-to-docx');
  console.error('Run: npm install html-to-docx');
  process.exit(2);
}

const inputFile = process.argv[2];
if (!inputFile) {
  console.error('Usage: node to-docx.js <path-to-markdown-file>');
  process.exit(1);
}

const outputFile = inputFile.replace(/\.md$/, '.docx');
const isCoverLetter = inputFile.includes('cover-letter');

// Parser-safe HTML: single column, plain headings, no tables, no two-column,
// no headers/footers. The CSS here intentionally avoids anything an ATS
// parser drops or misreads.
const ATS_SAFE_CSS = `
  body { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; line-height: 1.35; color: #000; }
  h1 { font-size: 18pt; font-weight: bold; margin: 0 0 4pt 0; }
  h1 + p { font-size: 10.5pt; margin: 0 0 12pt 0; }
  h2 { font-size: 12pt; font-weight: bold; margin: 12pt 0 4pt 0; text-transform: none; }
  h3 { font-size: 11pt; font-weight: bold; margin: 8pt 0 2pt 0; }
  p  { font-size: 11pt; margin: 0 0 4pt 0; }
  ul { padding-left: 18pt; margin: 2pt 0 6pt 0; }
  li { font-size: 11pt; margin-bottom: 2pt; }
  strong { font-weight: bold; }
  em { font-style: italic; }
  a { color: #000; text-decoration: none; }
  hr { display: none; }
  table { display: none; }
`;

(async () => {
  const md = fs.readFileSync(inputFile, 'utf8');
  const bodyHtml = marked(md);

  if (/<table[\s>]/i.test(bodyHtml)) {
    console.warn('Warning: markdown contained a <table>. ATS parsers drop tables; rewrite as paragraphs.');
  }

  const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>${ATS_SAFE_CSS}</style></head><body>${bodyHtml}</body></html>`;

  const docxBuffer = await HTMLtoDOCX(html, null, {
    margins: { top: 720, right: 720, bottom: 720, left: 720 }, // 0.5in in twips
    font: 'Arial',
    fontSize: 22, // half-points: 22 = 11pt
    pageSize: { width: 12240, height: 15840 }, // Letter, twips
    orientation: 'portrait',
    title: path.basename(outputFile, '.docx'),
  });

  fs.writeFileSync(outputFile, docxBuffer);
  console.log(`OK DOCX saved: ${outputFile}`);
})().catch((e) => {
  console.error('to-docx failed:', e);
  process.exit(1);
});
