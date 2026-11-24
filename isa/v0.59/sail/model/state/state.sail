// LinxISA 0.59.1 architectural state. The decoder supplies shadow fields for block headers.

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
// Decoder-provided helpers for staged block-descriptor execution.
// The Sail model stores these in shadow registers so tests / a future decode
// layer can preload the already-decoded values without baking an ad hoc parser
// into the execution rules.
register decoded_bdim_index_shadow : bits(2) = 0b00
register decoded_bdim_value_shadow : bits(64) = 0x0000_0000_0000_0000
register decoded_bcatr_raw_shadow : bits(64) = 0x0000_0000_0000_0000
register decoded_bdatr_raw_shadow : bits(64) = 0x0000_0000_0000_0000
register decoded_biot_raw_shadow : bits(64) = 0x0000_0000_0000_0000
// PTO/Linx 0.58 absolute-index core-private Shared tile binding.
register shared_tile_binding_valid : bool = false
register shared_tile_binding_id : bits(8) = 0x00
register shared_tile_binding_pe_mode : bits(3) = 0b000
register shared_tile_binding_pe_mask : bits(4) = 0x0
register shared_tile_binding_size_code : bits(4) = 0x0
register decoded_tile_datatype_shadow : bits(5) = 0b00000
register decoded_bior_regsrc0_shadow : bits(5) = 0b00000
register decoded_bior_regsrc1_shadow : bits(5) = 0b00000
register decoded_bior_regsrc2_shadow : bits(5) = 0b00000
register decoded_bior_regdst_shadow  : bits(5) = 0b00000
register decoded_bior_execmask_shadow : bits(1) = 0b0

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

function decoded_biot_raw() -> bits(64) = { decoded_biot_raw_shadow }
function decoded_tile_datatype() -> bits(5) = { decoded_tile_datatype_shadow }

function decoded_bior_regsrc0() -> bits(5) = { decoded_bior_regsrc0_shadow }
function decoded_bior_regsrc1() -> bits(5) = { decoded_bior_regsrc1_shadow }
function decoded_bior_regsrc2() -> bits(5) = { decoded_bior_regsrc2_shadow }
function decoded_bior_regdst()  -> bits(5) = { decoded_bior_regdst_shadow }
function decoded_bior_execmask() -> bits(1) = { decoded_bior_execmask_shadow }

function set_decoded_bior(regsrc0 : bits(5), regsrc1 : bits(5), regsrc2 : bits(5), regdst : bits(5), execmask : bits(1)) -> unit = {
  decoded_bior_regsrc0_shadow = regsrc0;
  decoded_bior_regsrc1_shadow = regsrc1;
  decoded_bior_regsrc2_shadow = regsrc2;
  decoded_bior_regdst_shadow = regdst;
  decoded_bior_execmask_shadow = execmask
}

// Latched B.CATR/B.DATR state relevant to VEC bring-up.
register bcatr_raw : bits(64) = 0x0000_0000_0000_0000
register bdatr_raw : bits(64) = 0x0000_0000_0000_0000
register bfpatr_pre_quant_mode : bits(6) = 0b00_0000
register bfpatr_relu_mode : bits(3) = 0b000
register bfpatr_group_n_code : bits(4) = 0x0
register bfpatr_row_max_en : bool = false
register bfpatr_group_max_en : bool = false
register bfpatr_row_max_init : bool = false
register bfpatr_max_abs_en : bool = false
register bfpatr_trans_a : bool = false
register bfpatr_trans_b : bool = false
function bcatr_dr() -> bool = { bcatr_raw[26] == 0b1 }
function bdatr_sat() -> bool = { bdatr_raw[26] == 0b1 }

// -----------------------------------------------------------------------------
// Tile-engine architectural effect envelope (PTO ISA 0.58 subset)
//
// The current Sail carrier does not yet contain a byte-addressable Tile payload
// array.  These registers nevertheless model the architectural transaction:
// decoded family/function and DataType, B.IOT legality/lifetime facts, complete
// preflight, memory/Tile/implicit-ACC publication, and full-instruction retry.
// Payload arithmetic remains a separately graded numeric-oracle gap.

