# WeasyPrint PDF Conversion for NotebookLM Reports

NotebookLM reports download as markdown only. To deliver a styled PDF, convert via weasyprint with a dark-themed HTML wrapper.

## Prerequisites

```bash
pip install weasyprint
# Also verify: which weasyprint
```

## Workflow

1. **Download the report from NotebookLM:**
   ```bash
   notebooklm download report ./report.md
   ```

2. **Create an HTML wrapper** with dark-themed styling appropriate for investment/research briefings. Key design elements:
   - Cover page with gradient background, title, subtitle, metadata
   - Dark theme (#0f0f0f background, #e8e6e3 text, #4dabf7 accent)
   - Styled tables with alternating row colors
   - Callout boxes with left accent border
   - Highlight boxes for key findings
   - Stat cards for metric grids
   - Font: Helvetica Neue or system sans-serif, 10pt body

3. **Key @page rules for professional output:**
   ```css
   @page { margin: 2.2cm 2cm 2.2cm 2cm; size: A4; }
   @page :first { margin-top: 0; }
   ```
   The `:first` page rule gives the cover full-bleed background.

4. **Cover page pattern:**
   ```css
   .cover {
     page-break-after: always;
     display: flex; flex-direction: column; justify-content: center;
     min-height: 100vh;
     background: linear-gradient(...);
   }
   ```
   Note: weasyprint warns about `min-height: 100vh` but still renders it correctly. The warning is cosmetic.

5. **Convert:**
   ```bash
   weasyprint input.html output.pdf
   ```

6. **Verify:**
   ```bash
   file output.pdf    # Should say "PDF document, version 1.7"
   ls -lh output.pdf  # 50-100KB for a 6-10 page briefing
   ```

## Important Notes

- weasyprint ignores `min-height: 100vh` warning but still renders it correctly — safe to ignore
- Tables must use `<table>` with inline `page-break-inside: avoid` to prevent orphans
- The report content from NotebookLM is used as research context — the HTML wrapper reorganizes it with a cover page and proper hierarchy
- For the actual report body, paraphrase/condense the NotebookLM research output into the HTML rather than embedding the raw markdown. The HTML is the canonical document.
- Delivery: include `MEDIA:/absolute/path/to/output.pdf` in the response message

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| "invalid value" warning | `min-height: 100vh` | Cosmetic — PDF still renders correctly |
| Output is 0 bytes | weasyprint not installed or broken | Run `pip install weasyprint --upgrade` |
| Text overflow in table cells | Cell content too long | Reduce font-size in tables to 8-8.5pt |
| Cover page bleeds into content | Missing `page-break-after: always` on cover | Add `page-break-after: always` to `.cover` |
