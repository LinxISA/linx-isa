// LinxISA architectural state (skeleton).
// TODO: define register files, PC/TPC, CARG/BARG, privilege state, and exceptions.
//
// NOTE: In the staged bring-up model we keep execute semantics growing while state/exception
// wiring is still under construction. Provide minimal stubs so the Sail project remains
// syntactically complete, but do NOT guess behavior.

// GPR/ClockHands accessors (stubs).
function read_reg5(r : bits(5)) -> bits(64) = {
  unimplemented("read_reg5");
  0x0000_0000_0000_0000
}

function write_regdst(RegDst : bits(5), v : bits(64)) -> unit = {
  unimplemented("write_regdst")
}

// Temporary PC (TPC) accessors (stub).
function read_tpc() -> bits(64) = {
  unimplemented("read_tpc");
  0x0000_0000_0000_0000
}

function write_tpc(v : bits(64)) -> unit = {
  unimplemented("write_tpc")
}

// PC/TPC-unified accessor for PC-relative instructions (ADDTPC/SETRET).
// In strict v0.3 the base is "current instruction PC/TPC" depending on context.
function read_pc_or_tpc() -> bits(64) = {
  unimplemented("read_pc_or_tpc");
  0x0000_0000_0000_0000
}

// Block-control predicate / commit-argument (BARG.CARG) update (stub).
function set_commit_argument(v : bits(64)) -> unit = {
  unimplemented("set_commit_argument")
}

// Block next-target selector (BARG.TGT) update (stub).
// SETC.TGT / C.SETC.TGT select the register-based target for RET/IND-class transitions.
function set_commit_target_reg(r : bits(5)) -> unit = {
  unimplemented("set_commit_target_reg")
}

function read_commit_argument() -> bits(64) = {
  // Legacy/staged name: commit-argument / block-control predicate domain.
  unimplemented("read_commit_argument");
  0x0000_0000_0000_0000
}

// Vec engine predicate register (p). In strict v0.3, `B.Z`/`B.NZ` consult this
// predicate domain when executed in the vec engine scalar lane.
function read_predicate_p() -> bits(64) = {
  unimplemented("read_predicate_p");
  0x0000_0000_0000_0000
}



// Trap raising (stubs). In a complete model these update TRAPNO/TRAPARG0/ECSTATE
// and transfer control. In staged bring-up we keep these as explicit markers.
function raise_trap(trapnum : bits(6), cause : bits(24), traparg0 : bits(64), bi : bits(1)) -> unit = {
  unimplemented("raise_trap")
}

// -----------------------------------------------------------------------------
// BLOCK_TRAP / E_BLOCK helpers (v0.3 bring-up contract)
//
// Normative sources:
// - docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc
// - docs/bringup/plan/isa_clarifications.md
//
// TRAPNUM major class:
//   BLOCK_TRAP = 5
// E_BLOCK cause space:
//   EC_CFI      = 0x1 (with EC_CFI_KIND in CAUSE[3:0])
//   EC_BLOCKFMT = 0x2
//   EC_BFETCH   = 0x3
//
// NOTE: The manual defines EC and subcause fields within TRAPNO.CAUSE. The Sail model
// passes a single 24-bit `cause` to raise_trap(). We pack it as:
//   cause[15:8] = EC_* (E_BLOCK subcause class)
//   cause[7:0]  = detail/subcause (for EC_CFI: CAUSE[3:0]=EC_CFI_KIND, CAUSE[7:4]=0)
// This matches the documented low-bit requirements and keeps the encoding explicit.

function trapnum_block_trap() -> bits(6) = { to_bits(6, 5) }

function e_block_cause(ec : bits(8), detail : bits(8)) -> bits(24) = {
  // Zero-extend into the 24-bit TRAPNO.CAUSE field.
  let c16 : bits(16) = (ec << 8) | detail;
  0x000000 | c16
}

function trap_block_cfi(ec_cfi_kind : bits(4), src_pc_or_tpc : bits(64)) -> unit = {
  // E_BLOCK(EC_CFI) is precise, BI=0, TRAPARG0=source PC/TPC.
  // detail[3:0]=kind, detail[7:4]=0.
  let detail : bits(8) = 0x00 | ec_cfi_kind;
  raise_trap(trapnum_block_trap(), e_block_cause(0x01, detail), src_pc_or_tpc, 0b0)
}

function trap_blockfmt(missing_desc_family : bits(8), missing_detail : bits(8), src_pc_or_tpc : bits(64)) -> unit = {
  // E_BLOCK(EC_BLOCKFMT): BI=0, TRAPARG0 encodes missing/invalid descriptor.
  // Clarifications: TRAPARG0[7:0]=MissingDescFamily, TRAPARG0[15:8]=MissingDetail.
  let traparg0 = (0x0000_0000_0000_0000 | missing_desc_family)
              | (0x0000_0000_0000_0000 | (missing_detail << 8));
  raise_trap(trapnum_block_trap(), e_block_cause(0x02, 0x00), traparg0, 0b0)
}

function trap_bfetch(fault_va : bits(64)) -> unit = {
  // E_BLOCK(EC_BFETCH): BI=1, TRAPARG0=faulting VA.
  raise_trap(trapnum_block_trap(), e_block_cause(0x03, 0x00), fault_va, 0b1)
}

function trap_assert_fail(traparg0 : bits(64)) -> unit = {
  // TRAPNUM_ASSERT_FAIL = 52, CAUSE=0, BI=0
  raise_trap(to_bits(6, 52), to_bits(24, 0), traparg0, 0b0)
}

// ECONFIG (execution config) accessors (stub). In strict v0.3, ECONFIG[3] is the global exception enable.
function read_econfig() -> bits(64) = {
  unimplemented("read_econfig");
  0x0000_0000_0000_0000
}

// Global exception enable (profile-defined). When disabled, ASSERT is treated as a no-op.
function exceptions_enabled() -> bool = {
  read_econfig()[3] == 1b1
}


function trap_sw_breakpoint(traparg0 : bits(64)) -> unit = {
  // TRAPNUM_SW_BREAKPOINT = 50, CAUSE=0, BI=0
  raise_trap(to_bits(6, 50), to_bits(24, 0), traparg0, 0b0)
}

// -----------------------------------------------------------------------------
// Exclusive monitor (LR/SC) - staged model
//
// We approximate ARM-style exclusive monitor with a single local reservation
// tracked at cacheline granularity (64B).
//
// Limitations (staged):
//   - Other cores/agents are not modeled, so conflicting writes are not observed.
//   - Non-exclusive stores in this model do not automatically clear the monitor.

register excl_valid : bool = false
register excl_line  : bits(64) = 0x0000_0000_0000_0000

function excl_line_addr(ea : bits(64)) -> bits(64) = {
  ea & 0xFFFF_FFFF_FFFF_FFC0
}

function excl_set(ea : bits(64)) -> unit = {
  excl_valid = true;
  excl_line = excl_line_addr(ea)
}

function excl_clear() -> unit = {
  excl_valid = false
}

function excl_check(ea : bits(64)) -> bool = {
  excl_valid & (excl_line == excl_line_addr(ea))
}


// Memory accessors (stubs).
// In a complete model these perform translation, permission checks, and fault reporting.
// For staged bring-up we keep them explicit and do not guess the MMU/privilege behavior.

function read_mem8(ea : bits(64)) -> bits(8) = {
  unimplemented("read_mem8");
  0x00
}

function write_mem8(ea : bits(64), v : bits(8)) -> unit = {
  unimplemented("write_mem8")
}
