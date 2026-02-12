# Laravel 12 Integration

This integration is optional and intended as a production wrapper around the Python extractor.

Laravel uses a safe runner pattern:
1. Validate upload.
2. Store temporary file in `storage/app/tmp`.
3. Execute Python extractor script.
4. Normalize JSON.
5. Return DTO response and cleanup temporary file.

## Published Agent (Primary)

Command:

```bash
php artisan llama:extract-invoice storage/app/tmp/sample.pdf --agent-name="Nota Fiscal"
```

The command executes:

```bash
python integration/python/extract_invoice.py --file storage/app/tmp/sample.pdf --agent-name "Nota Fiscal"
```

## Fallback Schema (Optional)

```bash
php artisan llama:extract-invoice storage/app/tmp/sample.pdf \
  --agent-name="Nota Fiscal" \
  --fallback-schema="schema.json"
```

If the agent cannot be loaded/executed, Python falls back automatically to local schema.

## API Route Example

- `POST /api/extract/invoice` (see `routes_example.php`)

## Environment

```env
LLAMA_CLOUD_API_KEY=your_key
LLAMA_EXTRACT_PYTHON=python3
LLAMA_EXTRACT_SCRIPT=integration/python/extract_invoice.py
AGENT_NAME=Nota Fiscal
```

## Security

- Never log `LLAMA_CLOUD_API_KEY`.
- Validate MIME and file size in `InvoiceExtractRequest`.
- Cleanup temporary files after processing.
- Add Laravel rate limiting middleware to extraction endpoint.
