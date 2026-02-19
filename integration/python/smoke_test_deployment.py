#!/usr/bin/env python3
"""Smoke test for deployed Llama workflow endpoint."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a deployment smoke test against Llama workflow API.")
    parser.add_argument(
        "--deploy-url",
        default=os.getenv("LLAMA_DEPLOY_URL", "https://api.cloud.llamaindex.ai/deployments/nota-fiscal-agent-v2"),
        help="Base deployment URL.",
    )
    parser.add_argument("--workflow", default="default", help="Workflow name.")
    parser.add_argument("--file", default="examples/input/sample.pdf", help="File path expected by workflow.")
    parser.add_argument("--agent-name", default=os.getenv("AGENT_NAME", "Nota Fiscal"), help="Published agent name.")
    parser.add_argument("--poll-seconds", type=float, default=2.0, help="Polling interval in seconds.")
    parser.add_argument("--max-polls", type=int, default=45, help="Max poll attempts before timeout.")
    parser.add_argument(
        "--out",
        default="examples/output/out.deploy.test.json",
        help="Output JSON file path (relative to repo root).",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_api_key() -> str:
    load_dotenv(repo_root() / ".env")
    key = os.getenv("LLAMA_CLOUD_API_KEY", "").strip().strip('"')
    if not key:
        raise ValueError("LLAMA_CLOUD_API_KEY is not set.")
    return key


def extract_payload(handler: dict[str, Any]) -> dict[str, Any]:
    result = handler.get("result") or {}
    value = result.get("value")
    if isinstance(value, dict) and isinstance(value.get("result"), dict):
        return value["result"]
    if isinstance(value, dict):
        return value
    raise ValueError("No JSON result payload found in handler response.")


def main() -> int:
    args = parse_args()
    try:
        api_key = load_api_key()
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"start_event": {"file": args.file, "agent_name": args.agent_name}}

    try:
        with httpx.Client(timeout=60.0, headers=headers) as client:
            workflows_resp = client.get(f"{args.deploy_url}/workflows")
            workflows_resp.raise_for_status()
            workflows = (workflows_resp.json() or {}).get("workflows", [])
            if args.workflow not in workflows:
                raise ValueError(f"Workflow not found: {args.workflow}. Available: {workflows}")

            run_resp = client.post(f"{args.deploy_url}/workflows/{args.workflow}/run-nowait", json=payload)
            run_resp.raise_for_status()
            run_obj = run_resp.json() or {}
            handler_id = run_obj.get("handler_id")
            if not handler_id:
                raise ValueError("Missing handler_id in run-nowait response.")

            handler_obj: dict[str, Any] | None = None
            for _ in range(args.max_polls):
                status_resp = client.get(f"{args.deploy_url}/handlers/{handler_id}")
                status_resp.raise_for_status()
                handler_obj = status_resp.json() or {}
                status = handler_obj.get("status")
                if status in {"completed", "failed", "cancelled"}:
                    break
                time.sleep(args.poll_seconds)

            if not handler_obj:
                raise ValueError("No handler response received.")
            if handler_obj.get("status") != "completed":
                raise ValueError(f"Workflow did not complete successfully: {handler_obj.get('status')}")
            if handler_obj.get("error"):
                raise ValueError(f"Workflow returned error: {handler_obj.get('error')}")

            data = extract_payload(handler_obj)
            output_path = (repo_root() / args.out).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

            print(f"ok: workflow={args.workflow}, status=completed")
            print(f"numero_fatura={data.get('numero_fatura')}")
            print(f"cliente={(data.get('cliente') or {}).get('nome')}")
            print(f"saved={output_path}")
            return 0
    except Exception as exc:
        print(f"Error: smoke test failed ({exc.__class__.__name__}): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
