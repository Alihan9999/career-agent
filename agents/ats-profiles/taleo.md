# ATS Profile: Taleo

Taleo is one of the oldest ATSs and the least forgiving of modern
formatting. DOCX is strongly preferred; PDFs parse with reduced section
accuracy.

## Preferred Format
- **DOCX** (preferred — Taleo's parser was built around .doc/.docx)
- PDF parses but with measurably lower section-extraction accuracy

## Section Order
1. Header (name + contact)
2. Professional Experience
3. Education
4. Technical Skills
5. Projects (if relevant)

(Note: Taleo orders Education before Skills more reliably than other ATSs;
deviate only when the role is highly technical.)

## Banned Constructs
- Tables — Taleo drops them entirely
- Text boxes
- Page headers/footers with contact info — Taleo strips, contact gets lost
- Two-column layouts — Taleo will read the columns top-to-bottom and
  merge them into a single garbled stream
- Images, icons, color
- Non-standard fonts — stick to Arial, Calibri, Times New Roman

## Required Constructs
- Standard section headings exactly: "Experience" or "Work Experience",
  "Education", "Skills" — Taleo's section detector uses literal heading match
- Date format: "MM/YYYY - MM/YYYY" or "Month YYYY - Month YYYY", consistent
- Each role: company name, title, dates, location on separate logical lines
  (Taleo merges multi-piece bold lines unpredictably)

## Keyword Expansion
- Acronym + full term pairs (same set as iCIMS)
- Taleo's keyword scorer is literal and case-insensitive but treats
  punctuation as token boundaries

## Parser Risk Flags
- Hyphens in metrics ("3-5 years", "10-20%") may be read as ranges and
  miscategorized — write "3 to 5 years", "10 to 20 percent"
- Unicode bullet markers fail more often in Taleo than in newer ATSs