register tile_effect_pending : bool = false
register tile_effect_family : bits(2) = 0b00 // 1=TLSU, 2=CUBE
register tile_effect_function : bits(5) = 0b00000
register tile_effect_datatype : bits(5) = 0b00000
register tile_effect_iot_count : bits(6) = 0b00_0000
register tile_effect_pe_mode_valid : bool = false
register tile_effect_pe_mode : bits(3) = 0b000
register tile_effect_pe_mask : bits(4) = 0x0
register tile_effect_source_count : bits(6) = 0b00_0000
register tile_effect_output_count : bits(6) = 0b00_0000
register tile_effect_release_count : bits(6) = 0b00_0000
register tile_effect_iot_legal : bool = true
register tile_effect_last_seen : bool = false
register tile_effect_after_last : bool = false
register tile_effect_access_set_valid : bool = true
register tile_effect_fault_address : bits(64) = 0x0000_0000_0000_0000
register tile_effect_restart_pending : bool = false

register tile_effect_commit_seq : bits(64) = 0x0000_0000_0000_0000
register tile_effect_preflight_seq : bits(64) = 0x0000_0000_0000_0000
register tile_effect_memory_seq : bits(64) = 0x0000_0000_0000_0000
register tile_effect_tile_seq : bits(64) = 0x0000_0000_0000_0000
register tile_effect_acc_seq : bits(64) = 0x0000_0000_0000_0000
register tile_effect_lifetime_releases : bits(64) = 0x0000_0000_0000_0000
register tile_effect_last_family : bits(2) = 0b00
register tile_effect_last_function : bits(5) = 0b00000
register tile_effect_last_datatype : bits(5) = 0b00000
register tile_effect_last_masked : bool = false
register tile_effect_last_mask_suppresses_access : bool = false
register tile_effect_last_pad : bits(2) = 0b00
register tile_effect_last_mx : bool = false
register tile_effect_last_bias : bool = false
register tile_effect_last_accumulate : bool = false
register tile_effect_last_scale_a_rows : bits(64) = 0x0000_0000_0000_0000
register tile_effect_last_scale_a_cols : bits(64) = 0x0000_0000_0000_0000
register tile_effect_last_scale_b_rows : bits(64) = 0x0000_0000_0000_0000
register tile_effect_last_scale_b_cols : bits(64) = 0x0000_0000_0000_0000
register tile_effect_last_scale_a_source : bits(6) = 0b00_0000
register tile_effect_last_scale_b_source : bits(6) = 0b00_0000

register tile_acc_valid : bool = false
register tile_acc_datatype : bits(5) = 0b00000
register tile_acc_rows : bits(64) = 0x0000_0000_0000_0000
register tile_acc_cols : bits(64) = 0x0000_0000_0000_0000
register tile_acc_k : bits(64) = 0x0000_0000_0000_0000

function tile_effect_reset_descriptors() -> unit = {
  tile_effect_iot_count = 0b00_0000;
  tile_effect_pe_mode_valid = false;
  tile_effect_pe_mode = 0b000;
  tile_effect_pe_mask = 0x0;
  tile_effect_source_count = 0b00_0000;
  tile_effect_output_count = 0b00_0000;
  tile_effect_release_count = 0b00_0000;
  tile_effect_iot_legal = true;
  tile_effect_last_seen = false;
  tile_effect_after_last = false
}

