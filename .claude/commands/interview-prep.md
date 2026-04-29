Generate a targeted interview preparation document for a specific company application.

## Input
The user will provide one of:
- A company name: `/interview-prep PayNearMe`
- A full output folder: `/interview-prep PayNearMe-2026-04-27`
- No argument: ask the user which company to prep for

## Steps

1. Find the output folder:
   - If a full folder name was given, use `output/<folder>/`
   - If only a company name was given, find the most recent folder matching that company in `output/`
   - If nothing was given, list available folders in `output/` and ask the user to pick one

2. Read these files from the folder:
   - `job-analysis.json`
   - `company-research.json`
   - `resume.md`

3. Run the **Interview Prep Agent** (`agents/interview-prep.md`) with the loaded context

4. Save the output to `output/<folder>/interview-prep.md`

5. Print a summary to the conversation:
   - Company and role
   - Number of technical questions generated
   - Number of behavioral questions with mapped answers
   - Any Gap Alerts to be aware of

## Notes
- If the output folder does not contain company-research.json, run a quick web search on the company before generating prep
- The document is meant to be read the night before an interview, not during — keep it scannable
- Always check `data/resume.md` (base resume) in addition to the customized `output/.../resume.md` for full experience context
