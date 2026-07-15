# AI Workload Bring-up Flow

This is the canonical hard-break loop for maturing LinxISA AI workloads until
QEMU-passing Linx ELFs also run in the C++ `tools/LinxCoreModel` target.

Machine-readable flow:

- `docs/bringup/ai_workload_bringup_flow.json`

Runner:

```bash
python3 tools/bringup/run_ai_workload_flow.py --profile smoke --dry-run
python3 tools/bringup/run_ai_workload_flow.py --profile smoke --run-id <run-id>
```

Artifacts are written under:

```text
workloads/generated/<run-id>/ai-bringup/
```

## Profiles

- `smoke`: Tier 0. Bounded AVS PTO parity/tile smoke plus minimal SuperNPUBench tileop cases.
- `pr`: Tiers 0-1. Adds standalone PTO catalog smoke harnesses, PTO kernel compile/static checks, AVS PTO parity model-prefix coverage, the full AVS PTO QEMU parity row, and promoted SuperNPUBench tileop API/control smoke cases.
- `nightly`: Tiers 0-3. Adds matrix, memory, reduction, accelerator, and DeepSeek/model-oriented cases.
- `full`: Tiers 0-4. Full AI workload matrix, including the full AVS PTO parity LinxCoreModel closure target.

Use `--tier`, `--kind`, `--case`, and `--limit` to narrow local debugging.
By default `--case` is a substring filter across case id, suite, and kind.
Prefix the selector with `=` for exact matching, for example
`--case '=supernpu-tileop_api-TAdds'`.
Use `--clang`, `--clangxx`, `--lld`, `--qemu`, `--model-root`, or `--gfsim`
when testing an external lane. The pin lane defaults to in-repo Linx LLVM,
`emulator/qemu/build-linx/qemu-system-linx64`, and
`tools/LinxCoreModel/bin/gfsim`.

Timeouts are lane-specific: `--model-build-timeout` gates CMake configure/build
and generated model-smoke ELF compilation, while `--model-timeout` gates
`gfsim -f <elf>` smoke and workload runs. Non-dry runs rebuild
`tools/LinxCoreModel/bin/gfsim` unless `--skip-model-build` is passed. The
runner configures `gfsim` with `-DOPT_LEVEL=O3 -DDISABLE_DEBUG_SYMBOLS=ON` so
model workload probes use the optimized bring-up binary by default.

## Stage Order

1. `source-contract`: validate PTO catalogs, SuperNPUBench manifests, source paths, hashes, and normalized case records.
2. `compiler-contract`: compile with `compiler/llvm/build-linxisa-clang/bin`, produce ELF/object/asm evidence, and run static checks.
3. `qemu-execution`: run compiler-passing executable cases in Linx QEMU and capture logs/digests.
4. `model-build-smoke`: rebuild or locate `tools/LinxCoreModel/bin/gfsim`, then run a known tiny Linx smoke ELF. By default the runner generates `cases/_model/linx-model-smoke.{cpp,ld,elf}`; `--model-smoke-elf` can override it.
5. `linxcoremodel-execution`: run only QEMU-passing ELFs through `gfsim -f <elf>`.
   On model failures, the runner parses the `gfsim` log for finisher writes,
   assertion text, UART breadcrumbs, and the latest periodic BROB head progress
   so the failure packet names the repeated BPC, terminal marker, or last
   source-level progress marker directly. When the last BROB BPC is available,
   the runner also emits a focused objdump window around that address so
   model-lane packets link runtime progress to compiler output.
6. `differential-triage`: compare QEMU/model digest evidence when both sides emit it.
7. `fix-packets`: emit bounded agent packets for the first failing owner.
8. `skill-doc-evolution`: write an explicit `skill-evolve` update/no-update closeout.

The runner stops on the first red hard-break stage unless
`--continue-on-fail` is set.

## Case Types

