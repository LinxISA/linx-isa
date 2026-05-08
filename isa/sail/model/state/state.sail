// LinxISA architectural state model for canonical v0.56.
// The state model grows incrementally while strict legality and execution coverage expand.
//
// NOTE: The current bring-up model still relies on decoder shadow metadata for some
// block/header fields, but the architectural state and execute layers carry concrete
// behavior for active v0.56 instructions.

$include <prelude.sail>
$include <arith.sail>
$include <vector.sail>
$include "../lib/common.sail"
$include <string.sail>

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

// Block-control predicate / commit-argument (BARG.CARG).
register barg_carg : bits(64) = 0x0000_0000_0000_0000
register barg_tgt_reg_valid : bool = false
register barg_tgt_reg : bits(5) = 0b00000

function set_commit_argument(v : bits(64)) -> unit = {
  barg_carg = v
}

// Block next-target selector (BARG.TGT).
// SETC.TGT / C.SETC.TGT select the register-based target for RET/IND/ICALL-class transitions.
function set_commit_target_reg(r : bits(5)) -> unit = {
  barg_tgt_reg_valid = true;
  barg_tgt_reg = r
}

function read_commit_argument() -> bits(64) = {
  barg_carg
}

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
// Vector engine block-local state (staged bring-up)
//
// This models the second-layer (vector block internal) architectural state that is
// visible to vector instructions.

// Vec engine predicate register (p).
// - Block-local, initialized from B.DIM/B.DATR state on block dispatch.
// - Inactive lanes are typically treated as don't-care by most V.* ops; explicit
//   merge is performed via V.PSEL.
register vec_p : bits(64) = 0xFFFF_FFFF_FFFF_FFFF

function read_predicate_p() -> bits(64) = { vec_p }
function write_predicate_p(v : bits(64)) -> unit = { vec_p = v }

// Decoder-provided helpers for staged block-descriptor execution.
// The Sail model stores these in shadow registers so tests / a future decode
// layer can preload the already-decoded values without baking an ad hoc parser
// into the execution rules.
register decoded_bdim_index_shadow : bits(2) = 0b00
register decoded_bdim_value_shadow : bits(64) = 0x0000_0000_0000_0000
register decoded_bcatr_raw_shadow : bits(64) = 0x0000_0000_0000_0000
register decoded_bdatr_raw_shadow : bits(64) = 0x0000_0000_0000_0000
register decoded_bior_regsrc0_shadow : bits(5) = 0b00000
register decoded_bior_regsrc1_shadow : bits(5) = 0b00000
register decoded_bior_regsrc2_shadow : bits(5) = 0b00000
register decoded_bior_regdst_shadow  : bits(5) = 0b00000

function decoded_bdim_index() -> bits(2) = {
  // 0=LB0, 1=LB1, 2=LB2
  decoded_bdim_index_shadow
}

function decoded_bdim_value() -> bits(64) = {
  decoded_bdim_value_shadow
}

function decoded_bcatr_raw() -> bits(64) = {
  // Full 64-bit control-attribute word as encoded by B.CATR.
  decoded_bcatr_raw_shadow
}

function decoded_bdatr_raw() -> bits(64) = {
  // Full 64-bit data-attribute word as encoded by B.DATR.
  decoded_bdatr_raw_shadow
}

function decoded_bior_regsrc0() -> bits(5) = { decoded_bior_regsrc0_shadow }
function decoded_bior_regsrc1() -> bits(5) = { decoded_bior_regsrc1_shadow }
function decoded_bior_regsrc2() -> bits(5) = { decoded_bior_regsrc2_shadow }
function decoded_bior_regdst()  -> bits(5) = { decoded_bior_regdst_shadow }

function set_decoded_bior(regsrc0 : bits(5), regsrc1 : bits(5), regsrc2 : bits(5), regdst : bits(5)) -> unit = {
  decoded_bior_regsrc0_shadow = regsrc0;
  decoded_bior_regsrc1_shadow = regsrc1;
  decoded_bior_regsrc2_shadow = regsrc2;
  decoded_bior_regdst_shadow = regdst
}

