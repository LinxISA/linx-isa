#!/usr/bin/env python3
"""Fail when removed pre-v0.56 ISA surfaces leak into active canonical content."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

ALLOWED_EXTS = {'.adoc','.c','.cc','.cpp','.h','.hpp','.json','.md','.opc','.py','.S','.s','.sh','.yaml','.yml','.decode','.txt','.ll','.mir'}
REJECT_PATTERNS = [
    ('legacy B.IOTI descriptor', re.compile(r'\bB\.IOTI\b')),
    ('legacy B.ATTR descriptor', re.compile(r'\bB\.ATTR\b')),
    ('legacy TCOPY mnemonic', re.compile(r'\bTCOPY\b')),
    ('legacy zero-based tile register', re.compile(r'\b[TMUN]#0\b')),
    ('legacy fixed tile capacity range', re.compile(r'512B\.\.4KB|512B-4KB|\[512B,\s*4KB\]')),
    ('active v0.3 profile reference', re.compile(r'v0\.3|isa/v0\.3|docs/reference/examples/v0\.3|linxisa-v0\.3|uop_classification_v0\.3')),
    ('active v0.4 profile reference', re.compile(r'v0\.4|isa/v0\.4|docs/reference/examples/v0\.4|linxisa-v0\.4|uop_classification_v0\.4|check_canonical_v04')),
]

SKIP_PARTS = {
    '.git','__pycache__','node_modules','vendor','build','site',
    'out','out-linx32','out-linx64','_roundtrip_probe',
    'compiler/llvm','emulator/qemu','kernel/linux','rtl/LinxCore','tools/pyCircuit','lib/glibc','lib/musl','workloads/pto_kernels','skills/linx-skills'
}
SKIP_FILES = {'check_canonical_v056.py'}
ARCHIVE_PREFIXES = (
    'docs/bringup/plan/',
    'docs/releases/',
    'docs/architecture/research/',
    'docs/architecture/isa-manual/vendor/',
)
SUBMODULE_ACTIVE_PREFIXES = (
    'kernel/linux/Documentation/linxisa/',
    'kernel/linux/tools/linxisa/',
)

ACTIVE_TARGETS = [
    'AGENTS.md',
    'README.md',
    'mkdocs.yml',
    'isa',
    'docs/README.md',
    'docs/index.md',
    'docs/architecture',
    'docs/architecture/isa-manual/src',
    'docs/reference',
    'docs/bringup',
    'kernel/README.md',
    'kernel/linux/Documentation/linxisa',
    'kernel/linux/tools/linxisa',
    'avs',
    'tools/isa',
    'tools/bringup',
    'tools/regression',
    'tools/model/CMakeLists.txt',
    'tools/model/README.md',
    'tools/model/docs',
    'tools/model/tools',
]


def should_skip(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    if path.name in SKIP_FILES:
        return True
    if any(rel.startswith(prefix) for prefix in ARCHIVE_PREFIXES):
        return True
    if any(rel.startswith(prefix) for prefix in SUBMODULE_ACTIVE_PREFIXES):
        return False
    return any(part in rel.split('/') for part in SKIP_PARTS) or '/build/' in rel or '/vendor/' in rel


def iter_files(root: Path) -> Iterable[Path]:
    for rel in ACTIVE_TARGETS:
        t = root / rel
        if not t.exists():
            continue
        if t.is_file():
            if t.suffix in ALLOWED_EXTS and not should_skip(t, root):
                yield t
            continue
        for p in t.rglob('*'):
            if p.is_file() and p.suffix in ALLOWED_EXTS and not should_skip(p, root):
                yield p


def check_spec(root: Path) -> list[str]:
    errors: list[str] = []
    spec_path = root / 'isa/v0.56/linxisa-v0.56.json'
    if not spec_path.is_file():
        return [f'missing canonical spec: {spec_path}']
    spec = json.loads(spec_path.read_text())
    mnems = {str(i.get('mnemonic')) for i in spec.get('instructions', [])}
    for banned in ['B.IOTI','B.ATTR','TCOPY']:
        if banned in mnems:
            errors.append(f'{spec_path}: banned mnemonic remains in canonical catalog: {banned}')
    for required in ['B.IOT','B.CATR','B.DATR','BSTART.TMOV']:
        if required not in mnems:
            errors.append(f'{spec_path}: required v0.56 mnemonic missing: {required}')
    tile = root / 'isa/v0.56/registers/tile_reg.json'
    if tile.is_file():
        obj = json.loads(tile.read_text())
        if obj.get('count') != 64 or obj.get('depth_per_hand') != 16:
            errors.append(f'{tile}: expected count=64 and depth_per_hand=16')
        names = {e.get('name') for e in obj.get('entries', [])}
        for name in ['T#16','U#16','M#16','N#16']:
            if name not in names:
                errors.append(f'{tile}: missing {name}')
        for name in ['T#0','U#0','M#0','N#0']:
            if name in names:
                errors.append(f'{tile}: banned zero-based tile name remains: {name}')
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    args = ap.parse_args()
    root = Path(args.root).resolve()
    errors = check_spec(root)
    for path in iter_files(root):
        text = path.read_text(encoding='utf-8', errors='replace')
        rel = path.relative_to(root)
        for label, pat in REJECT_PATTERNS:
            for m in pat.finditer(text):
                line = text.count('\n', 0, m.start()) + 1
                errors.append(f'{rel}:{line}: {label}: {m.group(0)!r}')
                break
    if errors:
        for e in errors[:200]:
            print(e, file=sys.stderr)
        if len(errors) > 200:
            print(f'... {len(errors)-200} more', file=sys.stderr)
        return 1
    print('OK')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
