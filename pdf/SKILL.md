---
name: pdf
description: Extract text from PDFs with automatic OCR fallback. Use when user wants to read a PDF, extract text from a PDF, or convert PDF to text.
argument-hint: <path-to-pdf> [--force-ocr] [--chunk N]
---

# PDF Text Extraction Skill

Extract text from PDFs with automatic OCR fallback.

## Usage

```
/pdf <path-to-pdf> [--force-ocr] [--chunk <lines>] [--topic <topic-name>]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<path>` | Yes | Path to PDF file |
| `--force-ocr` | No | Use OCR even if text extraction works (for garbled PDFs) |
| `--chunk <N>` | No | Split into N-line chunks |
| `--topic <name>` | No | Create research metadata (requires research project structure) |

## How It Works

1. **Try `pdftotext`** first (fast, for digital PDFs)
2. **If empty/minimal output** → automatically fall back to OCR
3. **If `--force-ocr`** → skip pdftotext, go straight to OCR
4. **If >2000 lines** → auto-chunk into 500-line files

## Instructions for Claude

When user invokes `/pdf`:

**Step 1: Check for project script**
```bash
ls scripts/pdf-to-text.js 2>/dev/null && echo "exists" || echo "not found"
```

**Step 2a: If script exists (research project)**
```bash
node scripts/pdf-to-text.js "<path>" data/extracted [options]
```

**Step 2b: If no script (standalone)**
```bash
pdftotext -layout "<path>" "<path>.txt"
```
Then use Read tool to check output. If empty, inform user OCR requires `tesseract.js` setup.

**Step 3: Report results**
- Method used (pdftotext or OCR)
- Output file path and size
- Line count
- Chunk files created (if any)
- Preview first 30 lines

## Examples

```
/pdf paper.pdf                           # Basic extraction
/pdf scan.pdf --force-ocr                # Force OCR for scanned doc
/pdf big.pdf --chunk 400                 # Custom chunk size
/pdf paper.pdf --topic attribution_theory # With research metadata
```

## Standalone Mode

Works without research project structure. Output goes to same directory as input PDF, or `data/extracted/` if it exists.
