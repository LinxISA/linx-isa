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

