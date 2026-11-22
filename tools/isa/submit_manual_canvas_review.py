#!/usr/bin/env python3
"""Submit an independent cold read to the official Silicon Canvas review loop."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import anyio
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from review_manual_canvas_figure import checked


async def submit(args) -> None:
    independent = json.loads(args.review.read_text(encoding="utf-8"))
    server = StdioServerParameters(
        command=str(args.mcp.resolve()),
        args=[],
        env={"SILICON_CANVAS_OUTPUT_DIR": str(args.artifacts.resolve())},
    )
    async with stdio_client(server) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            decision = checked(
                await session.call_tool(
                    "silicon_submit_review",
                    {
                        "artifact_id": args.artifact_id,
                        "figure_id": args.figure_id,
                        "attempt": args.attempt,
                        "cold_read": independent["cold_read"],
                        "aesthetic": independent["aesthetic"],
                        "host_findings": json.loads(args.host_findings),
                    },
                )
            )
    args.output.write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--figure-id", default="overview")
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--host-findings", default="[]")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    anyio.run(submit, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
