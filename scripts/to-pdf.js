const puppeteer = require('puppeteer');
const { marked } = require('marked');
const fs = require('fs');

const inputFile = process.argv[2];
if (!inputFile) {
  console.error('Usage: node to-pdf.js <path-to-markdown-file>');
  process.exit(1);
}

const outputFile = inputFile.replace(/\.md$/, '.pdf');
const isCoverLetter = inputFile.includes('cover-letter');

// Letter paper at 96dpi CSS pixels: 8.5in x 11in = 816 x 1056px
const LETTER_WIDTH_PX  = 816;
const LETTER_HEIGHT_PX = 1056;

function buildResumeCss({ padding, lineHeight, sectionGap, bulletGap, skillsLineHeight, projectNameGap }) {
  return `
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: Arial, Helvetica, sans-serif;
      font-size: 10pt;
      line-height: ${lineHeight};
      color: #000;
      padding: ${padding}in 0.75in;
      width: ${LETTER_WIDTH_PX}px;
    }
    h1 {
      text-align: center;
      font-size: 22pt;
      font-weight: bold;
      margin-bottom: 3px;
    }
    h1 + p {
      text-align: center;
      font-size: 9.5pt;
      margin-bottom: ${Math.round(sectionGap * 0.8)}px;
    }
    h2 {
      font-size: 11pt;
      font-weight: bold;
      margin-top: ${sectionGap}px;
      margin-bottom: 3px;
      border: none;
      text-transform: none;
      letter-spacing: 0;
    }
    p {
      font-size: 10pt;
      margin-bottom: 2px;
      line-height: ${lineHeight};
    }
    h2 + p br { display: block; content: ""; }
    h2 + p {
      margin-bottom: 2px;
      line-height: ${skillsLineHeight};
    }
    ul {
      list-style: none;
      padding-left: 18px;
      margin: 2px 0 ${bulletGap}px 0;
    }
    li {
      font-size: 10pt;
      line-height: ${lineHeight};
      margin-bottom: ${Math.max(1, Math.round(bulletGap * 0.4))}px;
      text-indent: -11px;
      padding-left: 11px;
    }
    li::before { content: "● "; font-size: 7.5pt; }
    ul + p { margin-top: ${projectNameGap}px; margin-bottom: 1px; }
    .edu-row { display: flex; justify-content: space-between; font-size: 10pt; }
    a { color: #000; text-decoration: none; }
    hr { display: none; }
  `;
}