- `avs_pto`: executable AVS direct-boot PTO/tile suites. These produce
  `linx-qemu-tests.elf` through `avs/qemu/run_tests.py`; only rows marked
  model-eligible are promoted into `gfsim`.
  Once the executable AVS ELF exists, rows preserve objdump disassembly, symbol,
  section, and relocation sidecars for triage.
  Tier-0 PTO parity is the bounded `avs-pto-parity-smoke` case, which passes
  `-DPTO_PARITY_TLOAD_STORE_ONLY=1` through the AVS extra-cflag hook and runs
  only the `tload_store` digest path. The full smoke-sized parity sequence
  remains `avs-pto-parity` in Tier 1 as a QEMU parity maturity target, but it is
  intentionally not model-eligible in the PR lane. The mirrored Tier-4
  `avs-pto-parity-full-model` row owns final full-row LinxCoreModel closure and
  must stay red until the full sequence passes plain `gfsim -f <elf>`.
  Tier 1 also includes `avs-pto-parity-prefix-gemm-performance`, which uses
  deterministic bit-pattern F32/FP16 seeds plus
  `PTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_GEMM_PERFORMANCE` to prove the
  matmul/GEMM prefix through QEMU and `gfsim` before later float-helper-heavy
  stages are mature. The promoted post-GEMM prefix is
  `avs-pto-parity-prefix-flash-attention`, which stops after
  `PTO_PARITY_STAGE_FLASH_ATTENTION` and proves the current model-green boundary
  reaches the `flash_attention` digest. The next hard-break proof is
  `avs-pto-parity-prefix-flash-attention-softmax`, which stops after
  `PTO_PARITY_STAGE_FLASH_ATTENTION_SOFTMAX` and uses opt-in
  `PTO_ATTENTION_*` plus `PTO_FLASH_TILE_*` micro-shape flags to keep the
  prefix model-runnable. Current evidence proves source, compiler, QEMU,
  model-smoke, and plain `gfsim -f <elf>` through the
  `flash_attention_softmax` digest. The 2x bridge case
  `avs-pto-parity-prefix-flash-attention-softmax-2x` uses the same stop point
  with `PTO_ATTENTION_*` set to `2` and `PTO_FLASH_TILE_*` set to `1`, proving
  a larger scalar soft-float softmax prefix through QEMU and plain
  `gfsim -f <elf>`. Keep `avs-pto-parity` as the full smoke-sized maturity row;
  do not treat the micro-profiled softmax prefixes as substitutes for full-row
  closure. The promoted masked-attention prefix is
  `avs-pto-parity-prefix-flash-attention-masked`, which stops after
  `PTO_PARITY_STAGE_FLASH_ATTENTION_MASKED` and adds
  `PTO_ATTENTION_MASKED_SMOKE_*` micro-shape flags; current evidence proves it
  through the `flash_attention_masked` digest and plain `gfsim -f <elf>`.
  `avs-pto-parity-prefix-fa-performance` reuses the same 1x attention
  micro-profile, stops after `PTO_PARITY_STAGE_FA_PERFORMANCE`, and is now
  promoted through the `fa_performance` digest and plain `gfsim -f <elf>`.
  `avs-pto-parity-prefix-mla-attention` reuses that 1x attention micro-profile,
  stops after `PTO_PARITY_STAGE_MLA_ATTENTION`, and is promoted through the
  `mla_attention` digest and plain `gfsim -f <elf>`.
  `avs-pto-parity-prefix-flash-attention-cube` adds the
  `PTO_PARITY_FLASH_CUBE_*` and `PTO_FLASH_CUBE_*` 1x controls and is promoted
  through the `flash_attention_cube` digest. The subsequent
  `avs-pto-parity-prefix-flash-attention-vec` adds matching
  `PTO_FLASH_VEC_*` 1x controls and is promoted through the
  `flash_attention_vec` digest. The GQA prefix
  `avs-pto-parity-prefix-gqa` adds matching `PTO_PARITY_GQA_*` and
  `PTO_GQA_SMOKE_*` 1x controls and is promoted through the `gqa` digest
  `0x99D39E00C4C9CE38` under plain `gfsim -f <elf>`.
  `avs-pto-parity-prefix-sparse-attention-local` adds matching
  `PTO_PARITY_SPARSE_*` and `PTO_SPARSE_LOCAL_SMOKE_*` 1x controls and is
  promoted through the `sparse_attention_local` digest
  `0x9A43A000C528D955`. The RMSNorm prefix
  `avs-pto-parity-prefix-rmsnorm` adds matching `PTO_PARITY_RMS_*` and
  `PTO_RMSNORM_SMOKE_*` 1x controls, stops after
  `PTO_PARITY_STAGE_RMSNORM`, and is promoted through the `rmsnorm` digest
  `0x9AA9A100C57F8E3A` plus pass finisher under plain `gfsim -f <elf>`.
  The AVS source exposes stop-after-stage IDs for later PTO parity stages so
  agents can isolate the first red model boundary without changing the full-row
  target. Current full-row evidence reaches `flash_attention_softmax` and times
  out in `flash_attention_demo_f32` soft-float helper code at BROB BPC
  `0x18348` after QEMU pass; classify similar QEMU-passing full-shape timeouts
  as model-owned unless static legality evidence proves otherwise. Earlier
  `tanh` crash, `softmax`
  local-pipe stall, and
  `softmax_inplace` RAS assertion evidence were model BFU/RAS issues, so do not
  relabel QEMU-passing parity failures as benchmark/compiler without newer
  static legality evidence.
  Tier-0 tile smoke uses the AVS compile-smoke source override during QEMU
  execution so it exercises the PTO/QEMU/model handoff before the full tile
  runtime source is green. Keep this case-level smoke separate from
  `model-build-smoke`; the global model smoke must remain a generated tiny ELF
  unless `--model-smoke-elf` is explicitly provided.