// Latched B.CATR/B.DATR state relevant to VEC bring-up.
register bcatr_raw : bits(64) = 0x0000_0000_0000_0000
register bdatr_raw : bits(64) = 0x0000_0000_0000_0000
function bcatr_dr() -> bool = { bcatr_raw[26] == 0b1 }
function bdatr_sat() -> bool = { bdatr_raw[31] == 0b1 }

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
register ssr_lc0  : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0053
register ssr_lc1  : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0054
register ssr_lc2  : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0055

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
  if not_bool(bcatr_dr()) then {
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
// Vector lane register file (canonical v0.56 decode carrier)
//
// Live LLVM/QEMU v0.56 uses a class/index RegId10 encoding:
//   (Class << 5) | Index
//   Class 1 = ri*    (ordered B.IOR import namespace)
//   Class 3 = lc*    (lane/group counters)
//   Class 4 = vt / vt#n
//   Class 5 = vu / vu#n
//   Class 6 = vm / vm#n
//   Class 7 = vn / vn#n
//   Class 8 = ta/tb/tc/td/to/ts
//
// Vector register classes 4..7 map into a unified 32-entry carrier file:
//   0..7   = VT#0..VT#7
//   8..15  = VU#0..VU#7
//   16..23 = VM#0..VM#7
//   24..31 = VN#0..VN#7
//
// Every vector register is modeled as 64 lanes of 32-bit carriers. The live
// encoding does not carry an explicit RegId10 lane type field. Convert-class
// instructions use explicit SrcType/DstType, while non-convert integer/FP
// families receive mnemonic-defined default decoded type shadows and execute by
// numeric cast/cvt from the 32-bit carrier domain.

type vec_reg64x32 = bits(2048)

register vreg0  : vec_reg64x32 = sail_zeros(2048)
register vreg1  : vec_reg64x32 = sail_zeros(2048)
register vreg2  : vec_reg64x32 = sail_zeros(2048)
register vreg3  : vec_reg64x32 = sail_zeros(2048)
register vreg4  : vec_reg64x32 = sail_zeros(2048)
register vreg5  : vec_reg64x32 = sail_zeros(2048)
register vreg6  : vec_reg64x32 = sail_zeros(2048)
register vreg7  : vec_reg64x32 = sail_zeros(2048)
register vreg8  : vec_reg64x32 = sail_zeros(2048)
register vreg9  : vec_reg64x32 = sail_zeros(2048)
register vreg10 : vec_reg64x32 = sail_zeros(2048)
register vreg11 : vec_reg64x32 = sail_zeros(2048)
register vreg12 : vec_reg64x32 = sail_zeros(2048)
register vreg13 : vec_reg64x32 = sail_zeros(2048)
register vreg14 : vec_reg64x32 = sail_zeros(2048)
register vreg15 : vec_reg64x32 = sail_zeros(2048)
register vreg16 : vec_reg64x32 = sail_zeros(2048)
register vreg17 : vec_reg64x32 = sail_zeros(2048)
register vreg18 : vec_reg64x32 = sail_zeros(2048)
register vreg19 : vec_reg64x32 = sail_zeros(2048)
register vreg20 : vec_reg64x32 = sail_zeros(2048)
register vreg21 : vec_reg64x32 = sail_zeros(2048)
register vreg22 : vec_reg64x32 = sail_zeros(2048)
register vreg23 : vec_reg64x32 = sail_zeros(2048)
register vreg24 : vec_reg64x32 = sail_zeros(2048)
register vreg25 : vec_reg64x32 = sail_zeros(2048)
register vreg26 : vec_reg64x32 = sail_zeros(2048)
register vreg27 : vec_reg64x32 = sail_zeros(2048)
register vreg28 : vec_reg64x32 = sail_zeros(2048)
register vreg29 : vec_reg64x32 = sail_zeros(2048)
register vreg30 : vec_reg64x32 = sail_zeros(2048)
register vreg31 : vec_reg64x32 = sail_zeros(2048)

function read_vt(k : bits(5)) -> vec_reg64x32 = {
  match k {
    0b00000 => vreg0,
    0b00001 => vreg1,
    0b00010 => vreg2,
    0b00011 => vreg3,
    0b00100 => vreg4,
    0b00101 => vreg5,
    0b00110 => vreg6,
    0b00111 => vreg7,
    0b01000 => vreg8,
    0b01001 => vreg9,
    0b01010 => vreg10,
    0b01011 => vreg11,
    0b01100 => vreg12,
    0b01101 => vreg13,
    0b01110 => vreg14,
    0b01111 => vreg15,
    0b10000 => vreg16,
    0b10001 => vreg17,
    0b10010 => vreg18,
    0b10011 => vreg19,
    0b10100 => vreg20,
    0b10101 => vreg21,
    0b10110 => vreg22,
    0b10111 => vreg23,
    0b11000 => vreg24,
    0b11001 => vreg25,
    0b11010 => vreg26,
    0b11011 => vreg27,
    0b11100 => vreg28,
    0b11101 => vreg29,
    0b11110 => vreg30,
    0b11111 => vreg31
  }
}

function write_vt(k : bits(5), v : vec_reg64x32) -> unit = {
  match k {
    0b00000 => vreg0 = v,
    0b00001 => vreg1 = v,
    0b00010 => vreg2 = v,
    0b00011 => vreg3 = v,
    0b00100 => vreg4 = v,
    0b00101 => vreg5 = v,
    0b00110 => vreg6 = v,
    0b00111 => vreg7 = v,
    0b01000 => vreg8 = v,
    0b01001 => vreg9 = v,
    0b01010 => vreg10 = v,
    0b01011 => vreg11 = v,
    0b01100 => vreg12 = v,
    0b01101 => vreg13 = v,
    0b01110 => vreg14 = v,
    0b01111 => vreg15 = v,
    0b10000 => vreg16 = v,
    0b10001 => vreg17 = v,
    0b10010 => vreg18 = v,
    0b10011 => vreg19 = v,
    0b10100 => vreg20 = v,
    0b10101 => vreg21 = v,
    0b10110 => vreg22 = v,
    0b10111 => vreg23 = v,
    0b11000 => vreg24 = v,
    0b11001 => vreg25 = v,
    0b11010 => vreg26 = v,
    0b11011 => vreg27 = v,
    0b11100 => vreg28 = v,
    0b11101 => vreg29 = v,
    0b11110 => vreg30 = v,
    0b11111 => vreg31 = v
  }
}

// Ordered scalar imports (`ri*`) are allocated from B.IOR headers in descriptor order.
register ri_alloc_count : bits(6) = 0b00_0000

register ri_select0  : bits(5) = 0b00000
register ri_select1  : bits(5) = 0b00000
register ri_select2  : bits(5) = 0b00000
register ri_select3  : bits(5) = 0b00000
register ri_select4  : bits(5) = 0b00000
register ri_select5  : bits(5) = 0b00000
register ri_select6  : bits(5) = 0b00000
register ri_select7  : bits(5) = 0b00000
register ri_select8  : bits(5) = 0b00000
register ri_select9  : bits(5) = 0b00000
register ri_select10 : bits(5) = 0b00000
register ri_select11 : bits(5) = 0b00000
register ri_select12 : bits(5) = 0b00000
register ri_select13 : bits(5) = 0b00000
register ri_select14 : bits(5) = 0b00000
register ri_select15 : bits(5) = 0b00000
register ri_select16 : bits(5) = 0b00000
register ri_select17 : bits(5) = 0b00000
register ri_select18 : bits(5) = 0b00000
register ri_select19 : bits(5) = 0b00000
register ri_select20 : bits(5) = 0b00000
register ri_select21 : bits(5) = 0b00000
register ri_select22 : bits(5) = 0b00000
register ri_select23 : bits(5) = 0b00000
register ri_select24 : bits(5) = 0b00000
register ri_select25 : bits(5) = 0b00000
register ri_select26 : bits(5) = 0b00000
register ri_select27 : bits(5) = 0b00000
register ri_select28 : bits(5) = 0b00000
register ri_select29 : bits(5) = 0b00000
register ri_select30 : bits(5) = 0b00000
register ri_select31 : bits(5) = 0b00000

register ri_valid0  : bool = false
register ri_valid1  : bool = false
register ri_valid2  : bool = false
register ri_valid3  : bool = false
register ri_valid4  : bool = false
register ri_valid5  : bool = false
register ri_valid6  : bool = false
register ri_valid7  : bool = false
register ri_valid8  : bool = false
register ri_valid9  : bool = false
register ri_valid10 : bool = false
register ri_valid11 : bool = false
register ri_valid12 : bool = false
register ri_valid13 : bool = false
register ri_valid14 : bool = false
register ri_valid15 : bool = false
register ri_valid16 : bool = false
register ri_valid17 : bool = false
register ri_valid18 : bool = false
register ri_valid19 : bool = false
register ri_valid20 : bool = false
register ri_valid21 : bool = false
register ri_valid22 : bool = false
register ri_valid23 : bool = false
register ri_valid24 : bool = false
register ri_valid25 : bool = false
register ri_valid26 : bool = false
register ri_valid27 : bool = false
register ri_valid28 : bool = false
register ri_valid29 : bool = false
register ri_valid30 : bool = false
register ri_valid31 : bool = false

function ri_binding_reg(idx : bits(5)) -> bits(5) = {
  match idx {
    0b00000 => ri_select0,
    0b00001 => ri_select1,
    0b00010 => ri_select2,
    0b00011 => ri_select3,
    0b00100 => ri_select4,
    0b00101 => ri_select5,
    0b00110 => ri_select6,
    0b00111 => ri_select7,
    0b01000 => ri_select8,
    0b01001 => ri_select9,
    0b01010 => ri_select10,
    0b01011 => ri_select11,
    0b01100 => ri_select12,
    0b01101 => ri_select13,
    0b01110 => ri_select14,
    0b01111 => ri_select15,
    0b10000 => ri_select16,
    0b10001 => ri_select17,
    0b10010 => ri_select18,
    0b10011 => ri_select19,
    0b10100 => ri_select20,
    0b10101 => ri_select21,
    0b10110 => ri_select22,
    0b10111 => ri_select23,
    0b11000 => ri_select24,
    0b11001 => ri_select25,
    0b11010 => ri_select26,
    0b11011 => ri_select27,
    0b11100 => ri_select28,
    0b11101 => ri_select29,
    0b11110 => ri_select30,
    0b11111 => ri_select31
  }
}

function ri_binding_present(idx : bits(5)) -> bool = {
  match idx {
    0b00000 => ri_valid0,
    0b00001 => ri_valid1,
    0b00010 => ri_valid2,
    0b00011 => ri_valid3,
    0b00100 => ri_valid4,
    0b00101 => ri_valid5,
    0b00110 => ri_valid6,
    0b00111 => ri_valid7,
    0b01000 => ri_valid8,
    0b01001 => ri_valid9,
    0b01010 => ri_valid10,
    0b01011 => ri_valid11,
    0b01100 => ri_valid12,
    0b01101 => ri_valid13,
    0b01110 => ri_valid14,
    0b01111 => ri_valid15,
    0b10000 => ri_valid16,
    0b10001 => ri_valid17,
    0b10010 => ri_valid18,
    0b10011 => ri_valid19,
    0b10100 => ri_valid20,
    0b10101 => ri_valid21,
    0b10110 => ri_valid22,
    0b10111 => ri_valid23,
    0b11000 => ri_valid24,
    0b11001 => ri_valid25,
    0b11010 => ri_valid26,
    0b11011 => ri_valid27,
    0b11100 => ri_valid28,
    0b11101 => ri_valid29,
    0b11110 => ri_valid30,
    0b11111 => ri_valid31
  }
}

function set_ri_binding(idx : bits(5), reg : bits(5)) -> unit = {
  match idx {
    0b00000 => { ri_select0 = reg; ri_valid0 = true },
    0b00001 => { ri_select1 = reg; ri_valid1 = true },
    0b00010 => { ri_select2 = reg; ri_valid2 = true },
    0b00011 => { ri_select3 = reg; ri_valid3 = true },
    0b00100 => { ri_select4 = reg; ri_valid4 = true },
    0b00101 => { ri_select5 = reg; ri_valid5 = true },
    0b00110 => { ri_select6 = reg; ri_valid6 = true },
    0b00111 => { ri_select7 = reg; ri_valid7 = true },
    0b01000 => { ri_select8 = reg; ri_valid8 = true },
    0b01001 => { ri_select9 = reg; ri_valid9 = true },
    0b01010 => { ri_select10 = reg; ri_valid10 = true },
    0b01011 => { ri_select11 = reg; ri_valid11 = true },
    0b01100 => { ri_select12 = reg; ri_valid12 = true },
    0b01101 => { ri_select13 = reg; ri_valid13 = true },
    0b01110 => { ri_select14 = reg; ri_valid14 = true },
    0b01111 => { ri_select15 = reg; ri_valid15 = true },
    0b10000 => { ri_select16 = reg; ri_valid16 = true },
    0b10001 => { ri_select17 = reg; ri_valid17 = true },
    0b10010 => { ri_select18 = reg; ri_valid18 = true },
    0b10011 => { ri_select19 = reg; ri_valid19 = true },
    0b10100 => { ri_select20 = reg; ri_valid20 = true },
    0b10101 => { ri_select21 = reg; ri_valid21 = true },
    0b10110 => { ri_select22 = reg; ri_valid22 = true },
    0b10111 => { ri_select23 = reg; ri_valid23 = true },
    0b11000 => { ri_select24 = reg; ri_valid24 = true },
    0b11001 => { ri_select25 = reg; ri_valid25 = true },
    0b11010 => { ri_select26 = reg; ri_valid26 = true },
    0b11011 => { ri_select27 = reg; ri_valid27 = true },
    0b11100 => { ri_select28 = reg; ri_valid28 = true },
    0b11101 => { ri_select29 = reg; ri_valid29 = true },
    0b11110 => { ri_select30 = reg; ri_valid30 = true },
    0b11111 => { ri_select31 = reg; ri_valid31 = true }
  }
}

function clear_ri_bindings() -> unit = {
  ri_alloc_count = 0b00_0000;
  ri_valid0 = false;
  ri_valid1 = false;
  ri_valid2 = false;
  ri_valid3 = false;
  ri_valid4 = false;
  ri_valid5 = false;
  ri_valid6 = false;
  ri_valid7 = false;
  ri_valid8 = false;
  ri_valid9 = false;
  ri_valid10 = false;
  ri_valid11 = false;
  ri_valid12 = false;
  ri_valid13 = false;
  ri_valid14 = false;
  ri_valid15 = false;
  ri_valid16 = false;
  ri_valid17 = false;
  ri_valid18 = false;
  ri_valid19 = false;
  ri_valid20 = false;
  ri_valid21 = false;
  ri_valid22 = false;
  ri_valid23 = false;
  ri_valid24 = false;
  ri_valid25 = false;
  ri_valid26 = false;
  ri_valid27 = false;
  ri_valid28 = false;
  ri_valid29 = false;
  ri_valid30 = false;
  ri_valid31 = false
}

function allocate_ri_binding(reg : bits(5)) -> unit = {
  if ri_alloc_count == 0b10_0000 then {
    ()
  } else {
    set_ri_binding(ri_alloc_count[4..0], reg);
    ri_alloc_count = ri_alloc_count + 0b00_0001
  }
}

function read_ri_value(idx : bits(5)) -> bits(64) = {
  if ri_binding_present(idx) then {
    read_reg5(ri_binding_reg(idx))
  } else {
    0x0000_0000_0000_0000
  }
}

// Decode-provided vector operand raw RegId10 shadows.
register decoded_vec_srcl_regid_shadow : bits(10) = 0b00_0000_0000
register decoded_vec_srcr_regid_shadow : bits(10) = 0b00_0000_0000
register decoded_vec_srca_regid_shadow : bits(10) = 0b00_0000_0000
register decoded_vec_srcp_regid_shadow : bits(10) = 0b00_0000_0000
register decoded_vec_dst_regid_shadow  : bits(10) = 0b00_0000_0000

function decoded_vec_srcl_regid() -> bits(10) = { decoded_vec_srcl_regid_shadow }
function decoded_vec_srcr_regid() -> bits(10) = { decoded_vec_srcr_regid_shadow }
function decoded_vec_srca_regid() -> bits(10) = { decoded_vec_srca_regid_shadow }
function decoded_vec_srcp_regid() -> bits(10) = { decoded_vec_srcp_regid_shadow }
function decoded_vec_dst_regid()  -> bits(10) = { decoded_vec_dst_regid_shadow }

function set_decoded_vec_regids(srcl : bits(10), srcr : bits(10), srca : bits(10), srcp : bits(10), dst : bits(10)) -> unit = {
  decoded_vec_srcl_regid_shadow = srcl;
  decoded_vec_srcr_regid_shadow = srcr;
  decoded_vec_srca_regid_shadow = srca;
  decoded_vec_srcp_regid_shadow = srcp;
  decoded_vec_dst_regid_shadow = dst
}

// Decode-provided vector operand typing shadows.
//
// In the v0.56 bring-up profile, RegId10 itself only carries class/index.
// These shadows therefore come from explicit instruction type fields when present,
// or from the current default carrier-domain rules for the consuming opcode family.
register decoded_vec_srcl_type_shadow : bits(5) = 0b00001
register decoded_vec_srcr_type_shadow : bits(5) = 0b00001
register decoded_vec_srca_type_shadow : bits(5) = 0b00001
register decoded_vec_srcp_type_shadow : bits(5) = 0b00001
register decoded_vec_dst_type_shadow  : bits(5) = 0b00001

function decoded_vec_srcl_type() -> bits(5) = { decoded_vec_srcl_type_shadow }
function decoded_vec_srcr_type() -> bits(5) = { decoded_vec_srcr_type_shadow }
function decoded_vec_srca_type() -> bits(5) = { decoded_vec_srca_type_shadow }
function decoded_vec_srcp_type() -> bits(5) = { decoded_vec_srcp_type_shadow }
function decoded_vec_dst_type()  -> bits(5) = { decoded_vec_dst_type_shadow }

function set_decoded_vec_types(srcl_t : bits(5), srcr_t : bits(5), srca_t : bits(5), srcp_t : bits(5), dst_t : bits(5)) -> unit = {
  decoded_vec_srcl_type_shadow = srcl_t;
  decoded_vec_srcr_type_shadow = srcr_t;
  decoded_vec_srca_type_shadow = srca_t;
  decoded_vec_srcp_type_shadow = srcp_t;
  decoded_vec_dst_type_shadow = dst_t
}

function regid10_class(regid : bits(10)) -> bits(5) = {
  regid[9..5]
}

function regid10_index(regid : bits(10)) -> bits(5) = {
  regid[4..0]
}

function regid10_vector_namespace_ok(regid : bits(10)) -> bool = {
  let cls : bits(5) = regid10_class(regid);
  (cls == 0b00000) |
  (cls == 0b00001) |
  (cls == 0b00011) |
  (cls == 0b00100) |
  (cls == 0b00101) |
  (cls == 0b00110) |
  (cls == 0b00111) |
  (cls == 0b01000)
}

function regid10_vector_selector(regid : bits(10)) -> bits(5) = {
  let cls : bits(5) = regid10_class(regid);
  let idx : bits(5) = regid10_index(regid);
  if cls == 0b00100 then idx
  else if cls == 0b00101 then 0b01000 + idx
  else if cls == 0b00110 then 0b10000 + idx
  else if cls == 0b00111 then 0b11000 + idx
  else idx
}

function regid10_vector_int_type(regid : bits(10)) -> bits(5) = {
  let _ = regid;
  // Current strict profile default for non-convert integer/vector carrier ops.
  0b00001
}

function regid10_vector_fp_type(regid : bits(10)) -> bits(5) = {
  let _ = regid;
  // Current strict profile default for non-convert floating/vector carrier ops.
  0b00001
}

function regid10_is_vector_register(regid : bits(10)) -> bool = {
  let cls : bits(5) = regid10_class(regid);
  (cls == 0b00100) | (cls == 0b00101) | (cls == 0b00110) | (cls == 0b00111)
}

function read_lc_value(idx : bits(5)) -> bits(64) = {
  match idx {
    0b00000 => ssr_lc0,
    0b00001 => ssr_lc1,
    0b00010 => ssr_lc2,
    _ => {
      0x0000_0000_0000_0000
    }
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

function read_vec_operand_lane32(regid : bits(10), lane : int) -> bits(32) = {
  let cls : bits(5) = regid10_class(regid);
  let idx : bits(5) = regid10_index(regid);
  if cls == 0b00000 then {
    read_reg5(idx)[31..0]
  } else if cls == 0b00001 then {
    read_ri_value(idx)[31..0]
  } else if cls == 0b00011 then {
    read_lc_value(idx)[31..0]
  } else if regid10_is_vector_register(regid) then {
    vec_get_lane32(read_vt(regid10_vector_selector(regid)), lane)
  } else if cls == 0b01000 then {
    sail_zero_extend(idx, 32)
  } else {
    undefined_bitvector(32)
  }
}

function read_vec_operand_scalar64(regid : bits(10)) -> bits(64) = {
  let cls : bits(5) = regid10_class(regid);
  let idx : bits(5) = regid10_index(regid);
  if cls == 0b00000 then {
    read_reg5(idx)
  } else if cls == 0b00001 then {
    read_ri_value(idx)
  } else if cls == 0b00011 then {
    read_lc_value(idx)
  } else if regid10_is_vector_register(regid) then {
    zext32_from32(vec_get_lane32(read_vt(regid10_vector_selector(regid)), 0))
  } else if cls == 0b01000 then {
    sail_zero_extend(idx, 64)
  } else {
    0x0000_0000_0000_0000
  }
}

function read_vec_dest_value(regid : bits(10), fallback_k : bits(5)) -> vec_reg64x32 = {
  if regid10_is_vector_register(regid) then {
    read_vt(regid10_vector_selector(regid))
  } else if regid == 0b00_0000_0000 then {
    sail_zeros(2048)
  } else {
    read_vt(fallback_k)
  }
}

function write_vec_dest_value(regid : bits(10), fallback_k : bits(5), v : vec_reg64x32) -> unit = {
  if regid10_is_vector_register(regid) then {
    write_vt(regid10_vector_selector(regid), v)
  } else if regid == 0b00_0000_0000 then {
    ()
  } else {
    write_vt(fallback_k, v)
  }
}


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
// NOTE: This staged model only provides concrete storage for the subset of base SSRs
// needed by current software and gates. Unknown/unsupported SSR IDs trap through the
// architectural illegal-SSR path.

register ssr_tp     : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0000
register ssr_gp     : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0001
register ssr_cstate : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0020
register ssr_ecstate_acr0 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0F00 (low nibble = target ACR, bit4 = BI)
register ssr_ecstate_acr1 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x1F00
register ssr_ecstate_acr2 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x2F00
register ssr_econfig_acr0 : bits(64) = 0x0000_0000_0000_0008 // SSR_ID 0x0F07
register ssr_econfig_acr1 : bits(64) = 0x0000_0000_0000_0008 // SSR_ID 0x1F07
register ssr_econfig_acr2 : bits(64) = 0x0000_0000_0000_0008 // SSR_ID 0x2F07
register ssr_ebarg_bpc_cur_acr0 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0F41
register ssr_ebarg_bpc_cur_acr1 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x1F41
register ssr_ebarg_bpc_cur_acr2 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x2F41
register ssr_ebarg_bpc_tgt_acr0 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0F42
register ssr_ebarg_bpc_tgt_acr1 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x1F42
register ssr_ebarg_bpc_tgt_acr2 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x2F42
register ssr_ebarg_tpc_acr0 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0F43
register ssr_ebarg_tpc_acr1 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x1F43
register ssr_ebarg_tpc_acr2 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x2F43
register ssr_ebarg_extctx_ptr_acr0 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0F4F
register ssr_ebarg_extctx_ptr_acr1 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x1F4F
register ssr_ebarg_extctx_ptr_acr2 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x2F4F
register ssr_ebarg_extctx_meta_acr0 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0F50
register ssr_ebarg_extctx_meta_acr1 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x1F50
register ssr_ebarg_extctx_meta_acr2 : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x2F50
// (ssr_lcfr/ssr_lb0..2 declared earlier for vec bring-up)

// -----------------------------------------------------------------------------
// XBINFO / CAC_TABLE (current v0.56 bring-up profile)
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

// Resolved XB dispatch request.
// The generic v0.56 architecture standardizes legality, permission, and
// CAC-table selection, but the binary entry layout remains platform-defined.
// The Sail model therefore records the resolved dispatch request instead of
// inventing a non-canonical in-entry block-header decoder.
register xb_dispatch_valid : bool = false
register xb_dispatch_acr : bits(4) = 0x0
register xb_dispatch_cid : bits(7) = 0b0000000
register xb_dispatch_entry_ea : bits(64) = 0x0000_0000_0000_0000
register xb_dispatch_entry_word0 : bits(64) = 0x0000_0000_0000_0000

function read_xbinfo_for_acr(acr : bits(4)) -> bits(64) = {
  if acr == 0x0 then xbinfo_acr0
  else if acr == 0x1 then xbinfo_acr1
  else if acr == 0x2 then xbinfo_acr2
  else 0x0000_0000_0000_0000
}

function current_acr_id() -> bits(4) = { ssr_cstate[3..0] }

function read_ecstate_for_acr(acr : bits(4)) -> bits(64) = {
  if acr == 0x0 then ssr_ecstate_acr0
  else if acr == 0x1 then ssr_ecstate_acr1
  else if acr == 0x2 then ssr_ecstate_acr2
  else 0x0000_0000_0000_0000
}

function write_ecstate_for_acr(acr : bits(4), v : bits(64)) -> unit = {
  if acr == 0x0 then ssr_ecstate_acr0 = v
  else if acr == 0x1 then ssr_ecstate_acr1 = v
  else if acr == 0x2 then ssr_ecstate_acr2 = v
  else ()
}

function read_ebarg_bpc_cur_for_acr(acr : bits(4)) -> bits(64) = {
  if acr == 0x0 then ssr_ebarg_bpc_cur_acr0
  else if acr == 0x1 then ssr_ebarg_bpc_cur_acr1
  else if acr == 0x2 then ssr_ebarg_bpc_cur_acr2
  else 0x0000_0000_0000_0000
}

function write_ebarg_bpc_cur_for_acr(acr : bits(4), v : bits(64)) -> unit = {
  if acr == 0x0 then ssr_ebarg_bpc_cur_acr0 = v
  else if acr == 0x1 then ssr_ebarg_bpc_cur_acr1 = v
  else if acr == 0x2 then ssr_ebarg_bpc_cur_acr2 = v
  else ()
}

function read_ebarg_bpc_tgt_for_acr(acr : bits(4)) -> bits(64) = {
  if acr == 0x0 then ssr_ebarg_bpc_tgt_acr0
  else if acr == 0x1 then ssr_ebarg_bpc_tgt_acr1
  else if acr == 0x2 then ssr_ebarg_bpc_tgt_acr2
  else 0x0000_0000_0000_0000
}

function write_ebarg_bpc_tgt_for_acr(acr : bits(4), v : bits(64)) -> unit = {
  if acr == 0x0 then ssr_ebarg_bpc_tgt_acr0 = v
  else if acr == 0x1 then ssr_ebarg_bpc_tgt_acr1 = v
  else if acr == 0x2 then ssr_ebarg_bpc_tgt_acr2 = v
  else ()
}

function read_ebarg_tpc_for_acr(acr : bits(4)) -> bits(64) = {
  if acr == 0x0 then ssr_ebarg_tpc_acr0
  else if acr == 0x1 then ssr_ebarg_tpc_acr1
  else if acr == 0x2 then ssr_ebarg_tpc_acr2
  else 0x0000_0000_0000_0000
}

function write_ebarg_tpc_for_acr(acr : bits(4), v : bits(64)) -> unit = {
  if acr == 0x0 then ssr_ebarg_tpc_acr0 = v
  else if acr == 0x1 then ssr_ebarg_tpc_acr1 = v
  else if acr == 0x2 then ssr_ebarg_tpc_acr2 = v
  else ()
}

function read_ebarg_extctx_ptr_for_acr(acr : bits(4)) -> bits(64) = {
  if acr == 0x0 then ssr_ebarg_extctx_ptr_acr0
  else if acr == 0x1 then ssr_ebarg_extctx_ptr_acr1
  else if acr == 0x2 then ssr_ebarg_extctx_ptr_acr2
  else 0x0000_0000_0000_0000
}

function write_ebarg_extctx_ptr_for_acr(acr : bits(4), v : bits(64)) -> unit = {
  if acr == 0x0 then ssr_ebarg_extctx_ptr_acr0 = v
  else if acr == 0x1 then ssr_ebarg_extctx_ptr_acr1 = v
  else if acr == 0x2 then ssr_ebarg_extctx_ptr_acr2 = v
  else ()
}

function read_ebarg_extctx_meta_for_acr(acr : bits(4)) -> bits(64) = {
  if acr == 0x0 then ssr_ebarg_extctx_meta_acr0
  else if acr == 0x1 then ssr_ebarg_extctx_meta_acr1
  else if acr == 0x2 then ssr_ebarg_extctx_meta_acr2
  else 0x0000_0000_0000_0000
}

function write_ebarg_extctx_meta_for_acr(acr : bits(4), v : bits(64)) -> unit = {
  if acr == 0x0 then ssr_ebarg_extctx_meta_acr0 = v
  else if acr == 0x1 then ssr_ebarg_extctx_meta_acr1 = v
  else if acr == 0x2 then ssr_ebarg_extctx_meta_acr2 = v
  else ()
}

function ecstate_target_acr(v : bits(64)) -> bits(4) = { v[3..0] }
function ecstate_bi(v : bits(64)) -> bool = { v[4] == 0b1 }

function record_xb_dispatch(acr : bits(4), cid : bits(7), entry_ea : bits(64), word0 : bits(64)) -> unit = {
  xb_dispatch_valid = true;
  xb_dispatch_acr = acr;
  xb_dispatch_cid = cid;
  xb_dispatch_entry_ea = entry_ea;
  xb_dispatch_entry_word0 = word0
}

// -----------------------------------------------------------------------------
// ILLEGAL_INST / E_INST helpers (current v0.56 bring-up contract)
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
function trapnum_data_page_fault() -> bits(6) = { (sail_zeros(6) + 35) }

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

function trap_data_page_fault(fault_va : bits(64)) -> unit = {
  // Bring-up profile: use DATA_PAGE_FAULT for MMU/IOMMU translation faults.
  // CAUSE remains profile-defined; keep it zeroed in the staged Sail model.
  raise_trap(trapnum_data_page_fault(), sail_zeros(24), fault_va, 0b0)
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
    0xF00 => read_ecstate_for_acr(current_acr_id()),
    0xF07 => {
      let cur_acr : bits(4) = current_acr_id();
      if cur_acr == 0x0 then ssr_econfig_acr0
      else if cur_acr == 0x1 then ssr_econfig_acr1
      else if cur_acr == 0x2 then ssr_econfig_acr2
      else 0x0000_0000_0000_0000
    },
    0xF41 => read_ebarg_bpc_cur_for_acr(current_acr_id()),
    0xF42 => read_ebarg_bpc_tgt_for_acr(current_acr_id()),
    0xF43 => read_ebarg_tpc_for_acr(current_acr_id()),
    0xF4F => read_ebarg_extctx_ptr_for_acr(current_acr_id()),
    0xF50 => read_ebarg_extctx_meta_for_acr(current_acr_id()),

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
    0xF00 => write_ecstate_for_acr(current_acr_id(), v),
    0xF07 => {
      let cur_acr : bits(4) = current_acr_id();
      if cur_acr == 0x0 then ssr_econfig_acr0 = v
      else if cur_acr == 0x1 then ssr_econfig_acr1 = v
      else if cur_acr == 0x2 then ssr_econfig_acr2 = v
      else trap_illegal_ssr()
    },
    0xF41 => write_ebarg_bpc_cur_for_acr(current_acr_id(), v),
    0xF42 => write_ebarg_bpc_tgt_for_acr(current_acr_id(), v),
    0xF43 => write_ebarg_tpc_for_acr(current_acr_id(), v),
    0xF4F => write_ebarg_extctx_ptr_for_acr(current_acr_id(), v),
    0xF50 => write_ebarg_extctx_meta_for_acr(current_acr_id(), v),

    0xF30 => {
      let cur_acr : bits(4) = current_acr_id();
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
// CSTATE floating-point control/status fields (v0.56 staged profile)
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
// BLOCK_TRAP / E_BLOCK helpers (v0.56 bring-up contract)
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
// Block boundary + BARG state (current v0.56 bring-up contract)
//
// The Sail model keeps an explicit architectural BARG shadow so block-control
// instructions have concrete semantics even before fetch/decode is fully wired.
// Decoder/fetch-specific details (branch-kind decode, resolved target labels,
// descriptor immediates) are supplied through shadow registers below.

type block_type = bits(4)
type block_xfer_kind = bits(4)

register barg_valid : bool = false
register barg_block_type_cur : block_type = 0b0000
register barg_xfer_kind_cur : block_xfer_kind = 0b0000
register barg_bpc_cur : bits(64) = 0x0000_0000_0000_0000
register barg_bpc_tgt : bits(64) = 0x0000_0000_0000_0000
register barg_last_committed_bpc : bits(64) = 0x0000_0000_0000_0000
register barg_last_committed_target : bits(64) = 0x0000_0000_0000_0000
register barg_commit_seqno : bits(64) = 0x0000_0000_0000_0000

function block_xfer_fall() -> block_xfer_kind = { 0b0000 }
function block_xfer_direct() -> block_xfer_kind = { 0b0001 }
function block_xfer_cond() -> block_xfer_kind = { 0b0010 }
function block_xfer_call() -> block_xfer_kind = { 0b0011 }
function block_xfer_ind() -> block_xfer_kind = { 0b0100 }
function block_xfer_icall() -> block_xfer_kind = { 0b0101 }
function block_xfer_ret() -> block_xfer_kind = { 0b0110 }

function barg_reset_at_block_start() -> unit = {
  barg_valid = true;
  barg_block_type_cur = 0b0000;
  barg_xfer_kind_cur = block_xfer_fall();
  barg_bpc_cur = read_pc_or_tpc();
  barg_bpc_tgt = 0x0000_0000_0000_0000;
  barg_carg = 0x0000_0000_0000_0000;
  barg_tgt_reg_valid = false;
  barg_tgt_reg = 0b00000
}

function barg_set_block_type(bt : block_type) -> unit = {
  barg_block_type_cur = bt
}

function barg_set_xfer_kind(k : block_xfer_kind) -> unit = {
  barg_xfer_kind_cur = k
}

function barg_set_next_pc_target(tgt : bits(64)) -> unit = {
  barg_bpc_tgt = tgt
}

function block_commit_boundary() -> unit = {
  if barg_valid then {
    var take_target : bool = false;
    var target_pc : bits(64) = barg_bpc_tgt;

    if barg_xfer_kind_cur == block_xfer_direct() then {
      take_target = true
    } else if barg_xfer_kind_cur == block_xfer_call() then {
      take_target = true
    } else if barg_xfer_kind_cur == block_xfer_cond() then {
      take_target = barg_carg != 0x0000_0000_0000_0000
    } else if (barg_xfer_kind_cur == block_xfer_ind()) | (barg_xfer_kind_cur == block_xfer_icall()) | (barg_xfer_kind_cur == block_xfer_ret()) then {
      if barg_tgt_reg_valid then {
        take_target = true;
        target_pc = read_reg5(barg_tgt_reg)
      } else ()
    } else ();

    barg_last_committed_bpc = barg_bpc_cur;
    barg_last_committed_target = if take_target then target_pc else barg_bpc_cur;
    barg_commit_seqno = barg_commit_seqno + 0x0000_0000_0000_0001;

    if take_target then {
      pc = target_pc;
      tpc = target_pc
    } else ();

    barg_valid = false
  } else ()
}

// Decoded immediate/target helpers for block markers.
// The decoder/fetch layer is responsible for computing the architectural target address
// (e.g. PC-relative label resolved to an address).
register decoded_block_target_pc_shadow : bits(64) = 0x0000_0000_0000_0000
register decoded_block_type_shadow : block_type = 0b0000
register decoded_block_xfer_kind_shadow : block_xfer_kind = 0b0000
register decoded_block_contract_kind_shadow : bits(4) = 0b0000
register block_marker_strict : bool = false
register block_marker0_valid : bool = false
register block_marker0_pc : bits(64) = 0x0000_0000_0000_0000
register block_marker1_valid : bool = false
register block_marker1_pc : bits(64) = 0x0000_0000_0000_0000
register block_marker2_valid : bool = false
register block_marker2_pc : bits(64) = 0x0000_0000_0000_0000
register block_marker3_valid : bool = false
register block_marker3_pc : bits(64) = 0x0000_0000_0000_0000

function decoded_block_target_pc() -> bits(64) = {
  decoded_block_target_pc_shadow
}

function decoded_block_type() -> block_type = {
  decoded_block_type_shadow
}

function decoded_block_xfer_kind() -> block_xfer_kind = {
  decoded_block_xfer_kind_shadow
}

// CFI check hook: return true iff `addr` is a legal block start marker.
function is_block_start_marker(addr : bits(64)) -> bool = {
  if not_bool(block_marker_strict) then addr[0] == 0b0
  else ((block_marker0_valid & (block_marker0_pc == addr))
     |  (block_marker1_valid & (block_marker1_pc == addr))
     |  (block_marker2_valid & (block_marker2_pc == addr))
     |  (block_marker3_valid & (block_marker3_pc == addr)))
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
//   1=B.DIM, 2=B.TEXT, 3=B.ARG, 4=B.IOR, 5=B.IOT
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
  bdesc_seen_iot = false;
  clear_ri_bindings()
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
  decoded_block_contract_kind_shadow
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

function read_econfig() -> bits(64) = {
  let cur_acr : bits(4) = ssr_cstate[3..0];
  if cur_acr == 0x0 then ssr_econfig_acr0
  else if cur_acr == 0x1 then ssr_econfig_acr1
  else if cur_acr == 0x2 then ssr_econfig_acr2
  else 0x0000_0000_0000_0000
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


// Memory accessors (host hooks).
// Translation, permission checks, and detailed fault behavior are provided by the
// host integration used to execute the Sail model.

val mem_read8 = impure "linx_mem_read8" : bits(64) -> bits(8)
val mem_write8 = impure "linx_mem_write8" : (bits(64), bits(8)) -> unit
val mem_load16_le = impure "linx_mem_load16_le" : bits(64) -> bits(16)
val mem_load32_le = impure "linx_mem_load32_le" : bits(64) -> bits(32)
val mem_load64_le = impure "linx_mem_load64_le" : bits(64) -> bits(64)
val mem_store16_le = impure "linx_mem_store16_le" : (bits(64), bits(16)) -> unit
val mem_store32_le = impure "linx_mem_store32_le" : (bits(64), bits(32)) -> unit
val mem_store64_le = impure "linx_mem_store64_le" : (bits(64), bits(64)) -> unit

function read_mem8(ea : bits(64)) -> bits(8) = {
  mem_read8(ea)
}

function write_mem8(ea : bits(64), v : bits(8)) -> unit = {
  mem_write8(ea, v)
}
