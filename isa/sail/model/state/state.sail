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
