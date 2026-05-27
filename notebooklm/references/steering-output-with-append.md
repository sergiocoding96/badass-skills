# Steering NotebookLM Output with --append

The `--append` flag on `generate report` and `generate slide-deck` lets you inject specific instructions that steer what NotebookLM writes. Without it, the AI chooses its own focus — often the most prominent source rather than the one you care about.

## Usage

```bash
notebooklm generate report --format briefing-doc --append "Write this report specifically for PROJECT X..." --wait
notebooklm generate slide-deck --append "Frame every slide around PROJECT Y..." --wait
```

## Example: Framing a report around your project

From the Lullaby Residences session:
The notebook had deep research sources about North Beach Miami. Without `--append`, the report focused on "Ocean Terrace Residences and the Miami Luxury Real Estate Outlook" — the most prominent source. With `--append`, it produced:

```
--append "Write this report specifically for the LULLABY RESIDENCES project --
a 4-unit duplex development at 7920 Byron Ave, Miami Beach (North Beach).
Each unit is 181.2m² (118.5m² interior + 62.5m² terraces), medium-high quality,
family-oriented. Name the report 'Lullaby Residences — North Beach Market
Intelligence'. Cover: macro Miami Beach market, North Beach transformation &
development pipeline, neighborhood demographics (schools, parks, transit),
comps (Ella, Iris on the Bay, 7200 Collins, Ocean Terrace), and strategic
positioning for Lullaby."
```

Result: A properly scoped report with the correct title, framing, and section structure.

## When to use --append

- **Always** when you have a specific project/product the research should serve
- When the notebook contains multiple topics and you want one focused output
- When the default title doesn't match your use case
- To specify format preferences, section order, or emphasis

## Limitations

- Longer `--append` text increases generation time slightly
- The AI still synthesizes from its sources — `--append` guides but doesn't override factual content
- For slide decks, batch ALL corrections into the initial `--append` — revisions have a ~9/day quota