- `supernpu`: SuperNPUBench `compile.all` Makefile cases compiled with
  `PLAT=linx`. The runner passes a per-case `OBJ_ROOT` under
  `cases/<case>/compiler/supernpu-output/`, links these as direct-boot Linx
  ELFs with `_start` first at `0x10000`, and copies the canonical ELF,
  objdump outputs, raw bin, and linker script into the compiler artifact
  directory for QEMU/model triage. Each `compile.all` case row must be a
  concrete `make` command; do not leave shell-loop variables such as
  `${num_col}` or `${debug}` in rows consumed by the runner. When `TESTCASE` is generic, such as
  `kernel/gemm/matmul TESTCASE=matmul`, the source contract resolves concrete
  sources from `TYPE` first (`A16W4.cpp`, `HiF4_HiF4.cpp`, etc.) and preserves
  actual path casing in source manifests. Current direct-boot green tileop cases are
  `MatMul`, `MatMul_e4m3`, `MatMacc`, `test_MatMul`, `test_MatMacc`, `TAdd`,
  `TAbs`, `TCI`,
  `TCopyIn`, `TCopyOut`, `TCopy`, `TCvt`, `TExpandCol`, `TExpandRow`,
  `TExpandScalar`, `TReshape`, `TTrans`, `TPad`, `TRowMax`, `TRowMaxExpand`,
  `TRowSum`, `TRowSumExpand`, `TSub`, `TSubs`, `TAdd_mask`, `TAdds`, `TDiv`,
  `TDivs`, `TExp`, `TRem`, `TRecip`, `TSqrt`, `TMul`, `TMuls`, `TMax`, `TMaxs`,
  `TAnd`, `TOr`, `TCmp`, and `kernel/control hashtable_lookup_simt`; keep
  future promotions similarly bounded and prove each exact case through QEMU
  and `gfsim -f <elf>`. `hashtable_lookup_simt` currently has two bounded
  `kNum=16` embedded-data direct smokes over the generated 2048-entry table:
  `LINX_HT_SCAN=1` for the linear-scan fallback and `LINX_HT_DIRECT=1` without
  scan for the real MurmurHash3 initial-slot plus linear-probe path. Keep both
  promoted through QEMU and `gfsim`; the hash/probe case is the regression for
  model W-form logical-right-shift semantics. Keep only these `kNum=16`
  `FOR_GFSIM` control rows in Tier 1. The `kNum=6144` SIMT rows and the SIMD
  `NUM_COL=256/512/1024` rows remain Tier 2 until their large/debug source
  contracts are adapted for Linx direct boot.
  Keep SuperNPUBench control data-object rows with explicit no-op generated
  object targets so redirected `OBJ_ROOT` runs do not rebuild `.s` files with a
  host/default assembler. `MatMacc` is currently a
  bounded `4x4` int64 row-major multiply-accumulate smoke; col-major MatMacc
  has QEMU-pass/model-fail evidence and remains a model-lane maturity packet.
  `test_MatMul` is currently a bounded `4x4` int64 row-major MATMUL smoke;
  its original TileLeft/TileRight/TileAcc plus TCVT float path remains deferred
  until the Linx direct-boot model lane supports that runtime contract.
  `test_MatMacc` is currently a bounded `4x4` int64 row-major MATMUL+MATMACC
  smoke; its original TileLeft/TileRight/TileAcc plus TCVT float path remains
  deferred on the same model-lane runtime contract. `MatMul_e4m3` keeps the
  original FP8 e4m3 conversion, TileLeft/TileRight inputs, TileAcc output, and
  vector-kernel conversion contract for non-Linx builds, but its `__linx`
  direct-boot path is a source-local `4x4` int64 MATMUL smoke with the same
  freestanding `_start`/finisher pattern as neighboring tileop cases. Keep that
  smoke distinct from the existing `MatMul` source so both `tileop_api` and
  `other/tileop_api` manifests remain individually promotable while boxed,
  ACC, and FP8 runtime support matures. `TSqrt` is currently a
  bounded `4x4` int64 perfect-square direct-boot smoke; broader integer and
  floating-point sqrt remain deferred until the model lane has matching
  evidence. `TExp` is currently a bounded `4x4` int64 rounded-exp
  direct-boot smoke using a comparison ladder; float/half exponential and
  compiler-generated constant-table paths remain deferred until the model lane
  has matching evidence. Keep `other/tileop_test` and non-control `kernel/*`
  suites in Tier 2 until their larger shape/source contracts are individually
  promoted; keep `kernel/fusion*` rows in Tier 3 because they are model-oriented
  long-shape workloads. SuperNPUBench `kernel/gemm/matmul` `TYPE=A16W4` and
  `TYPE=HIF4_HIF4` currently reach source-contract pass and model-build-smoke pass,
  then fail the compiler-contract as benchmark-owned maturity packets because
  their MX path still depends on vector-only `template_asm.h` `Tr` constraints
  and `blkv_get_*` launch helpers. Do not reclassify these as compiler failures
  unless a Linx direct-boot MX API contract exists and the same source still
  fails in LLVM/MC/link.
