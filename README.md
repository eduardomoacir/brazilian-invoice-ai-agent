# Brazilian Invoice AI Agent (LlamaExtract)

Production-oriented submission repository for the **LlamaAgents Contest / Document Agent Olympics**.

## Problem
Brazilian invoices and fiscal notes (NF-e/NFS-e and similar formats) are often delivered as messy PDFs or scans.
They contain unstructured tables, taxes, and inconsistent number/date formatting, making reliable automation hard.

## Solution
This project uses an existing **LlamaExtract agent** on LlamaCloud (`Nota Fiscal`) with a strict JSON Schema (`schema.json`) to produce normalized invoice JSON.

Core normalization rules:
- All keys are snake_case and ASCII-only (no spaces, no accents).
- All monetary values are `integer` in cents (`*_centavos`).
- All dates are ISO `YYYY-MM-DD`.
- `itens` and `tributos` are always arrays.
- No invented taxes: if missing in source, return `tributos: []`.

## Why Cents Instead of Floats
Currency in floats causes precision and rounding bugs in production.
Using integer cents avoids decimal drift and keeps accounting-safe behavior across Python, PHP, JS, SQL, and BI tools.

## Architecture
High-level flow:
1. User uploads invoice PDF/image.
2. LlamaExtract agent parses and extracts structured fields.
3. Output validated against `schema.json`.
4. Normalized JSON consumed by ERP, finance, or downstream APIs.

Detailed architecture is in `docs/architecture.md`.

## Environment Variables
Set these before running any integration:
- `LLAMA_CLOUD_API_KEY`
- `AGENT_ID` or `AGENT_NAME`

Never commit real API keys.

## How To Use

### Option A: LlamaCloud UI
1. Open your LlamaCloud agent (`Nota Fiscal`).
2. Upload a sample invoice document.
3. Run extraction.
4. Compare result with `schema.json` and `examples/output/output.sample.json`.

### Option B: Programmatic API
- Python example: `integration/python/`
- Laravel 12 example: `integration/laravel/`

Both are designed so API endpoint details can be adjusted in one place.

## Demo
Quick local demo with Python:

```bash
cd integration/python
pip install -r requirements.txt
python extract_invoice.py --file ../../examples/input/your_invoice.pdf --agent-name "Nota Fiscal"
```

Expected output file:
- `examples/output/out.json`

A reference output is available at:
- `examples/output/output.sample.json`

## Repository Contents
- `README.md`: contest-facing explanation and usage.
- `schema.json`: strict JSON Schema for extraction output.
- `examples/input/`: place local test files here (do not commit sensitive docs).
- `examples/output/`: sample output JSON.
- `integration/python/`: official SDK usage with CLI script.
- `integration/laravel/`: Laravel 12 service/controller/request/DTO integration.
- `docs/architecture.md`: design and data flow.
- `docs/security.md`: secure production guidance.
- `docs/submission.md`: contest submission checklist.

## Screenshots
Add screenshots before submission:
- LlamaCloud agent configuration screen.
- Extraction run screen with sample result.
- Optional side-by-side source invoice vs JSON output.

## Short Portuguese Section
Este repositorio demonstra extracao de nota fiscal brasileira com LlamaExtract, padronizando datas em ISO e valores monetarios em centavos para uso seguro em producao.

## License
MIT (`LICENSE`).
