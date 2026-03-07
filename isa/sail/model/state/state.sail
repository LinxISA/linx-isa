// LinxISA architectural state (skeleton).
// TODO: define register files, PC/TPC, CARG/BARG, privilege state, and exceptions.
//
// NOTE: In the staged bring-up model we keep execute semantics growing while state/exception
// wiring is still under construction. Provide minimal stubs so the Sail project remains
// syntactically complete, but do NOT guess behavior.

$include <prelude.sail>
$include <arith.sail>
$include <vector.sail>
$include "memory.sail"

// -----------------------------------------------------------------------------
// GPR file + PC/TPC (minimal concrete state)
//
// This is enough to run the executable model for unit tests and bring-up.
// Policy: x0 is hard-wired to zero.

register gpr0  : bits(64) = 0x0000_0000_0000_0000
register gpr1  : bits(64) = 0x0000_0000_0000_0000
register gpr2  : bits(64) = 0x0000_0000_0000_0000
register gpr3  : bits(64) = 0x0000_0000_0000_0000
register gpr4  : bits(64) = 0x0000_0000_0000_0000
register gpr5  : bits(64) = 0x0000_0000_0000_0000
register gpr6  : bits(64) = 0x0000_0000_0000_0000
register gpr7  : bits(64) = 0x0000_0000_0000_0000
register gpr8  : bits(64) = 0x0000_0000_0000_0000
register gpr9  : bits(64) = 0x0000_0000_0000_0000
register gpr10 : bits(64) = 0x0000_0000_0000_0000
register gpr11 : bits(64) = 0x0000_0000_0000_0000
register gpr12 : bits(64) = 0x0000_0000_0000_0000
register gpr13 : bits(64) = 0x0000_0000_0000_0000
register gpr14 : bits(64) = 0x0000_0000_0000_0000
register gpr15 : bits(64) = 0x0000_0000_0000_0000
register gpr16 : bits(64) = 0x0000_0000_0000_0000
register gpr17 : bits(64) = 0x0000_0000_0000_0000
register gpr18 : bits(64) = 0x0000_0000_0000_0000
register gpr19 : bits(64) = 0x0000_0000_0000_0000
register gpr20 : bits(64) = 0x0000_0000_0000_0000
register gpr21 : bits(64) = 0x0000_0000_0000_0000
register gpr22 : bits(64) = 0x0000_0000_0000_0000
register gpr23 : bits(64) = 0x0000_0000_0000_0000
register gpr24 : bits(64) = 0x0000_0000_0000_0000
register gpr25 : bits(64) = 0x0000_0000_0000_0000
register gpr26 : bits(64) = 0x0000_0000_0000_0000
register gpr27 : bits(64) = 0x0000_0000_0000_0000
register gpr28 : bits(64) = 0x0000_0000_0000_0000
register gpr29 : bits(64) = 0x0000_0000_0000_0000
register gpr30 : bits(64) = 0x0000_0000_0000_0000
register gpr31 : bits(64) = 0x0000_0000_0000_0000

function read_reg5(r : bits(5)) -> bits(64) = {
  match r {
    0b00000 => 0x0000_0000_0000_0000,
    0b00001 => gpr1,
    0b00010 => gpr2,
    0b00011 => gpr3,
    0b00100 => gpr4,
    0b00101 => gpr5,
    0b00110 => gpr6,
    0b00111 => gpr7,
    0b01000 => gpr8,
    0b01001 => gpr9,
    0b01010 => gpr10,
    0b01011 => gpr11,
    0b01100 => gpr12,
    0b01101 => gpr13,
    0b01110 => gpr14,
    0b01111 => gpr15,
    0b10000 => gpr16,
    0b10001 => gpr17,
    0b10010 => gpr18,
    0b10011 => gpr19,
    0b10100 => gpr20,
    0b10101 => gpr21,
    0b10110 => gpr22,
    0b10111 => gpr23,
    0b11000 => gpr24,
    0b11001 => gpr25,
    0b11010 => gpr26,
    0b11011 => gpr27,
    0b11100 => gpr28,
    0b11101 => gpr29,
    0b11110 => gpr30,
    0b11111 => gpr31
  }
}

