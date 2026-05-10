---
name: "csv-file-preview-function-development"
description: "How to create Python functions for previewing CSV files. Use when the user asks for CSV reading, data preview, inspecting file contents, printing first N rows, handling headers, converting rows to dictionaries, or processing large CSV files. Also trigger on requests for 'quick look at CSV data', 'see the structure of a CSV', 'read CSV without loading everything', 'CSV sample viewer', or any task involving extracting a subset of rows from a CSV file for inspection or debugging."
metadata: { "openclaw": { "emoji": "📊" } }
---

# Develop CSV File Preview Functions

Create a set of Python functions to read and preview the first few rows of a CSV file, with options for different output formats and performance considerations.

## When to use this skill
- When you need to quickly inspect the contents and structure of a CSV file without loading it entirely into memory.
- When you want to provide different output formats for CSV data: raw rows, header-separated output, or dictionary rows.
- When dealing with large CSV files where performance matters and you need efficient preview capabilities.

## Steps
1. **Basic CSV preview with csv.reader**
   - Use Python's built-in `csv` module to read the file and iterate through rows.
   - Why this matters: This is the simplest approach using only the standard library, suitable for small to medium files.

2. **Add header handling**
   - Extract the first row separately as the header before processing data rows.
   - Why this matters: Many CSV files have header rows that describe column names, and separating them makes the output clearer.

3. **Use DictReader for dictionary output**
   - Switch to `csv.DictReader` which automatically uses the first row as field names and yields dictionaries.
   - Why this matters: Dictionary format makes data more accessible by column name and is often more convenient for downstream processing.

4. **Create pandas variant for large files**
   - Use `pandas.read_csv()` with the `nrows` parameter to limit memory usage.
   - Why this matters: Pandas provides better performance for large files, automatic type inference, and handles various CSV quirks more robustly.

5. **Write pytest tests**
   - Create a test that uses temporary files and output capturing to verify the function works correctly.
   - Why this matters: Automated testing ensures the preview functions work as expected and prevents regressions.

## Pitfalls and solutions
❌ **Loading entire large CSV into memory** → This can cause memory issues with big files → ✅ **Use `nrows` parameter in pandas or iterator approach in csv module** to only read the needed rows.

❌ **Not handling missing headers** → If a CSV file has no header row, `next(reader)` will fail → ✅ **Use `next(reader, None)`** which returns None if no more rows are available, allowing graceful handling.

❌ **Forgetting to close files** → This can lead to resource leaks → ✅ **Always use `with open(...)` context manager** which ensures proper file closure even if errors occur.

## Key code and configuration

**Basic CSV preview:**
```python
import csv

def preview_csv(path: str, n: int = 5) -> None:
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i >= n:
                break
            print(row)
```

**With header separation:**
```python
import csv

def preview_csv(path: str, n: int = 5) -> None:
    with open(path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header:
            print('HEADER:', header)
        for i, row in enumerate(reader):
            if i >= n:
                break
            print(row)
```

**Dictionary format with DictReader:**
```python
import csv

def preview_csv_dict(path: str, n: int = 5) -> None:
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= n:
                break
            print(row)
```

**Pandas version for large files:**
```python
import pandas as pd

def preview_csv_pandas(path: str, n: int = 5) -> pd.DataFrame:
    df = pd.read_csv(path, nrows=n)
    print(df)
    return df
```

**Pytest test case:**
```python
import io, csv
from preview import preview_csv

def test_preview_csv_basic(tmp_path, capsys):
    p = tmp_path / 't.csv'
    p.write_text('a,b\n1,2\n3,4\n')
    preview_csv(str(p), n=1)
    out = capsys.readouterr().out
    assert 'a' in out and '1' in out
```

## Environment and prerequisites
- Python 3.6+
- For basic functions: Only Python standard library (`csv` module)
- For pandas variant: `pandas` library installed (`pip install pandas`)
- For testing: `pytest` installed (`pip install pytest`)

## Companion files
- `scripts/preview_functions.py` - Contains all four CSV preview function implementations
- `scripts/test_preview.py` - Pytest test file for verifying the CSV preview functions work correctly