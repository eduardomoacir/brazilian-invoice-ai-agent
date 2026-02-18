#!/usr/bin/env python3
"""Extract Brazilian invoice JSON using published LlamaCloud agent with schema fallback."""

from __future__ import annotations

import argparse
import json
import os
import sys
import warnings
from pathlib import Path
from typing import Any, Tuple

from dotenv import load_dotenv
from llama_cloud import ExtractConfig

warnings.filterwarnings("ignore", category=DeprecationWarning)
from llama_cloud_services import LlamaExtract
from sanitizer import sanitize_extracted_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract invoice JSON from a document file.")
    parser.add_argument("--file", required=True, help="Input file path.")
    parser.add_argument(
        "--agent-name",
        default=os.getenv("AGENT_NAME", "Nota Fiscal"),
        help='Published agent name.',
    )
    parser.add_argument(
        "--fallback-schema",
        default="../../schema.json",
        help="Fallback schema JSON path if agent is missing.",
    )
    parser.add_argument("--out", default="examples/output/out.json", help="Output file path.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_path(raw_path: str, base_dir: Path) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def resolve_input_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate
    return (repo_root() / path).resolve()


def load_env_files() -> None:
    script_dir = Path(__file__).resolve().parent
    candidates = [
        repo_root() / ".env",
        script_dir / ".env",
        Path.cwd() / ".env",
    ]
    for env_file in candidates:
        if env_file.exists():
            load_dotenv(env_file, override=False)


def get_run_data(run_obj: Any) -> Any:
    run = run_obj[0] if isinstance(run_obj, list) and run_obj else run_obj
    data = getattr(run, "data", run)
    if hasattr(data, "dict"):
        return data.dict()
    return data


def load_schema_and_config(schema_path: Path) -> Tuple[dict, ExtractConfig]:
    try:
        schema_data = json.loads(schema_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Fallback schema file not found: {schema_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Fallback schema is invalid JSON: {schema_path}") from exc

    data_schema = schema_data.get("dataSchema", schema_data)
    config_data = schema_data.get("config", {})
    config = ExtractConfig(**config_data)
    return data_schema, config


def run_fallback(extractor: LlamaExtract, file_path: Path, fallback_schema_path: Path) -> Any:
    print("Fallback schema mode enabled")
    data_schema, config = load_schema_and_config(fallback_schema_path)
    result = extractor.extract(data_schema, config, file_path)
    return get_run_data(result)


def run_agent_first(extractor: LlamaExtract, file_path: Path, agent_name: str, fallback_schema_path: Path) -> Any:
    print(f"Using agent: {agent_name}")
    try:
        agent = extractor.get_agent(name=agent_name)
        if not hasattr(agent, "extract"):
            raise RuntimeError("Agent object does not support extract().")
        result = agent.extract(file_path)
        return get_run_data(result)
    except Exception:
        return run_fallback(extractor, file_path, fallback_schema_path)


def main() -> int:
    load_env_files()
    args = parse_args()

    if not os.getenv("LLAMA_CLOUD_API_KEY"):
        print("Error: LLAMA_CLOUD_API_KEY is not set.", file=sys.stderr)
        return 1

    input_file = resolve_input_path(args.file)
    if not input_file.exists() or not input_file.is_file():
        print(f"Error: input file not found: {input_file}", file=sys.stderr)
        return 1

    fallback_schema = resolve_path(args.fallback_schema, Path(__file__).resolve().parent)
    output_file = resolve_path(args.out, repo_root())
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        extractor = LlamaExtract()
        raw = run_agent_first(extractor, input_file, args.agent_name, fallback_schema)
        if not isinstance(raw, dict):
            raise ValueError("Extraction output is not a JSON object.")

        normalized = sanitize_extracted_payload(raw)
        subtotal_calculado = sum(
            int(item.get("valor_total_item_centavos", 0))
            for item in normalized.get("itens", [])
            if isinstance(item, dict)
        )
        subtotal_extraido = int(normalized.get("subtotal_itens_centavos", 0))
        if subtotal_calculado != subtotal_extraido:
            print(
                f"Warning: subtotal mismatch (calculated={subtotal_calculado}, extracted={subtotal_extraido})",
                file=sys.stderr,
            )

        output_file.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Saved: {output_file}")
        print(f"Summary: itens={len(normalized.get('itens', []))}, tributos={len(normalized.get('tributos', []))}")
        return 0
    except Exception as exc:
        print(f"Error: extraction failed ({exc.__class__.__name__}): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