- `pto_kernel`: cataloged PTO kernel sources. Most entries currently
  participate in source and compile/static stages only; an ABI-specific
  standalone ELF harness is required before they can enter QEMU/model stages
  individually. Current promoted catalog smokes are `pto-kernel-tload_store`,
  `pto-kernel-gemm`, `pto-kernel-gemm_basic`, `pto-kernel-gemm_demo`,
  `pto-kernel-gemm_performance`, `pto-kernel-gemm_reuse_a_fp16`,
  `pto-kernel-gemm_reuse_b_fp16`, `pto-kernel-gemm_reuse_ab_fp16`,
  `pto-kernel-mamulb`, `pto-kernel-tmatmul_acc`, `pto-kernel-relu_fp32`, and
  `pto-kernel-add_custom` in Tier 1, plus the Tier-2 layout cases
  `pto-kernel-flatten_fp32`, `pto-kernel-reshape_fp32`,
  `pto-kernel-squeeze_fp32`, `pto-kernel-unsqueeze_fp32`,
  `pto-kernel-concat_fp32`, `pto-kernel-split_fp32`,
  `pto-kernel-stack_fp32`, `pto-kernel-permute_nhwc_nchw_fp32`, and
  `pto-kernel-transpose_large_fp32`, plus the Tier-2 indexing cases
  `pto-kernel-slice_fp32`, `pto-kernel-gather_fp32`,
  `pto-kernel-scatter_fp32`, `pto-kernel-where_fp32`,
  `pto-kernel-argmax_fp32`, `pto-kernel-unique_i32`,
  `pto-kernel-hash_table_insert_fp32`,
  `pto-kernel-hash_table_lookup_fp32`, and
  `pto-kernel-unsorted_segment_sum_fp32`: the
  runner generates per-case harnesses, compiles the matching source with
  `-DPTO_QEMU_SMOKE=1`, emits direct-boot Linx ELFs plus objdump/raw-bin side
  artifacts, then promotes each passing ELF through QEMU and
  `gfsim -f <elf>`. The full non-smoke tile paths remain covered by AVS
  parity/model maturity suites until each catalog kernel has its own full-shape
  harness and oracle. `pto-kernel-add_custom` uses a harness-local freestanding
  `__addsf3` helper scoped to the positive integer-valued smoke inputs seeded by
  the oracle, and its oracle-side `f32_bits_from_u32` must fast-path the current
  small smoke range with an exact bit table so `gfsim` does not spend the run in
  harness-only bit-scan loops. Keep that table local to `add_custom`; adding the
  same table to the GEMM copy harness changes its generated `.rodata` access
  pattern and must not be done without rerunning `pto-kernel-gemm_basic` and
  `pto-kernel-gemm_demo`. `pto-kernel-unsorted_segment_sum_fp32` uses the same
  scoped helper for positive integer-valued smoke additions. Do not treat either
  helper as a general compiler-rt replacement.
  `pto-kernel-gemm_basic`, `pto-kernel-gemm_demo`, and
  `pto-kernel-gemm_performance` use float bit-pattern copy-oracle harnesses for
  their `PTO_QEMU_SMOKE` branches; `gemm_performance` keeps `repeat_tiles=3`
  and verifies the final repeat through a precomputed expected-bit table. Treat
  full float TMATMUL/TCVT/TMULS coverage as still owned by later full-shape
  parity/model suites. `pto-kernel-gemm_reuse_a_fp16`,
  `pto-kernel-gemm_reuse_b_fp16`, and `pto-kernel-gemm_reuse_ab_fp16` now have
  direct-boot FP16 storage harnesses with harness-local positive-integer
  `__mulsf3`/`__addsf3` shims. These cases pass source, compiler, QEMU, and
  `gfsim -f <elf>` at the default `PTO_QEMU_SMOKE=1` 16x16x16 shape when the AI
  flow uses `--model-timeout 600`. The PTO sources accept
  `PTO_QEMU_SMOKE_DIM` for controlled future probes, but the runner keeps the
  default 16x16x16 shape because smaller override probes must first prove the
  same QEMU oracle behavior. AVS parity accepts
  `PTO_PARITY_FAST_F32_SEED`, `PTO_PARITY_FAST_FP16_SEED`, and
  `PTO_PARITY_STOP_AFTER_STAGE` only as case-level AI bring-up controls; do not
  make them default AVS behavior without rerunning the QEMU and model parity
  lanes.