function write_reg5(r : bits(5), v : bits(64)) -> unit = {
  match r {
    0b00000 => (),
    0b00001 => gpr1 = v,
    0b00010 => gpr2 = v,
    0b00011 => gpr3 = v,
    0b00100 => gpr4 = v,
    0b00101 => gpr5 = v,
    0b00110 => gpr6 = v,
    0b00111 => gpr7 = v,
    0b01000 => gpr8 = v,
    0b01001 => gpr9 = v,
    0b01010 => gpr10 = v,
    0b01011 => gpr11 = v,
    0b01100 => gpr12 = v,
    0b01101 => gpr13 = v,
    0b01110 => gpr14 = v,
    0b01111 => gpr15 = v,
    0b10000 => gpr16 = v,
    0b10001 => gpr17 = v,
    0b10010 => gpr18 = v,
    0b10011 => gpr19 = v,
    0b10100 => gpr20 = v,
    0b10101 => gpr21 = v,
    0b10110 => gpr22 = v,
    0b10111 => gpr23 = v,
    0b11000 => gpr24 = v,
    0b11001 => gpr25 = v,
    0b11010 => gpr26 = v,
    0b11011 => gpr27 = v,
    0b11100 => gpr28 = v,
    0b11101 => gpr29 = v,
    0b11110 => gpr30 = v,
    0b11111 => gpr31 = v
  }
}

function write_regdst(RegDst : bits(5), v : bits(64)) -> unit = { write_reg5(RegDst, v) }

register pc  : bits(64) = 0x0000_0000_0000_0000
register tpc : bits(64) = 0x0000_0000_0000_0000

function read_tpc() -> bits(64) = { tpc }
function write_tpc(v : bits(64)) -> unit = { tpc = v }

