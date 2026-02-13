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

## LlamaCloud Agent Link
- Agent name: `Nota Fiscal`
- Agent URL: `https://cloud.llamaindex.ai/project/83b51c29-c58e-4476-84d6-79eb6c54b2e9/extract/e73ebcc0-529f-4438-b990-a9e6d4dbbe7b`

## How To Use

### Option A: Quick Start (Recommended for Judges)
Run the Python integration only:

```bash
cd integration/python
pip install -r requirements.txt
python extract_invoice.py --file ../../examples/input/your_invoice.pdf --agent-name "Nota Fiscal"
```

Expected output:
- `examples/output/out.json`

### Option B: LlamaCloud UI
1. Open your LlamaCloud agent (`Nota Fiscal`).
2. Upload a sample invoice document.
3. Run extraction.
4. Compare result with `schema.json` and `examples/output/output.sample.json`.

### Option C: Optional Production Integration
- Python reference: `integration/python/` (primary)
- Laravel 12 wrapper: `integration/laravel/` (optional)

Laravel is intentionally isolated and optional for contest evaluation.

## Demo
Contest demo path (Python-first):

```bash
cd integration/python
pip install -r requirements.txt
python extract_invoice.py --file ../../examples/input/your_invoice.pdf --agent-name "Nota Fiscal"
```

Expected output file:
- `examples/output/out.json`

A reference output is available at:
- `examples/output/output.sample.json`
- `examples/output/output.full.json`

Optional Laravel demo is documented in `integration/laravel/README.md`.

## Repository Contents
- `README.md`: contest-facing explanation and usage.
- `schema.json`: strict JSON Schema for extraction output.
- `examples/input/`: place local test files here (do not commit sensitive docs).
- `examples/output/`: sample output JSON.
- `integration/python/`: official SDK usage with CLI script.
- `integration/laravel/`: optional Laravel 12 integration wrapper.
- `docs/architecture.md`: design and data flow.
- `docs/security.md`: secure production guidance.
- `docs/submission.md`: contest submission checklist.

## Screenshots
Add screenshots before submission (recommended filenames below):
- `docs/assets/screenshots/agent-config.png`: LlamaCloud agent configuration screen.
- `docs/assets/screenshots/extraction-run.png`: extraction run with JSON result.
- `docs/assets/screenshots/source-vs-json.png`: optional side-by-side source vs output.

Example markdown to enable after adding files:

```md
![Agent Config](docs/assets/screenshots/agent-config.png)
![Extraction Run](docs/assets/screenshots/extraction-run.png)
![Source vs JSON](docs/assets/screenshots/source-vs-json.png)
```

## Short Portuguese Section
Este repositorio demonstra extracao de nota fiscal brasileira com LlamaExtract, padronizando datas em ISO e valores monetarios em centavos para uso seguro em producao.

## Contact
- Name: Eduardo Moacir
- Email: desenvolvimento@eduardosites.com.br
- GitHub: https://github.com/eduardomoacir

## License
MIT (`LICENSE`).