function tile_effect_reset_arch() -> unit = {
  tile_effect_pending = false;
  tile_effect_family = 0b00;
  tile_effect_function = 0b00000;
  tile_effect_datatype = 0b00000;
  tile_effect_reset_descriptors();
  tile_effect_access_set_valid = true;
  tile_effect_fault_address = sail_zeros(64);
  tile_effect_restart_pending = false;
  tile_effect_commit_seq = sail_zeros(64);
  tile_effect_preflight_seq = sail_zeros(64);
  tile_effect_memory_seq = sail_zeros(64);
  tile_effect_tile_seq = sail_zeros(64);
  tile_effect_acc_seq = sail_zeros(64);
  tile_effect_lifetime_releases = sail_zeros(64);
  tile_effect_last_family = 0b00;
  tile_effect_last_function = 0b00000;
  tile_effect_last_datatype = 0b00000;
  tile_effect_last_masked = false;
  tile_effect_last_mask_suppresses_access = false;
  tile_effect_last_pad = 0b00;
  tile_effect_last_mx = false;
  tile_effect_last_bias = false;
  tile_effect_last_accumulate = false;
  tile_effect_last_scale_a_rows = sail_zeros(64);
  tile_effect_last_scale_a_cols = sail_zeros(64);
  tile_effect_last_scale_b_rows = sail_zeros(64);
  tile_effect_last_scale_b_cols = sail_zeros(64);
  tile_effect_last_scale_a_source = 0b00_0000;
  tile_effect_last_scale_b_source = 0b00_0000;
  tile_acc_valid = false;
  tile_acc_datatype = 0b00000;
  tile_acc_rows = sail_zeros(64);
  tile_acc_cols = sail_zeros(64);
  tile_acc_k = sail_zeros(64)
}

// False mask lanes are architecturally silent: no source read, memory access,
// destination write, or fault check.  The bit result makes this contract easy
// to exercise without pretending the model has a numeric Tile payload.
function tile_mask_lane_effect(active : bool) -> bits(4) = {
  if active then 0b1111 else 0b0000
}

// Block-local dimensions retained for PTO Tile headers.
register ssr_lb0 : bits(64) = 0x0000_0000_0000_0001
register ssr_lb1 : bits(64) = 0x0000_0000_0000_0001
register ssr_lb2 : bits(64) = 0x0000_0000_0000_0001

// PTO BLOCKNUM/BLOCKID are read-only launch-context registers. The staged
// model exposes the reset/ambient values; future HSCB state can update these
// two registers when an actual worker dispatch is modeled.
register ssr_blocknum : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0050 (RO)
register ssr_blockid  : bits(64) = 0x0000_0000_0000_0000 // SSR_ID 0x0051 (RO)

function read_blocknum() -> bits(64) = { ssr_blocknum }
function read_blockid() -> bits(64) = { ssr_blockid }

// -----------------------------------------------------------------------------
// Minimal trap plumbing for bring-up.
// Record the last trap request so tests can observe it.
register last_trapnum  : bits(6)  = sail_zeros(6)
register last_cause    : bits(24) = sail_zeros(24)
register last_traparg0 : bits(64) = 0x0000_0000_0000_0000
register last_bi       : bits(1)  = 0b0
register last_e        : bits(1)  = 0b0
register last_argv     : bits(1)  = 0b0

function raise_trap_full(
  e : bits(1),
  argv : bits(1),
  trapnum : bits(6),
  cause : bits(24),
  traparg0 : bits(64),
  bi : bits(1)
) -> unit = {
  last_e        = e;
  last_argv     = argv;
  last_trapnum  = trapnum;
  last_cause    = cause;
  last_traparg0 = traparg0;
  last_bi       = bi
}

function raise_trap(trapnum : bits(6), cause : bits(24), traparg0 : bits(64), bi : bits(1)) -> unit = {
  raise_trap_full(0b1, 0b1, trapnum, cause, traparg0, bi)
}

// -----------------------------------------------------------------------------
// System Status Registers (SSR) - bring-up state model
//
// Normative sources:
// - isa/v0.59/state/pto_system_registers.json
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
register ssr_econfig_acr0 : bits(64) = 0x0000_0003_0000_0008 // SSR_ID 0x0F07
register ssr_econfig_acr1 : bits(64) = 0x0000_0003_0000_0008 // SSR_ID 0x1F07
register ssr_econfig_acr2 : bits(64) = 0x0000_0003_0000_0008 // SSR_ID 0x2F07
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
// Block-local dimensions are declared with the block descriptor state.

