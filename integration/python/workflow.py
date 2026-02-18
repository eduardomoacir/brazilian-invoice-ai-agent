from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from llama_cloud_services import LlamaExtract
from workflows import Workflow, step
from workflows.events import StartEvent, StopEvent

from .sanitizer import sanitize_extracted_payload


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_input_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate
    return (_repo_root() / path).resolve()


def _extract_run_data(run_obj: Any) -> Any:
    run = run_obj[0] if isinstance(run_obj, list) and run_obj else run_obj
    data = getattr(run, "data", run)
    if hasattr(data, "dict"):
        return data.dict()
    return data


class InvoiceWorkflow(Workflow):
    @step
    async def run_extract(self, ev: StartEvent) -> StopEvent:
        if not os.getenv("LLAMA_CLOUD_API_KEY"):
            raise ValueError("LLAMA_CLOUD_API_KEY is not set.")

        raw_file_path = str(ev.get("file", "")).strip()
        if not raw_file_path:
            raise ValueError("Input 'file' is required.")

        agent_name = str(ev.get("agent_name", os.getenv("AGENT_NAME", "Nota Fiscal"))).strip()
        if not agent_name:
            agent_name = "Nota Fiscal"

        input_file = _resolve_input_path(raw_file_path)
        if not input_file.exists() or not input_file.is_file():
            raise ValueError(f"Input file not found: {input_file}")

        extractor = LlamaExtract()
        agent = extractor.get_agent(name=agent_name)
        if not hasattr(agent, "extract"):
            raise RuntimeError("Agent object does not support extract().")

        result = agent.extract(input_file)
        payload = _extract_run_data(result)
        if not isinstance(payload, dict):
            raise ValueError("Extraction output is not a JSON object.")

        normalized = sanitize_extracted_payload(payload)
        return StopEvent(result=normalized)


invoice_workflow = InvoiceWorkflow()
