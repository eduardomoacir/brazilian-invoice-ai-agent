# Python Integration

Official primary flow uses the published LlamaCloud agent:

```python
from llama_cloud_services import LlamaExtract

extractor = LlamaExtract()
agent = extractor.get_agent(name="Nota Fiscal")
result = agent.extract(file)
```

## Install

```bash
pip install -r integration/python/requirements.txt
```

## Environment

```bash
export LLAMA_CLOUD_API_KEY="your_key"
export AGENT_NAME="Nota Fiscal"
```

PowerShell:

```powershell
$env:LLAMA_CLOUD_API_KEY="your_key"
$env:AGENT_NAME="Nota Fiscal"
```

## CLI Arguments

- `--file` (required)
- `--agent-name` (default: `Nota Fiscal`)
- `--fallback-schema` (default: `../../schema.json`)
- `--out` (default: `examples/output/out.json`)

## Mode 1 (Recommended): Published Agent

```bash
python integration/python/extract_invoice.py --file examples/input/sample.pdf
```

## Mode 2 (Automatic Fallback): Local Schema

If agent lookup/execution fails, script automatically prints:
- `Using agent: ...`
- `Fallback schema mode enabled`

Then it uses local schema + config with:
- `extractor.extract(data_schema, config, file)`

You can override fallback schema path:

```bash
python integration/python/extract_invoice.py \
  --file examples/input/sample.pdf \
  --fallback-schema schema.json
```

## Soft Consistency Check

The script logs a warning (without failing) when:
- `subtotal_itens_centavos` differs from `sum(itens[].valor_total_item_centavos)`

This is intentional for production safety and contest transparency.