// -----------------------------------------------------------------------------
// XBINFO / CAC_TABLE (current v0.58 architecture profile)
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
// The generic v0.57 architecture standardizes legality, permission, and
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
// Existing E_INST helpers plus the scoped v0.58.1 first-use trap.
//
// The generic staged illegal-instruction path remains unchanged.  First use
// has its own exact E_INST(0), raw EC_PERM(4) envelope.

function trapnum_e_inst() -> bits(6) = { sail_zeros(6) }
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
  trap_e_inst(0x01, 0x00, traparg0)
}

function trap_data_page_fault(fault_va : bits(64)) -> unit = {
  // Bring-up profile: use DATA_PAGE_FAULT for MMU/IOMMU translation faults.
  // CAUSE remains profile-defined; keep it zeroed in the staged Sail model.
  raise_trap(trapnum_data_page_fault(), sail_zeros(24), fault_va, 0b0)
}

function trap_illegal_ssr() -> unit = {
  trap_illegal_inst(read_pc_or_tpc())
}

function system_register_readable(id24 : bits(24)) -> bool = {
  let id : bits(12) = id24[11..0];
  match id {
    0x000 => true,
    0x001 => true,
    0x020 => true,
    0x024 => true,
    // These two base registers have exact 24-bit identities. In particular,
    // HL.SSRGET must not alias a nonzero upper address onto the base namespace.
    0x050 => id24 == 0x000050,
    0x051 => id24 == 0x000051,
    0xF00 => true,
    0xF07 => true,
    0xF30 => true,
    0xF41 => true,
    0xF42 => true,
    0xF43 => true,
    0xF4F => true,
    0xF50 => true,
    _ => false
  }
}

function system_register_writable(id24 : bits(24)) -> bool = {
  let id : bits(12) = id24[11..0];
  match id {
    0x000 => true,
    0x001 => true,
    0x020 => true,
    0xF00 => true,
    0xF07 => true,
    0xF30 => true,
    0xF41 => true,
    0xF42 => true,
    0xF43 => true,
    0xF4F => true,
    0xF50 => true,
    _ => false
  }
}

