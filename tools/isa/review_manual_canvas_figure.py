#!/usr/bin/env python3
"""Start the official Silicon Canvas review loop for a generated bitmap."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import anyio
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def checked(result) -> dict:
    if result.is_error:
        message = " ".join(getattr(item, "text", "") for item in result.content)
        raise RuntimeError("Silicon Canvas MCP failed: " + message)
    if not isinstance(result.structured_content, dict):
        raise RuntimeError("Silicon Canvas MCP returned no structured content")
    return result.structured_content


async def start_review(args) -> None:
    server = StdioServerParameters(
        command=str(args.mcp.resolve()),
        args=[],
        env={"SILICON_CANVAS_OUTPUT_DIR": str(args.artifacts.resolve())},
    )
    async with stdio_client(server) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            review = checked(
                await session.call_tool(
                    "silicon_review_image",
                    {
                        "artifact_id": args.artifact_id,
                        "figure_id": args.figure_id,
                        "image_path": str(args.image.resolve()),
                    },
                )
            )
    args.output.write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--figure-id", default="overview")
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    anyio.run(start_review, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
