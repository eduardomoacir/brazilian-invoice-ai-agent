# Security Guide

## Secret Management
- Keep `LLAMA_CLOUD_API_KEY` in environment variables or secret manager.
- Never hardcode keys in source code.
- Never log tokens or Authorization headers.
- Never print API keys in exception messages.

## File Upload Security
- Validate MIME type and extension.
- Enforce max file size and request throttling.
- Reject unsupported formats early.
- Use FormRequest validation before any file persistence.

## Data Handling
- Use private storage for temporary files.
- Remove temporary files after extraction completes.
- Avoid storing raw invoices unless required by policy.
- Sanitize filenames and avoid exposing local filesystem paths to clients.

## API and Runtime Hardening
- Add rate limiting on extraction endpoints.
- Use queue workers for expensive extraction calls.
- Add retry/backoff only for transient failures.
- Apply timeouts to external HTTP calls.
- Run Python extractor with controlled command arguments only.
- Handle missing/unavailable agent gracefully and use explicit fallback logic.

## Observability Without Sensitive Data
- Log job ids, status codes, durations, and generic errors.
- Do not log full extracted payload when it can include personal/company data.
- Mask identifiers when debugging in shared environments.

## Compliance Notes
- Respect LGPD and internal retention policies.
- Use sanitized/synthetic docs for public demos.
