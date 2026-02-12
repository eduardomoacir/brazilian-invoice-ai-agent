# Submission Checklist (LlamaAgents Contest / Document Agent Olympics)

## Required
- [ ] Public GitHub repository.
- [ ] Clear project explanation in `README.md`.
- [ ] Reproducible run instructions (Python CLI at minimum).
- [ ] `schema.json` committed and documented.
- [ ] Input/output examples included.
- [ ] Link to LlamaCloud project or agent reference (`AGENT_ID` or `AGENT_NAME`).
- [ ] Screenshots of LlamaCloud UI and extraction result in README.
- [ ] Local demo command documented and tested.

## Strongly Recommended
- [ ] Add short demo video (optional but valuable).
- [ ] Add architecture notes and security notes.
- [ ] Include API integration examples for at least one backend stack.
- [ ] Keep non-primary integrations clearly marked as optional.

## Pre-Submission Validation
- [ ] Remove secrets from code and git history.
- [ ] Confirm README commands run as documented.
- [ ] Validate output sample against `schema.json`.
- [ ] Confirm no real customer invoices are committed.
- [ ] Confirm license file exists (MIT).
- [ ] Run Python demo command: `python integration/python/extract_invoice.py --file examples/input/sample.pdf --agent-name "Nota Fiscal"`
- [ ] (Optional) Run Laravel command demo: `php artisan llama:extract-invoice storage/app/tmp/sample.pdf --agent-name="Nota Fiscal" --json`
