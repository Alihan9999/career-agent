const { mdToPdf } = require('md-to-pdf');
const path = require('path');
const fs = require('fs');

const inputFile = process.argv[2];
if (!inputFile) {
  console.error('Usage: node to-pdf.js <path-to-markdown-file>');
  process.exit(1);
}

const outputFile = inputFile.replace(/\.md$/, '.pdf');

const resumeCss = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #1a1a1a;
    padding: 0.55in 0.6in;
    max-width: 100%;
  }

  /* Name — top of resume */
  h1 {
    font-size: 20pt;
    font-weight: 700;
    letter-spacing: -0.3px;
    margin-bottom: 3px;
    color: #000;
  }

  /* Contact line under name */
  h1 + p {
    font-size: 9pt;
    color: #444;
    margin-bottom: 14px;
    border-bottom: 1.5px solid #000;
    padding-bottom: 8px;
  }

  /* Section headers */
  h2 {
    font-size: 10pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #000;
    margin-top: 13px;
    margin-bottom: 5px;
    border-bottom: 0.75px solid #bbb;
    padding-bottom: 2px;
  }

  /* Job title / project name */
  h3 {
    font-size: 10.5pt;
    font-weight: 600;
    color: #000;
    margin-top: 7px;
    margin-bottom: 1px;
  }

  /* Dates / subtitle line (italics after h3) */
  h3 + p em, h3 + p {
    font-size: 9pt;
    color: #555;
    margin-bottom: 3px;
    font-style: italic;
  }

  /* Bullets */
  ul {
    margin: 3px 0 4px 0;
    padding-left: 14px;
  }

  li {
    font-size: 10pt;
    margin-bottom: 2px;
    line-height: 1.4;
  }

  /* Skills / bold label lines */
  p strong:first-child {
    font-weight: 600;
  }

  p {
    font-size: 10pt;
    margin-bottom: 3px;
    line-height: 1.4;
  }

  hr {
    display: none;
  }

  a {
    color: #1a1a1a;
    text-decoration: none;
  }

  @page {
    size: Letter;
    margin: 0;
  }
`;

const coverLetterCss = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.65;
    color: #1a1a1a;
    padding: 0.9in 0.85in;
    max-width: 100%;
  }

  p { margin-bottom: 14px; }
  hr { border: none; border-top: 1px solid #ccc; margin: 18px 0; }

  h1, h2, h3 { font-size: 11pt; font-weight: 600; margin-bottom: 4px; }

  @page {
    size: Letter;
    margin: 0;
  }
`;

const isCoverLetter = inputFile.includes('cover-letter');
const css = isCoverLetter ? coverLetterCss : resumeCss;

(async () => {
  try {
    const pdf = await mdToPdf(
      { path: inputFile },
      {
        stylesheet: [],
        body_class: [],
        css,
        pdf_options: {
          format: 'Letter',
          printBackground: false,
          margin: { top: '0', right: '0', bottom: '0', left: '0' },
        },
        launch_options: { args: ['--no-sandbox'] },
      }
    );

    fs.writeFileSync(outputFile, pdf.content);
    console.log(`✓ PDF saved: ${outputFile}`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
})();