## Owner Classification

The first failing boundary assigns the fix lane:

- `benchmark`: source, manifest, API, or workload normalization failure.
  SuperNPUBench compiler-stage logs are still benchmark-owned when they show a
  missing Linx tile API implementation such as `*_Impl`, unsupported Linx tile
  runtime contracts such as vector-kernel syntax, `Tr` asm constraints,
  `blkv_get_*`, or boxed layouts, or
  direct-boot source paths that still depend on host libc/soft-float symbols.
  If a SuperNPUBench `make` invocation exits successfully but no ELF appears,
  inspect the compile log before assigning compiler ownership: stale data-object
  assembly paths that still target `linx64v5`, or source manifests that still
  require missing benchmark-only headers such as `benchmark.h`, are
  benchmark/source-contract failures. SuperNPUBench `compile.all` rows that
  contain unexpanded shell variables are also benchmark/source-contract failures,
  because the AI flow treats those rows as machine-readable case manifests.
- `compiler`: clang, LLVM backend, MC, link, entry symbol, relocation, or retired-token static failure.
- `emulator`: legal compiler output fails under QEMU.
- `model`: QEMU-passing ELF fails to build, load, decode, execute, or match digest evidence in `gfsim`.
  For scalar or vector select divergence around `csel`/`psel`, the model must
  match the LLVM/QEMU contract: `SrcP != 0` selects `SrcR`; `SrcP == 0` selects
  `SrcL`. For `kernel/control hashtable_lookup_simt`, QEMU-passing MurmurHash3
  probe loops that fail only in `gfsim` should first check W-form scalar
  arithmetic, especially `SRLW`/`SRLIW`: use `SrcL[31:0]`, a 5-bit shift
  amount, and sign-extend the 32-bit result.
- `docs-skills`: the run exposes a reusable contract, command, or triage rule not covered by docs/skills.

Each failed case gets a JSON packet under `fix-packets/` with owner, evidence,
repro command, logs, artifacts, and expected next boundary.

## Required Evidence

Every run emits:

- `manifest.json`: tool paths, submodule SHAs, profile/tiers, selected cases.
- `report.json`: per-stage and per-case machine-readable status.
- `summary.md`: human triage table.
- `skill_evolution.{json,md}`: explicit skill closeout.
- `cases/<case>/...`: source hashes, compile logs, ELF/object/asm, objdump,
  optional raw bin, QEMU log, model log, and fix packet links when relevant.
  Model execution rows also carry parsed diagnostics when available:
  `finisher_value`, `finisher_status`, `assertion`, `uart_count`, `uart_tail`,
  `last_brob_bpc`, `last_retired_blocks`, `last_brob_head`,
  `last_brob_bpc_disasm`, and `last_brob_bpc_window`.
- `cases/_model/`: CMake logs plus generated model-smoke source, linker script,
  ELF, compile log, and `gfsim` smoke transcript.
