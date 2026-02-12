# Architecture

## Overview
This repository uses a published LlamaCloud agent as the primary extraction path, with local schema fallback only when agent execution is unavailable.

## Components
1. **Input Upload Layer**
   - Python CLI receives local file path.
   - Laravel API receives multipart upload, validates file, and stores temporary file.
2. **Runner Layer**
   - Laravel command `llama:extract-invoice` executes Python script.
   - Runner service captures command output and returns JSON.
3. **LlamaExtract Layer**
   - Official Python SDK (`llama-cloud-services`) loads the published agent (`Nota Fiscal`).
   - Fallback path uses local `schema.json` + `llama-cloud` `ExtractConfig`.
4. **Schema Contract (`schema.json`)**
   - Single source of truth for output shape.
   - Enforces cents as integers and ISO dates.
5. **Examples**
   - Input placeholder folder.
   - Output sample for deterministic contract understanding.

## Data Flow
1. Upload
2. Laravel Runner
3. Python Extract Script
4. Llama Agent
5. JSON Normalization
6. Persistencia/Response

Detailed behavior:
1. File is uploaded (CLI path or Laravel multipart).
2. Laravel stores file in `storage/app/tmp` and invokes command runner.
3. Python script tries `extractor.get_agent(name="Nota Fiscal")` and `agent.extract(file)`.
4. If agent path fails, script logs fallback mode and runs schema extraction.
5. Normalizer fixes key format (trim + accent-safe + snake_case style).
6. DTO validates final payload and API returns normalized JSON.
7. Temporary files are removed.

## Production Considerations
- Keep all monetary fields as cents.
- Validate and sanitize file uploads.
- Use queue workers/background jobs for large batches.
- Enforce schema validation before persistence.
- Do not assume undocumented HTTP endpoints; prefer official SDK runner when endpoint contract is unknown.
