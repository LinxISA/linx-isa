#!/usr/bin/env python3
"""Compile editable manual figures through the real Silicon Canvas MCP."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import anyio
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


TOOL_COMMIT = "7b590daf2217acc5a95d5c40d289d56d91a9fbfc"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_sha(root: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    for path in files:
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def verify_tool(mcp: Path, tool_root: Path) -> dict:
    mcp = mcp.resolve()
    tool_root = tool_root.resolve()
    commit = subprocess.check_output(
        ["git", "-C", str(tool_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if commit != TOOL_COMMIT:
        raise RuntimeError(
            f"Silicon Canvas checkout is {commit}, expected {TOOL_COMMIT}"
        )
    dirty = subprocess.check_output(
        ["git", "-C", str(tool_root), "status", "--porcelain"], text=True
    ).strip()
    if dirty:
        raise RuntimeError("Silicon Canvas checkout is not clean")
    source_package = tool_root / "src" / "silicon_canvas"
    if not source_package.is_dir():
        raise RuntimeError("Silicon Canvas source package is missing")
    first_line = mcp.read_text(encoding="utf-8").splitlines()[0]
    if not first_line.startswith("#!"):
        raise RuntimeError("Silicon Canvas MCP entry point has no interpreter")
    # Keep the venv launcher path: resolving its symlink loses the venv package path.
    interpreter = Path(first_line[2:])
    try:
        probe = subprocess.check_output(
            [
                str(interpreter),
                "-c",
                (
                    "import inspect,json,pathlib,silicon_canvas;"
                    "p=pathlib.Path(inspect.getfile(silicon_canvas)).resolve().parent;"
                    "print(json.dumps({'package':str(p)}))"
                ),
            ],
            text=True,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("MCP interpreter cannot import silicon_canvas") from exc
    installed_package = Path(json.loads(probe)["package"])
    source_files = {
        path.relative_to(source_package).as_posix()
        for path in source_package.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    installed_files = {
        path.relative_to(installed_package).as_posix()
        for path in installed_package.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    if source_files != installed_files:
        raise RuntimeError(
            "Installed Silicon Canvas package file set differs from checkout"
        )
    source_tree_sha256 = tree_sha(source_package)
    installed_tree_sha256 = tree_sha(installed_package)
    if source_tree_sha256 != installed_tree_sha256:
        raise RuntimeError(
            "Installed Silicon Canvas package bytes differ from checkout"
        )
    entry = mcp.read_text(encoding="utf-8")
    if "from silicon_canvas.mcp_server import main" not in entry:
        raise RuntimeError("MCP executable does not invoke silicon_canvas.mcp_server")
    return {
        "repository": "https://github.com/du-du-wang/silicon-canvas",
        "commit": commit,
        "version": "0.7.0",
        "entrypoint": mcp.name,
        "entrypoint_sha256": sha(mcp),
        "package_tree_sha256": source_tree_sha256,
        "package_file_count": len(source_files),
    }


def checked(result) -> dict:
    if result.is_error:
        text = " ".join(getattr(item, "text", "") for item in result.content)
        raise RuntimeError("Silicon Canvas MCP failed: " + text)
    if not isinstance(result.structured_content, dict):
        raise RuntimeError("Silicon Canvas MCP returned no structured content")
    return result.structured_content


async def compile_all(args) -> None:
    args.output.mkdir(parents=True, exist_ok=True)
    tool_identity = verify_tool(args.mcp, args.tool_root)
    records = []
    server = StdioServerParameters(
        command=str(args.mcp.resolve()),
        args=[],
        env={"SILICON_CANVAS_OUTPUT_DIR": str(args.artifacts.resolve())},
    )
    async with stdio_client(server) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            tools = {tool.name for tool in (await session.list_tools()).tools}
            required = {"silicon_prepare", "silicon_compile", "silicon_export"}
            if not required <= tools:
                raise RuntimeError(
                    f"Silicon Canvas tools missing: {sorted(required - tools)}"
                )
            for source_path in args.sources:
                source = json.loads(source_path.read_text(encoding="utf-8"))
                stem = source_path.name.removesuffix(".silicon-canvas.json")
                preparation = checked(
                    await session.call_tool(
                        "silicon_prepare",
                        {
                            "description": source["description"],
                            "settings": source["settings"],
                            "lock_structure": True,
                        },
                    )
                )
                compiled_result = await session.call_tool(
                    "silicon_compile",
                    {
                        "spec": source["spec"],
                        "preparation_id": preparation["preparation_id"],
                        "figure_id": source["figure_id"],
                    },
                )
                compiled = checked(compiled_result)
                if compiled.get("guide_role") != "target_structure" or not compiled.get(
                    "guide_path"
                ):
                    raise RuntimeError(
                        f"{stem}: engineering target guide is unavailable"
                    )
                exported = checked(
                    await session.call_tool(
                        "silicon_export", {"artifact_id": compiled["artifact_id"]}
                    )
                )
                destinations = {
                    "guide": args.output / f"{stem}.silicon-canvas-guide.png",
                    "export": args.output / f"{stem}.silicon-canvas-export.zip",
                    "prompt": args.output / f"{stem}.silicon-canvas-prompt.txt",
                    "caption": args.output / f"{stem}.silicon-canvas-caption.txt",
                }
                shutil.copyfile(compiled["guide_path"], destinations["guide"])
                shutil.copyfile(exported["path"], destinations["export"])
                destinations["prompt"].write_text(compiled["prompt"], encoding="utf-8")
                destinations["caption"].write_text(
                    compiled["caption"], encoding="utf-8"
                )
                records.append(
                    {
                        "name": stem,
                        "source": source_path.name,
                        "source_sha256": sha(source_path),
                        "artifact_id": compiled["artifact_id"],
                        "selected_figure_id": compiled["selected_figure_id"],
                        "guide_role": compiled["guide_role"],
                        "canvas": compiled["canvas"],
                        "assets": {
                            key: {
                                "path": path.name,
                                "sha256": sha(path),
                                "bytes": path.stat().st_size,
                            }
                            for key, path in destinations.items()
                        },
                    }
                )
    provenance = {
        "schema": "linxisa.manual.silicon-canvas.v1",
        "silicon_canvas": tool_identity,
        "linxisa": {
            "tag": "v0.59.1",
            "commit": "d262515b55c727073997c8f4c95261909f2fe8d3",
        },
        "figures": records,
    }
    (args.output / "silicon-canvas-provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp", type=Path, required=True)
    parser.add_argument("--tool-root", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("sources", nargs="+", type=Path)
    args = parser.parse_args()
    anyio.run(compile_all, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