const coverLetterCss = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 11pt;
    line-height: 1.65;
    color: #000;
    padding: 0.9in 0.85in;
    width: ${LETTER_WIDTH_PX}px;
  }
  p { margin-bottom: 14px; }
  hr { border: none; border-top: 1px solid #ccc; margin: 18px 0; }
  h1, h2, h3 { font-size: 11pt; font-weight: 600; margin-bottom: 4px; }
`;

const spacingSteps = [
  { padding: 0.60, lineHeight: 1.50, sectionGap: 14, bulletGap: 5, skillsLineHeight: 1.65, projectNameGap: 6 },
  { padding: 0.55, lineHeight: 1.45, sectionGap: 12, bulletGap: 4, skillsLineHeight: 1.60, projectNameGap: 5 },
  { padding: 0.50, lineHeight: 1.40, sectionGap: 10, bulletGap: 4, skillsLineHeight: 1.55, projectNameGap: 5 },
  { padding: 0.45, lineHeight: 1.38, sectionGap:  9, bulletGap: 3, skillsLineHeight: 1.50, projectNameGap: 4 },
  { padding: 0.40, lineHeight: 1.35, sectionGap:  8, bulletGap: 3, skillsLineHeight: 1.45, projectNameGap: 4 },
  { padding: 0.35, lineHeight: 1.32, sectionGap:  7, bulletGap: 2, skillsLineHeight: 1.42, projectNameGap: 3 },
  { padding: 0.30, lineHeight: 1.28, sectionGap:  6, bulletGap: 2, skillsLineHeight: 1.38, projectNameGap: 3 },
];

(async () => {
  const md = fs.readFileSync(inputFile, 'utf8');
  const html = marked(md);

  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    args: ['--no-sandbox'],
  });
  const page = await browser.newPage();

  await page.setViewport({ width: LETTER_WIDTH_PX, height: LETTER_HEIGHT_PX });

  const css = isCoverLetter ? coverLetterCss : null;
  const steps = isCoverLetter ? [null] : spacingSteps;

  let chosenCss = css;
  let chosenStep = null;
  let finalHeight = 0;

  if (!isCoverLetter) {
    for (const step of spacingSteps) {
      const stepCss = buildResumeCss(step);
      await page.setContent(`<html><head><style>${stepCss}</style></head><body>${html}</body></html>`, { waitUntil: 'domcontentloaded' });

      const scrollHeight = await page.evaluate(() => document.body.scrollHeight);
      console.log(`  padding=${step.padding}in lineHeight=${step.lineHeight} → content height: ${scrollHeight}px (limit: ${LETTER_HEIGHT_PX}px)`);

      if (scrollHeight <= LETTER_HEIGHT_PX) {
        chosenCss = stepCss;
        chosenStep = step;
        finalHeight = scrollHeight;
        console.log(`✓ Fits at padding=${step.padding}in, lineHeight=${step.lineHeight}`);
        break;
      }
    }

    if (!chosenCss) {
      const last = spacingSteps[spacingSteps.length - 1];
      chosenCss = buildResumeCss(last);
      chosenStep = last;
      finalHeight = LETTER_HEIGHT_PX;
      console.warn('⚠ Could not fit on 1 page at minimum spacing — content needs to be shortened.');
    }
  }

  // Final render + PDF export
  await page.setContent(`<html><head><style>${chosenCss}</style></head><body>${html}</body></html>`, { waitUntil: 'domcontentloaded' });

  const pdfBuffer = await page.pdf({
    format: 'Letter',
    printBackground: false,
    margin: { top: '0', right: '0', bottom: '0', left: '0' },
  });

  fs.writeFileSync(outputFile, pdfBuffer);
  console.log(`✓ PDF saved: ${outputFile}`);

  // Auto-generate ATS report PDF if this is a resume run
  const outputDir = require('path').dirname(outputFile);
  const atsPath   = require('path').join(outputDir, 'ats-report.md');
  if (!isCoverLetter && fs.existsSync(atsPath)) {
    const atsPage = await browser.newPage();
    const atsMd   = fs.readFileSync(atsPath, 'utf8');
    const atsHtml = marked(atsMd);
    const atsCss  = `
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { font-family: Arial, Helvetica, sans-serif; font-size: 10.5pt; line-height: 1.55; color: #000; padding: 0.65in 0.75in; width: ${LETTER_WIDTH_PX}px; }
      h1 { font-size: 14pt; font-weight: bold; margin-bottom: 6px; }
      h2 { font-size: 11pt; font-weight: bold; margin-top: 14px; margin-bottom: 4px; border-bottom: 1px solid #ccc; padding-bottom: 2px; }
      h3 { font-size: 10.5pt; font-weight: bold; margin-top: 10px; margin-bottom: 2px; }
      p  { margin-bottom: 4px; }
      ul { padding-left: 20px; margin: 4px 0; }
      li { margin-bottom: 3px; }
      table { border-collapse: collapse; width: 100%; margin: 6px 0; }
      td, th { border: 1px solid #ddd; padding: 4px 8px; font-size: 10pt; }
      th { background: #f5f5f5; font-weight: bold; }
      code { background: #f0f0f0; padding: 1px 4px; font-size: 9.5pt; }
      hr { border: none; border-top: 1px solid #ddd; margin: 10px 0; }
      @page { size: Letter; margin: 0; }
    `;
    await atsPage.setContent(`<html><head><style>${atsCss}</style></head><body>${atsHtml}</body></html>`, { waitUntil: 'domcontentloaded' });
    const atsPdf = await atsPage.pdf({ format: 'Letter', printBackground: false, margin: { top: '0', right: '0', bottom: '0', left: '0' } });
    const atsPdfPath = require('path').join(outputDir, 'ats-report.pdf');
    fs.writeFileSync(atsPdfPath, atsPdf);
    await atsPage.close();
    console.log(`✓ ATS report PDF saved: ${atsPdfPath}`);
  }

  await browser.close();

  // Print markdown run report
  const reportDir  = require('path').dirname(outputFile);
  const atsReportPath = require('path').join(reportDir, 'ats-report.md');
  const atsContent    = fs.existsSync(atsReportPath) ? fs.readFileSync(atsReportPath, 'utf8') : null;
  const date          = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  const folderName    = require('path').basename(reportDir);

  const report = [
    `---`,
    `## Resume Generation Report`,
    `**Date:** ${date}`,
    `**Output folder:** \`output/${folderName}/\``,
    ``,
    `### PDF`,
    `| File | Status |`,
    `|---|---|`,
    `| \`resume.pdf\` | ✓ Saved |`,
    `| \`cover-letter.pdf\` | ${fs.existsSync(require('path').join(reportDir, 'cover-letter.pdf')) ? '✓ Saved' : '—'} |`,
    ``,
    isCoverLetter ? '' : [
      `### Layout`,
      `| Setting | Value |`,
      `|---|---|`,
      `| Pages | 1 ✓ |`,
      `| Padding | ${chosenStep ? chosenStep.padding + 'in' : 'min'} |`,
      `| Line height | ${chosenStep ? chosenStep.lineHeight : 'min'} |`,
      `| Content height | ${finalHeight}px / ${LETTER_HEIGHT_PX}px limit |`,
    ].join('\n'),
    ``,
    atsContent ? atsContent : `_No ATS report found in output folder._`,
    `---`,
  ].join('\n');

  console.log('\n' + report);
})();