function read_system_register(id24 : bits(24)) -> bits(64) = {
  // Base SSR namespace is 12-bit for 32-bit forms.
  let id : bits(12) = id24[11..0];
  if not_bool(system_register_readable(id24)) then {
    trap_illegal_ssr();
    0x0000_0000_0000_0000
  } else match id {
    0x000 => ssr_tp,
    0x001 => ssr_gp,
    0x020 => ssr_cstate,
    0x050 => read_blocknum(),
    0x051 => read_blockid(),
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
  if not_bool(system_register_writable(id24)) then {
    trap_illegal_ssr()
  } else match id {
    0x000 => ssr_tp = v,
    0x001 => ssr_gp = v,
    0x020 => ssr_cstate = v,
    0xF00 => write_ecstate_for_acr(current_acr_id(), v),
    0xF07 => {
      let cur_acr : bits(4) = current_acr_id();
      let masked = v & 0x0000_0003_0000_000F;
      if cur_acr == 0x0 then ssr_econfig_acr0 = masked
      else if cur_acr == 0x1 then ssr_econfig_acr1 = masked
      else if cur_acr == 0x2 then ssr_econfig_acr2 = masked
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
  if not_bool(system_register_readable(id24) & system_register_writable(id24)) then {
    trap_illegal_ssr();
    0x0000_0000_0000_0000
  } else {
    let old = read_system_register(id24);
    write_system_register(id24, v);
    old
  }
}

// -----------------------------------------------------------------------------
// CSTATE floating-point control/status fields (v0.57 staged profile)
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
// BLOCK_TRAP / E_BLOCK helpers (v0.58 architecture contract)
//
// Normative sources:
// - docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc
// - docs/architecture/v0.58-architecture-contract.md
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
// Block boundary + BARG state (current v0.58 architecture contract)
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

function set_commit_target_value(tgt : bits(64)) -> unit = {
  barg_tgt_reg_valid = false;
  barg_tgt_reg = 0b00000;
  barg_bpc_tgt = tgt;
  barg_xfer_kind_cur = block_xfer_direct()
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
// Generic block-control tests may use the relaxed hook. FRET template
// admission uses its own proof-only predicate in execute.sail.
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

// Architectural frame-template progress state and deterministic model hooks.
// Form IDs: 0=invalid, 1=FENTRY, 2=FEXIT, 3=FRET.RA, 4=FRET.STK.
register template_valid : bool = false
register template_form : bits(3) = 0b000
register template_phase : bits(2) = 0b00
register template_step_index : bits(8) = 0x00
register template_event_count : bits(8) = 0x00
register template_dirty : bool = false
register template_redo_ok : bool = false
register template_resume_ok : bool = false
register template_source_pc : bits(64) = 0x0000_0000_0000_0000
register template_begin : bits(5) = 0b00000
register template_end : bits(5) = 0b00000
register template_nregs : bits(8) = 0x00
register template_frame_f : bits(64) = 0x0000_0000_0000_0000
register template_sp_a : bits(64) = 0x0000_0000_0000_0000
register template_sp_c : bits(64) = 0x0000_0000_0000_0000
register template_retained_target : bits(64) = 0x0000_0000_0000_0000
register template_retained_slot0 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value0 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value1 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value2 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value3 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value4 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value5 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value6 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value7 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value8 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value9 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value10 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value11 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value12 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value13 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value14 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value15 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value16 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value17 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value18 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value19 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value20 : bits(64) = 0x0000_0000_0000_0000
register template_saved_value21 : bits(64) = 0x0000_0000_0000_0000
register template_fatal_reason : bits(8) = 0x00

// Explicit FRET.STK slot-zero admission evidence. The fail-closed default is
// unknown; only 1 proves a complete eight-byte Normal, idempotent access.
// 0=unknown, 1=Normal+idempotent, 2=Device/MMIO, 3=mixed,
// 4=unspecified/non-idempotent.
register template_vload_class : bits(3) = 0b000
register template_data_fault_step : bits(8) = 0xFF
register template_interrupt_step : bits(8) = 0xFF
register template_interrupt_id : bits(8) = 0x00
register template_memory_hook_enabled : bool = false
register template_memory_hook_load_value : bits(64) = 0x0000_0000_0000_0000

register template_last_event_kind : bits(8) = 0x00
register template_last_interrupted_event_kind : bits(8) = 0x00
register template_event_commit_count : bits(64) = 0x0000_0000_0000_0000
register template_final_count : bits(64) = 0x0000_0000_0000_0000
register template_vload_read_count : bits(64) = 0x0000_0000_0000_0000
register template_vload_forbidden_zero_read_count : bits(64) = 0x0000_0000_0000_0000
register template_vload_admission_check_count : bits(64) = 0x0000_0000_0000_0000
register template_marker_check_count : bits(64) = 0x0000_0000_0000_0000
register template_data_fault_injection_count : bits(64) = 0x0000_0000_0000_0000
register template_data_fault_ignored_count : bits(64) = 0x0000_0000_0000_0000
register template_interrupt_count : bits(64) = 0x0000_0000_0000_0000
register template_target_publish_count : bits(64) = 0x0000_0000_0000_0000
register template_restore_r10_count : bits(64) = 0x0000_0000_0000_0000
register template_memory_hook_load_count : bits(64) = 0x0000_0000_0000_0000
register template_memory_hook_store_count : bits(64) = 0x0000_0000_0000_0000

function template_clear() -> unit = {
  template_valid = false;
  template_form = 0b000;
  template_phase = 0b00;
  template_step_index = 0x00;
  template_event_count = 0x00;
  template_dirty = false;
  template_redo_ok = false;
  template_resume_ok = false;
  template_fatal_reason = 0x00
}

function template_record_phase0(form : bits(3), src_pc : bits(64)) -> unit = {
  template_valid = true;
  template_form = form;
  template_phase = 0b00;
  template_step_index = 0x00;
  template_event_count = 0x00;
  template_dirty = false;
  template_redo_ok = true;
  template_resume_ok = false;
  template_source_pc = src_pc;
  template_retained_target = 0x0000_0000_0000_0000;
  template_retained_slot0 = 0x0000_0000_0000_0000
}

function template_enter_phase1(form : bits(3), src_pc : bits(64), begin : bits(5), endv : bits(5), nregs : int, f : int, sp_a : bits(64), sp_c : bits(64), event_count : int) -> unit = {
  template_valid = true;
  template_form = form;
  template_phase = 0b01;
  template_step_index = 0x00;
  template_event_count = sail_zeros(8) + event_count;
  template_dirty = true;
  template_redo_ok = false;
  template_resume_ok = true;
  template_source_pc = src_pc;
  template_begin = begin;
  template_end = endv;
  template_nregs = sail_zeros(8) + nregs;
  template_frame_f = sail_zeros(64) + f;
  template_sp_a = sp_a;
  template_sp_c = sp_c
}

function template_raise_phase1_data_fault(faultarg : bits(64)) -> unit = {
  template_phase = 0b01;
  template_dirty = true;
  template_redo_ok = false;
  template_resume_ok = true;
  template_data_fault_injection_count = template_data_fault_injection_count + 0x0000_0000_0000_0001;
  raise_trap(trapnum_data_page_fault(), sail_zeros(24), faultarg, 0b1)
}

function template_raise_phase1_interrupt(event_kind : bits(8)) -> unit = {
  template_phase = 0b01;
  template_dirty = true;
  template_redo_ok = false;
  template_resume_ok = true;
  template_last_interrupted_event_kind = event_kind;
  template_interrupt_count = template_interrupt_count + 0x0000_0000_0000_0001;
  raise_trap((sail_zeros(6) + 44), sail_zeros(24), sail_zero_extend(template_interrupt_id, 64), 0b1)
}

function template_trap_vload_mmu_perm(fault_va : bits(64)) -> unit = {
  // DATA_PAGE_FAULT load permission syndrome in the active v0.58 profile.
  raise_trap(trapnum_data_page_fault(), (sail_zeros(24) + 2), fault_va, 0b0)
}

function template_set_saved_value(idx : int, v : bits(64)) -> unit = {
  if idx == 0 then template_saved_value0 = v
  else if idx == 1 then template_saved_value1 = v
  else if idx == 2 then template_saved_value2 = v
  else if idx == 3 then template_saved_value3 = v
  else if idx == 4 then template_saved_value4 = v
  else if idx == 5 then template_saved_value5 = v
  else if idx == 6 then template_saved_value6 = v
  else if idx == 7 then template_saved_value7 = v
  else if idx == 8 then template_saved_value8 = v
  else if idx == 9 then template_saved_value9 = v
  else if idx == 10 then template_saved_value10 = v
  else if idx == 11 then template_saved_value11 = v
  else if idx == 12 then template_saved_value12 = v
  else if idx == 13 then template_saved_value13 = v
  else if idx == 14 then template_saved_value14 = v
  else if idx == 15 then template_saved_value15 = v
  else if idx == 16 then template_saved_value16 = v
  else if idx == 17 then template_saved_value17 = v
  else if idx == 18 then template_saved_value18 = v
  else if idx == 19 then template_saved_value19 = v
  else if idx == 20 then template_saved_value20 = v
  else if idx == 21 then template_saved_value21 = v
  else ()
}

function template_get_saved_value(idx : int) -> bits(64) = {
  if idx == 0 then template_saved_value0
  else if idx == 1 then template_saved_value1
  else if idx == 2 then template_saved_value2
  else if idx == 3 then template_saved_value3
  else if idx == 4 then template_saved_value4
  else if idx == 5 then template_saved_value5
  else if idx == 6 then template_saved_value6
  else if idx == 7 then template_saved_value7
  else if idx == 8 then template_saved_value8
  else if idx == 9 then template_saved_value9
  else if idx == 10 then template_saved_value10
  else if idx == 11 then template_saved_value11
  else if idx == 12 then template_saved_value12
  else if idx == 13 then template_saved_value13
  else if idx == 14 then template_saved_value14
  else if idx == 15 then template_saved_value15
  else if idx == 16 then template_saved_value16
  else if idx == 17 then template_saved_value17
  else if idx == 18 then template_saved_value18
  else if idx == 19 then template_saved_value19
  else if idx == 20 then template_saved_value20
  else if idx == 21 then template_saved_value21
  else 0x0000_0000_0000_0000
}

function template_integrity_assert_fail(reason : bits(8)) -> unit = {
  template_valid = true;
  if template_phase == 0b00 then template_phase = 0b01 else ();
  template_dirty = true;
  template_redo_ok = false;
  template_resume_ok = false;
  template_fatal_reason = reason;
  raise_trap((sail_zeros(6) + 52), (sail_zeros(24) + 0), template_source_pc, 0b1)
}

// -----------------------------------------------------------------------------
// Block header descriptor validation (B.* stream)
//
// We model the mandatory-descriptor contracts for Tile headers as a
// fail-fast validation at the end of the header stream (at BSTOP / next BSTART).
//
// Normative sources:
// - docs/architecture/isa-manual/src/chapters/07_tile_blocks.adoc
// - docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc
// - docs/architecture/v0.58-architecture-contract.md
//
// MissingDescFamily IDs (TRAPARG0[7:0]):
//   1=B.DIM, 3=B.DATR, 4=B.IOR, 5=B.IOT, 6=B.FPATR
// MissingDetail (TRAPARG0[15:8]):
//   0x00 missing, 0x01 invalid/out-of-range, 0x02 illegal combination

register bdesc_seen_dim : bool = false
register bdesc_seen_datr : bool = false
register bdesc_seen_ior : bool = false
register bdesc_seen_iot : bool = false
register bdesc_seen_fpatr : bool = false

// B.IOR records retain selectors, not GPR values. The selected complete Tile
// schema consumes the records at completion and owns role/arity validation.
// Two records are needed by the published TGPR2T/TIMG2COL and GPR-mask forms.
register bior_record_count : bits(2) = 0b00
register bior0_regsrc0 : bits(5) = 0b00000
register bior0_regsrc1 : bits(5) = 0b00000
register bior0_regsrc2 : bits(5) = 0b00000
register bior0_regdst : bits(5) = 0b00000
register bior0_execmask : bits(1) = 0b0
register bior1_regsrc0 : bits(5) = 0b00000
register bior1_regsrc1 : bits(5) = 0b00000
register bior1_regsrc2 : bits(5) = 0b00000
register bior1_regdst : bits(5) = 0b00000
register bior1_execmask : bits(1) = 0b0

function bior_reset() -> unit = {
  bior_record_count = 0b00;
  bior0_regsrc0 = 0b00000;
  bior0_regsrc1 = 0b00000;
  bior0_regsrc2 = 0b00000;
  bior0_regdst = 0b00000;
  bior0_execmask = 0b0;
  bior1_regsrc0 = 0b00000;
  bior1_regsrc1 = 0b00000;
  bior1_regsrc2 = 0b00000;
  bior1_regdst = 0b00000;
  bior1_execmask = 0b0
}

function bior_store_record(regsrc0 : bits(5), regsrc1 : bits(5), regsrc2 : bits(5), regdst : bits(5), execmask : bits(1)) -> unit = {
  if bior_record_count == 0b00 then {
    bior0_regsrc0 = regsrc0;
    bior0_regsrc1 = regsrc1;
    bior0_regsrc2 = regsrc2;
    bior0_regdst = regdst;
    bior0_execmask = execmask;
    bior_record_count = 0b01
  } else {
    bior1_regsrc0 = regsrc0;
    bior1_regsrc1 = regsrc1;
    bior1_regsrc2 = regsrc2;
    bior1_regdst = regdst;
    bior1_execmask = execmask;
    bior_record_count = 0b10
  }
}

function bdesc_reset() -> unit = {
  // Missing DIM is architecturally identical to an explicit value one.
  ssr_lb0 = 0x0000_0000_0000_0001;
  ssr_lb1 = 0x0000_0000_0000_0001;
  ssr_lb2 = 0x0000_0000_0000_0001;
  bdesc_seen_dim = false;
  bdesc_seen_datr = false;
  bdesc_seen_ior = false;
  bdesc_seen_iot = false;
  bdesc_seen_fpatr = false;
  bior_reset();
  bfpatr_pre_quant_mode = 0b00_0000;
  bfpatr_relu_mode = 0b000;
  bfpatr_group_n_code = 0x0;
  bfpatr_row_max_en = false;
  bfpatr_group_max_en = false;
  bfpatr_row_max_init = false;
  bfpatr_max_abs_en = false;
  bfpatr_trans_a = false;
  bfpatr_trans_b = false;
  shared_tile_binding_valid = false;
  shared_tile_binding_id = 0x00;
  shared_tile_binding_pe_mode = 0b000;
  shared_tile_binding_pe_mask = 0x0;
  shared_tile_binding_size_code = 0x0;
  tile_effect_reset_descriptors()
}

function bdesc_mark_dim() -> unit = { bdesc_seen_dim = true }
function bdesc_mark_datr() -> unit = { bdesc_seen_datr = true }
function bdesc_mark_ior() -> unit = { bdesc_seen_ior = true }
function bdesc_mark_iot() -> unit = { bdesc_seen_iot = true }
function bdesc_mark_fpatr() -> unit = { bdesc_seen_fpatr = true }

// Block type classification for mandatory-descriptor contracts.
// The decoder provides a stable classification string for the staged model.
function decoded_block_contract_kind() -> bits(4) = {
  // 0=none/unspecified, 2=TLSU (TLOAD/TSTORE),
  // 3=TMOV, 4=CUBE, 6=HDRDRV (TEPL/FIXP/TLSU-other).
  // Kind 5 is intentionally unassigned in v0.58.
  decoded_block_contract_kind_shadow
}

function bdesc_require_or_trap(family : bits(8), present : bool, src_pc_or_tpc : bits(64)) -> unit = {
  if present then () else trap_blockfmt(family, 0x00, src_pc_or_tpc)
}

function bdesc_illegal_combo_or_trap(family : bits(8), src_pc_or_tpc : bits(64)) -> unit = {
  trap_blockfmt(family, 0x02, src_pc_or_tpc)
}

function bdesc_validate_header_end(src_pc_or_tpc : bits(64)) -> unit = {
  // Enforce mandatory descriptor families per Tile block type.
  // If multiple are missing, report exactly one using the priority order:
  //   B.DATR > B.IOT > B.IOR > B.DIM
  let k = decoded_block_contract_kind();
  match k {
    // TLSU: require DATR + IOR + IOT; TEXT illegal.
    0b0010 => {
      if not_bool(bdesc_seen_datr) then trap_blockfmt(0x03, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_iot) then trap_blockfmt(0x05, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_ior) then trap_blockfmt(0x04, 0x00, src_pc_or_tpc)
      else ()
    },
    // TMOV: require IOT; TEXT illegal.
    0b0011 => {
      if not_bool(bdesc_seen_iot) then trap_blockfmt(0x05, 0x00, src_pc_or_tpc)
      else ()
    },
    // CUBE: require IOT + DATR; omitted dimensions are one; TEXT is illegal.
    0b0100 => {
      if not_bool(bdesc_seen_datr) then trap_blockfmt(0x03, 0x00, src_pc_or_tpc)
      else if not_bool(bdesc_seen_iot) then trap_blockfmt(0x05, 0x00, src_pc_or_tpc)
      else ()
    },
    // HDRDRV: header-driven engine ops: TEXT illegal; mandatory families are op-specific.
    0b0110 => {
      ()
    },
    _ => ()
  }
}

function trap_assert_fail(traparg0 : bits(64)) -> unit = {
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

function cube_first_use_enabled() -> bool = {
  (current_acr_id() == 0x2) & (ssr_econfig_acr1[33] == 0b1)
}

function trap_cube_first_use() -> unit = {
  raise_trap_full(
    0b1,
    0b1,
    trapnum_e_inst(),
    (sail_zeros(24) + 4),
    0x0000_0000_0000_0001,
    0b0
  )
}


function trap_sw_breakpoint(traparg0 : bits(64)) -> unit = {
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
