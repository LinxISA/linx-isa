# LinxISA v0.4 (DRAFT)

This folder is the working area for **LinxISA v0.4** architectural changes.

Rules for this repo state (per project direction):
- **Do not modify v0.3** documents/contracts while drafting v0.4.
- All new/changed semantics required by the rendering + GPGPU architecture are captured here first.
- Once the rendering architecture draft stabilizes, we will propose a controlled upgrade path from v0.3 → v0.4.

## What goes here
- New or revised architectural contracts.
- Deltas relative to v0.3 (control-flow, SIMT kernel bodies, memory path, etc.).
- Rendering pipeline requirements that drive ISA changes.

## What does *not* go here
- Machine-generated artifacts (JSON catalogs, generated instruction tables) until the draft is ready to be promoted.

## Index
- `notes/v0.4-deltas.md` — high-level list of planned semantic changes vs v0.3
- `notes/simt-kernel-body-controlflow.md` — proposed rules for SIMT kernel bodies with group-level control flow
- `rendering/arch-overview.md` — rendering + AI unified GPGPU architecture notes (v0.4-driven)