function read_pc_or_tpc() -> bits(64) = {
  // Staged model: treat PC-relative bases as PC.
  pc
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

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
// Vector engine block-local state (staged bring-up)
//
// This models the second-layer (vector block internal) architectural state that is
// visible to vector instructions.

// Vec engine predicate register (p).
// - Block-local, initialized from B.DIM/B.ATTR state on block dispatch.
// - Inactive lanes are typically treated as don't-care by most V.* ops; explicit
//   merge is performed via V.PSEL.
register vec_p : bits(64) = 0xFFFF_FFFF_FFFF_FFFF

function read_predicate_p() -> bits(64) = { vec_p }
function write_predicate_p(v : bits(64)) -> unit = { vec_p = v }

// Decoder-provided helpers for staged block-descriptor execution.
// The decoder/fetch layer must provide the already-decoded immediate/register
// values for B.DIM/B.ATTR. These hooks avoid guessing operand formats here.
function decoded_bdim_index() -> bits(2) = {
  // 0=LB0, 1=LB1, 2=LB2
  unimplemented("decoded_bdim_index");
  0b00
}

function decoded_bdim_value() -> bits(64) = {
  unimplemented("decoded_bdim_value");
  0x0000_0000_0000_0000
}

function decoded_battr_raw() -> bits(64) = {
  // Full 64-bit attribute word as encoded by B.ATTR.
  unimplemented("decoded_battr_raw");
  0x0000_0000_0000_0000
}

// Latched B.ATTR state relevant to VEC bring-up.
register battr_raw : bits(64) = 0x0000_0000_0000_0000
function battr_dr() -> bool = { battr_raw[26] == 0b1 }

// LCFR (core feature) (staged): only LaneNum is currently consulted.
// LaneNum is encoded in LCFR[19:16] and represents log2(vec_length).
// Storage is provided via SSR_ID 0x0024 (ssr_lcfr).
//
// NOTE: Sail requires registers to be declared before use, so we declare the
// small SSR subset needed for vec bring-up here (full SSR block is below).
register ssr_lcfr : bits(64) = 0x0000_0000_0006_0000 // SSR_ID 0x0024 (RO): LaneNum=6 => vec_length=64 (bring-up)
register ssr_lb0  : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0050
register ssr_lb1  : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0051
register ssr_lb2  : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0052

function vec_length_from_lcfr() -> int = {
  let ln : int = unsigned(ssr_lcfr[19..16]);
  shl_int(1, ln)
}

function vec_all1_mask(n : int) -> bits(64) = {
  let ones : bits(64) = 0xFFFF_FFFF_FFFF_FFFF;
  if n >= 64 then ones
  else sail_shiftright(ones, 64 - n)
}

function vec_init_p_for_group(lc1 : bits(64)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lb1_i : int = unsigned(ssr_lb1[31..0]);
  let lb2_i : int = unsigned(ssr_lb2[31..0]);
  if not_bool(battr_dr()) then {
    // DR=0: LB0 is the effective lane_count for this group.
    if lb0_i >= vw then write_predicate_p(vec_all1_mask(vw))
    else write_predicate_p(vec_all1_mask(lb0_i))
  } else {
    // DR=1: strip-mine total iteration space across vec_length.
    let total : int = lb0_i * (if lb1_i == 0 then 1 else lb1_i) * (if lb2_i == 0 then 1 else lb2_i);
    let groups : int = tdiv_int(total + vw - 1, vw);
    let g : int = unsigned(lc1[31..0]);
    let rem : int = tmod_int(total, vw);
    if g == (groups - 1) then {
      if rem == 0 then write_predicate_p(vec_all1_mask(vw)) else write_predicate_p(vec_all1_mask(rem))
    } else {
      write_predicate_p(vec_all1_mask(vw))
    }
  }
}

// -----------------------------------------------------------------------------
// Vector lane register file (staged)
//
// We model vt#0..vt#7 as 64 lanes of 32-bit each, packed in a 2048-bit register.
// Other namespaces (vu/vm/vn) are left for later bring-up.

type vec_reg64x32 = bits(2048)

register vt0 : vec_reg64x32 = sail_zeros(2048)
register vt1 : vec_reg64x32 = sail_zeros(2048)
register vt2 : vec_reg64x32 = sail_zeros(2048)
register vt3 : vec_reg64x32 = sail_zeros(2048)
register vt4 : vec_reg64x32 = sail_zeros(2048)
register vt5 : vec_reg64x32 = sail_zeros(2048)
register vt6 : vec_reg64x32 = sail_zeros(2048)
register vt7 : vec_reg64x32 = sail_zeros(2048)

function read_vt(k : bits(3)) -> vec_reg64x32 = {
  match k {
    0b000 => vt0,
    0b001 => vt1,
    0b010 => vt2,
    0b011 => vt3,
    0b100 => vt4,
    0b101 => vt5,
    0b110 => vt6,
    0b111 => vt7
  }
}

function write_vt(k : bits(3), v : vec_reg64x32) -> unit = {
  match k {
    0b000 => vt0 = v,
    0b001 => vt1 = v,
    0b010 => vt2 = v,
    0b011 => vt3 = v,
    0b100 => vt4 = v,
    0b101 => vt5 = v,
    0b110 => vt6 = v,
    0b111 => vt7 = v
  }
}

function vec_get_lane32(v : vec_reg64x32, lane : int) -> bits(32) = {
  // Sail 0.20: avoid runtime-dependent subrange indexing.
  let lo : int = lane * 32;
  let w : bits(2048) = sail_shiftright(v, lo);
  truncate(w, 32)
}

function vec_set_lane32(v : vec_reg64x32, lane : int, x : bits(32)) -> vec_reg64x32 = {
  // Clear + insert the 32-bit lane using masks + shifts.
  let lo : int = lane * 32;
  let mask32_2048 : bits(2048) = sail_shiftleft(sail_zero_extend(0xFFFF_FFFF, 2048), lo);
  let cleared : bits(2048) = v & not_vec(mask32_2048);
  let ins : bits(2048) = sail_shiftleft(sail_zero_extend(x, 2048), lo);
  cleared | ins
}


// Trap raising (stubs). In a complete model these update TRAPNO/TRAPARG0/ECSTATE
// and transfer control. In staged bring-up we keep these as explicit markers.
// Minimal trap plumbing for bring-up.
// Record the last trap request so tests can observe it.
register last_trapnum  : bits(6)  = sail_zeros(6)
register last_cause    : bits(24) = sail_zeros(24)
register last_traparg0 : bits(64) = 0x0000_0000_0000_0000
register last_bi       : bits(1)  = 0b0

function raise_trap(trapnum : bits(6), cause : bits(24), traparg0 : bits(64), bi : bits(1)) -> unit = {
  last_trapnum  = trapnum;
  last_cause    = cause;
  last_traparg0 = traparg0;
  last_bi       = bi
}

// -----------------------------------------------------------------------------
// System Status Registers (SSR) - bring-up state model
//
// Normative sources:
// - docs/architecture/isa-manual/src/generated/system_registers_ssr.adoc
// - docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc (E_ISSR)
//
// NOTE: This staged model only provides concrete storage for a subset of base SSRs
// that are used by early software (TP/GP and bring-up loop regs). All other SSR IDs
// are routed to explicit `unimplemented(...)` until the privilege + trap envelope is
// wired into the Sail state.

register ssr_tp     : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0000
register ssr_gp     : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0001
register ssr_cstate : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0020
// (ssr_lcfr/ssr_lb0..2 declared earlier for vec bring-up)

// -----------------------------------------------------------------------------
// XBINFO / CAC_TABLE (v0.4-draft bring-up)
//
// XBINFO provides the base address of the CAC_TABLE for a given target ACR.
// The full system-call-block mechanism is platform-defined; the staged Sail model
// only uses XBINFO as an architectural knob to decide whether a CAC_TABLE exists.
//
// SSR exposure (bring-up): XBINFO is an ACR-scoped SSR.
// We allocate index 0xF30 (so full 16-bit SSR_ID is 0x nF30 for ACR n).
// The Sail SSRGET/SSRSET path uses the low 12-bit index; the active ACR bank is
// selected by the implementation (modeled explicitly here).
register xbinfo_acr0 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0F30
register xbinfo_acr1 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x1F30
register xbinfo_acr2 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x2F30

function read_xbinfo_for_acr(acr : bits(4)) -> bits(64) = {
  if acr == 0x0 then xbinfo_acr0
  else if acr == 0x1 then xbinfo_acr1
  else if acr == 0x2 then xbinfo_acr2
  else 0x0000_0000_0000_0000
}

register ssr_lc0 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0053
register ssr_lc1 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0054
register ssr_lc2 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0055

// -----------------------------------------------------------------------------
// ILLEGAL_INST / E_INST helpers (v0.4-draft bring-up contract)
//
// TRAPNUM major class:
//   ILLEGAL_INST = 4
// E_INST cause space (bring-up normative):
//   cause[15:8] = EC_* (subcause class)
//   cause[7:0]  = detail (subcause detail, 0 unless specified)
//
// EC_* allocation (staged, kept small):
//   EC_ILLEGAL = 0x01  (illegal encoding / reserved values)
//   EC_PARAM   = 0x02  (bad parameter / out-of-range / invalid combination)
//   EC_PERM    = 0x03  (permission/ACR policy violation)
//   EC_XBID    = 0x10  (XB index/id invalid)
//   EC_XBDEF   = 0x11  (XB definition invalid / CAC_TABLE entry invalid)

function trapnum_illegal_inst() -> bits(6) = { (sail_zeros(6) + 4) }

function e_inst_cause(ec : bits(8), detail : bits(8)) -> bits(24) = {
  let c16 : bits(16) = ec @ detail;
  sail_zero_extend(c16, 24)
}

function trap_e_inst(ec : bits(8), detail : bits(8), traparg0 : bits(64)) -> unit = {
  raise_trap(trapnum_illegal_inst(), e_inst_cause(ec, detail), traparg0, 0b0)
}

function trap_illegal_inst(traparg0 : bits(64)) -> unit = {
  // Legacy helper: map to E_INST(EC_ILLEGAL) with detail=0.
  trap_e_inst(0x01, 0x00, traparg0)
}

function trap_illegal_ssr() -> unit = {
  // For now, illegal SSR access is modeled as ILLEGAL_INST (manual: "illegal SSR").
  // TODO: when E_ISSR is fully wired, route to that trap class with a structured CAUSE.
  trap_illegal_inst(read_pc_or_tpc())
}

function read_system_register(id24 : bits(24)) -> bits(64) = {
  // Base SSR namespace is 12-bit for 32-bit forms.
  let id : bits(12) = id24[11..0];
  match id {
    0x000 => ssr_tp,
    0x001 => ssr_gp,
    0x020 => ssr_cstate,
    0x024 => ssr_lcfr,
    0x050 => ssr_lb0,
    0x051 => ssr_lb1,
    0x052 => ssr_lb2,
    0x053 => ssr_lc0,
    0x054 => ssr_lc1,
    0x055 => ssr_lc2,

    // XBINFO (ACR-scoped by bring-up convention). Indexed at 0xF30.
    // We select the bank by the current active ACR in CSTATE.
    0xF30 => {
      let cur_acr : bits(4) = ssr_cstate[3..0];
      if cur_acr == 0x0 then xbinfo_acr0
      else if cur_acr == 0x1 then xbinfo_acr1
      else if cur_acr == 0x2 then xbinfo_acr2
      else 0x0000_0000_0000_0000
    },

    _ => {
      trap_illegal_ssr();
      0x0000_0000_0000_0000
    }
  }
}

function write_system_register(id24 : bits(24), v : bits(64)) -> unit = {
  let id : bits(12) = id24[11..0];
  match id {
    0x000 => ssr_tp = v,
    0x001 => ssr_gp = v,
    0x020 => ssr_cstate = v,
    0x024 => { trap_illegal_inst(read_pc_or_tpc()) },
    0x050 => ssr_lb0 = v,
    0x051 => ssr_lb1 = v,
    0x052 => ssr_lb2 = v,
    0x053 => ssr_lc0 = v,
    0x054 => ssr_lc1 = v,
    0x055 => ssr_lc2 = v,

    0xF30 => {
      let cur_acr : bits(4) = ssr_cstate[3..0];
      if cur_acr == 0x0 then xbinfo_acr0 = v
      else if cur_acr == 0x1 then xbinfo_acr1 = v
      else if cur_acr == 0x2 then xbinfo_acr2 = v
      else trap_illegal_ssr()
    },

    _ => trap_illegal_ssr()
  }
}

function swap_system_register(id24 : bits(24), v : bits(64)) -> bits(64) = {
  let old = read_system_register(id24);
  write_system_register(id24, v);
  old
}

// -----------------------------------------------------------------------------
// CSTATE floating-point control/status fields (v0.3 staged profile)
//
// Architectural contract (per user + spec alignment):
// - CSTATE.FFLAGS[36:32] are IEEE754 sticky exception flags: NV/DZ/OF/UF/NX
// - CSTATE.FRM[39:37] is rounding mode; only low 4 encodings used initially.
//
// Flag bits within CSTATE:
//   bit32 NV, bit33 DZ, bit34 OF, bit35 UF, bit36 NX
//
// Rounding mode encodings (low 4):
//   0=RNE, 1=RDN, 2=RUP, 3=RTZ
// FCVTA uses ties-away (RMM) as an explicit override even though FRM doesn't
// currently expose an encoding for it.

function cstate_get_fflags() -> bits(5) = { ssr_cstate[36..32] }
function cstate_set_fflags(f : bits(5)) -> unit = {
  ssr_cstate[36..32] = f
}

function cstate_or_fflags(f : bits(5)) -> unit = {
  cstate_set_fflags(cstate_get_fflags() | f)
}

function cstate_get_frm() -> bits(3) = { ssr_cstate[39..37] }
function cstate_set_frm(rm : bits(3)) -> unit = {
  ssr_cstate[39..37] = rm
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

function trapnum_block_trap() -> bits(6) = { (sail_zeros(6) + 5) }

function e_block_cause(ec : bits(8), detail : bits(8)) -> bits(24) = {
  // Zero-extend into the 24-bit TRAPNO.CAUSE field.
  let c16 : bits(16) = ec @ detail;
  sail_zero_extend(c16, 24)
}

function trap_block_cfi(ec_cfi_kind : bits(4), src_pc_or_tpc : bits(64)) -> unit = {
  // E_BLOCK(EC_CFI) is precise, BI=0, TRAPARG0=source PC/TPC.
  // detail[3:0]=kind, detail[7:4]=0.
  let detail : bits(8) = sail_zero_extend(ec_cfi_kind, 8);
  raise_trap(trapnum_block_trap(), e_block_cause(0x01, detail), src_pc_or_tpc, 0b0)
}

function trap_blockfmt(missing_desc_family : bits(8), missing_detail : bits(8), src_pc_or_tpc : bits(64)) -> unit = {
  // E_BLOCK(EC_BLOCKFMT): BI=0, TRAPARG0 encodes missing/invalid descriptor.
  // Clarifications: TRAPARG0[7:0]=MissingDescFamily, TRAPARG0[15:8]=MissingDetail.
  let traparg0 = sail_zero_extend(missing_desc_family, 64)
              | sail_shiftleft(sail_zero_extend(missing_detail, 64), 8);
  raise_trap(trapnum_block_trap(), e_block_cause(0x02, 0x00), traparg0, 0b0)
}

function trap_bfetch(fault_va : bits(64)) -> unit = {
  // E_BLOCK(EC_BFETCH): BI=1, TRAPARG0=faulting VA.
  raise_trap(trapnum_block_trap(), e_block_cause(0x03, 0x00), fault_va, 0b1)
}

// -----------------------------------------------------------------------------
// Block boundary + BARG state (staged; contracts defined in ISA manual)
//
// These interfaces are used by BSTART/BSTOP semantics. A complete model will:
// - reset/initialize BARG at block start;
// - accumulate SETC/B.ATTR/B.* updates into BARG during the block;
// - at block commit (BSTOP or next BSTART), consult BARG and update architectural PC/privilege/etc.
//
// For now we keep these as explicit stubs and do not guess microarchitectural details.

type block_type = bits(4)
type block_xfer_kind = bits(4)

function barg_reset_at_block_start() -> unit = {
  unimplemented("barg_reset_at_block_start")
}

function barg_set_block_type(bt : block_type) -> unit = {
  unimplemented("barg_set_block_type")
}

function barg_set_xfer_kind(k : block_xfer_kind) -> unit = {
  unimplemented("barg_set_xfer_kind")
}

function barg_set_next_pc_target(tgt : bits(64)) -> unit = {
  unimplemented("barg_set_next_pc_target")
}

function block_commit_boundary() -> unit = {
  unimplemented("block_commit_boundary")
}

// Decoded immediate/target helpers for block markers.
// The decoder/fetch layer is responsible for computing the architectural target address
// (e.g. PC-relative label resolved to an address).
function decoded_block_target_pc() -> bits(64) = {
  unimplemented("decoded_block_target_pc");
  0x0000_0000_0000_0000
}

function decoded_block_type() -> block_type = {
  unimplemented("decoded_block_type");
  0b0000
}

function decoded_block_xfer_kind() -> block_xfer_kind = {
  unimplemented("decoded_block_xfer_kind");
  0b0000
}

// CFI check hook: return true iff `addr` is a legal block start marker.
function is_block_start_marker(addr : bits(64)) -> bool = {
  unimplemented("is_block_start_marker");
  false
}

// -----------------------------------------------------------------------------
// Block header descriptor validation (B.* stream)
//
// We model the mandatory-descriptor contracts for tile/vector headers as a
// fail-fast validation at the end of the header stream (at BSTOP / next BSTART).
//
// Normative sources:
// - docs/architecture/isa-manual/src/chapters/07_tile_blocks.adoc
// - docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc
// - docs/bringup/plan/isa_clarifications.md
//
// MissingDescFamily IDs (TRAPARG0[7:0]):
//   1=B.DIM, 2=B.TEXT, 3=B.ARG, 4=B.IOR, 5=B.IOT/B.IOTI
// MissingDetail (TRAPARG0[15:8]):
//   0x00 missing, 0x01 invalid/out-of-range, 0x02 illegal combination

register bdesc_seen_dim : bool = false
register bdesc_seen_text : bool = false
register bdesc_seen_arg : bool = false
register bdesc_seen_ior : bool = false
register bdesc_seen_iot : bool = false

function bdesc_reset() -> unit = {
  bdesc_seen_dim = false;
  bdesc_seen_text = false;
  bdesc_seen_arg = false;
  bdesc_seen_ior = false;
  bdesc_seen_iot = false
}

function bdesc_mark_dim() -> unit = { bdesc_seen_dim = true }
function bdesc_mark_text() -> unit = { bdesc_seen_text = true }
function bdesc_mark_arg() -> unit = { bdesc_seen_arg = true }
function bdesc_mark_ior() -> unit = { bdesc_seen_ior = true }
function bdesc_mark_iot() -> unit = { bdesc_seen_iot = true }

// Block type classification for mandatory-descriptor contracts.
// The decoder provides a stable classification string for the staged model.
function decoded_block_contract_kind() -> bits(4) = {
  // 0=none/unspecified, 1=VEC (VPAR/VSEQ/MPAR/MSEQ), 2=TMA (TLOAD/TSTORE),
  // 3=TMOV, 4=CUBE (TMATMUL/TMATMUL.ACC), 5=ACCCVT, 6=HDRDRV (TEPL/FIXP/TMA-other)
  unimplemented("decoded_block_contract_kind");
  0b0000
}

function bdesc_require_or_trap(family : bits(8), present : bool, src_pc_or_tpc : bits(64)) -> unit = {
  if present then () else trap_blockfmt(family, 0x00, src_pc_or_tpc)
}

function bdesc_illegal_combo_or_trap(family : bits(8), src_pc_or_tpc : bits(64)) -> unit = {
  trap_blockfmt(family, 0x02, src_pc_or_tpc)
}

function bdesc_validate_header_end(src_pc_or_tpc : bits(64)) -> unit = {
  // Enforce mandatory descriptor families per tile/vector block type.
  // If multiple are missing, report exactly one using the priority order:
  //   B.ARG > B.TEXT > B.IOT > B.IOR > B.DIM
  let k = decoded_block_contract_kind();
  match k {
    // VEC: SIMT vector blocks (VPAR/VSEQ/MPAR/MSEQ): require DIM + TEXT.
    0b0001 => {
      if not_bool(bdesc_seen_text) then trap_blockfmt(0x02, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_dim) then trap_blockfmt(0x01, 0x00, src_pc_or_tpc)
      else {
        // Staged vector bring-up: initialize lane predicate mask for group 0.
        vec_init_p_for_group(ssr_lc1)
      }
    },
    // TMA: TLOAD/TSTORE: require ARG + IOR + IOT; TEXT illegal.
    0b0010 => {
      if bdesc_seen_text then bdesc_illegal_combo_or_trap(0x02, src_pc_or_tpc)
      else if not_bool(bdesc_seen_arg) then trap_blockfmt(0x03, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_iot) then trap_blockfmt(0x05, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_ior) then trap_blockfmt(0x04, 0x00, src_pc_or_tpc)
      else ()
    },
    // TMOV: require IOT; TEXT illegal.
    0b0011 => {
      if bdesc_seen_text then bdesc_illegal_combo_or_trap(0x02, src_pc_or_tpc)
      else if not_bool(bdesc_seen_iot) then trap_blockfmt(0x05, 0x00, src_pc_or_tpc)
      else ()
    },
    // CUBE: require DIM + IOT + ARG; TEXT illegal.
    0b0100 => {
      if bdesc_seen_text then bdesc_illegal_combo_or_trap(0x02, src_pc_or_tpc)
      else if not_bool(bdesc_seen_arg) then trap_blockfmt(0x03, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_iot) then trap_blockfmt(0x05, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_dim) then trap_blockfmt(0x01, 0x00, src_pc_or_tpc)
      else ()
    },
    // ACCCVT: require DIM + IOT + ARG + IOR; TEXT illegal.
    0b0101 => {
      if bdesc_seen_text then bdesc_illegal_combo_or_trap(0x02, src_pc_or_tpc)
      else if not_bool(bdesc_seen_arg) then trap_blockfmt(0x03, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_iot) then trap_blockfmt(0x05, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_ior) then trap_blockfmt(0x04, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_dim) then trap_blockfmt(0x01, 0x00, src_pc_or_tpc)
      else ()
    },
    // HDRDRV: header-driven engine ops: TEXT illegal; mandatory families are op-specific.
    0b0110 => {
      if bdesc_seen_text then bdesc_illegal_combo_or_trap(0x02, src_pc_or_tpc) else ()
    },
    _ => ()
  }
}

function trap_assert_fail(traparg0 : bits(64)) -> unit = {
  // TRAPNUM_ASSERT_FAIL = 52, CAUSE=0, BI=0
  raise_trap((sail_zeros(6) + 52), (sail_zeros(24) + 0), traparg0, 0b0)
}

// ECONFIG (execution config) accessors (stub). In strict v0.3, ECONFIG[3] is the global exception enable.
function read_econfig() -> bits(64) = {
  unimplemented("read_econfig");
  0x0000_0000_0000_0000
}

// Global exception enable (profile-defined). When disabled, ASSERT is treated as a no-op.
function exceptions_enabled() -> bool = {
  read_econfig()[3] == 0b1
}


function trap_sw_breakpoint(traparg0 : bits(64)) -> unit = {
  // TRAPNUM_SW_BREAKPOINT = 50, CAUSE=0, BI=0
  raise_trap((sail_zeros(6) + 50), (sail_zeros(24) + 0), traparg0, 0b0)
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
  mem_read8(ea)
}

function write_mem8(ea : bits(64), v : bits(8)) -> unit = {
  mem_write8(ea, v)
}
