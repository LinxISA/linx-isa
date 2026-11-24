// v0.59.1-only hard-break checks. This file is copied into the Sail export.

$include "../model/linxisa_v0591.sail"

function reset_v0591_hard_break_case() -> unit = {
  pc = 0x0000_0000_0000_1900;
  tpc = 0x0000_0000_0000_1900;
  last_e = 0b0;
  last_argv = 0b0;
  last_trapnum = sail_zeros(6);
  last_cause = sail_zeros(24);
  last_traparg0 = sail_zeros(64);
  write_reg5(0b00001, 0x1111_1111_1111_1111);
  write_reg5(0b00010, 0x2222_2222_2222_2222);
  write_reg5(0b00011, 0x3333_3333_3333_3333);
  ssr_cstate = 0x4444_4444_4444_4444;
  barg_bpc_cur = 0x5555_5555_5555_5555;
  barg_valid = false;
  tile_effect_reset_arch();
  bdesc_reset()
}

function assert_v0591_hard_break_state() -> unit = {
  assert(last_e == 0b1);
  assert(last_trapnum == trapnum_illegal_inst());
  assert(read_reg5(0b00001) == 0x1111_1111_1111_1111);
  assert(read_reg5(0b00010) == 0x2222_2222_2222_2222);
  assert(read_reg5(0b00011) == 0x3333_3333_3333_3333);
  assert(ssr_cstate == 0x4444_4444_4444_4444);
  assert(barg_bpc_cur == 0x5555_5555_5555_5555);
  assert(not_bool(barg_valid));
  assert(not_bool(tile_effect_pending));
  assert(not_bool(bdesc_seen_dim));
  assert(not_bool(bdesc_seen_datr));
  assert(not_bool(bdesc_seen_ior))
}

function assert_reserved16(word : bits(16)) -> unit = {
  reset_v0591_hard_break_case();
  decode_execute16(word);
  assert_v0591_hard_break_state()
}

function assert_reserved32(word : bits(32)) -> unit = {
  reset_v0591_hard_break_case();
  decode_execute32(word);
  assert_v0591_hard_break_state()
}

function assert_reserved64(word : bits(64)) -> unit = {
  reset_v0591_hard_break_case();
  decode_execute64(word);
  assert_v0591_hard_break_state()
}

function verify_v0591_hard_break() -> unit = {
  // Four compressed block entries.
  assert_reserved16(0x08C0);
  assert_reserved16(0x48C0);
  assert_reserved16(0x88C0);
  assert_reserved16(0xC8C0);

  // Four full-width block entries and the full B.TEXT opcode range.
  assert_reserved32(0x0000_1181);
  assert_reserved32(0x0000_9181);
  assert_reserved32(0x0002_1181);
  assert_reserved32(0x0002_9181);
  assert_reserved32(0xDEAD_BE03);

  // A value outside the former 184 rows still belongs to the V.* wildcard.
  assert_reserved64(0xDEAD_BEFF_0123_4567);

  // Current extension-owned forms reject before reading operands or changing state.
  assert_reserved32(0x0400_EF81); // XB
  assert_reserved32(0x1820_A031); // ESAVE
  assert_reserved32(0x1820_B031); // ERCOV

  // B.IOR accepts only absolute GPR selectors 0..23. It records selectors
  // without reading GPR values; ExecMaskPresent is retained for complete-
  // schema validation instead of being rejected by the common decoder.
  reset_v0591_hard_break_case();
  decode_execute32(0x0031_0213); // src={a0,a1,zero}, dst=a2
  assert(last_e == 0b0);
  assert(bior_record_count == 0b01);
  assert(bior0_regsrc0 == 0b00010 & bior0_regsrc1 == 0b00011);
  assert(bior0_regsrc2 == 0b00000 & bior0_regdst == 0b00100);
  assert(bior0_execmask == 0b0 & bdesc_seen_ior);
  assert(read_reg5(0b00010) == 0x2222_2222_2222_2222);
  assert(read_reg5(0b00011) == 0x3333_3333_3333_3333);

  reset_v0591_hard_break_case();
  decode_execute32(0x0401_0013); // first-record Base-plus-mask form
  assert(last_e == 0b0 & bior_record_count == 0b01);
  assert(bior0_execmask == 0b1);

  reset_v0591_hard_break_case();
  decode_execute32(0x0031_0213); // unflagged operation-owned record
  decode_execute32(0x0462_8013); // final source-only GPR mask record
  assert(last_e == 0b0 & bior_record_count == 0b10);
  assert(bior1_regsrc0 == 0b00101 & bior1_regsrc1 == 0b00110);
  assert(bior1_regsrc2 == 0b00000 & bior1_regdst == 0b00000);
  assert(bior1_execmask == 0b1);

  // A third record, or a record after an already-final mask record, rejects
  // before changing the previously accepted selector state.
  last_e = 0b0;
  last_trapnum = sail_zeros(6);
  decode_execute32(0x0000_0013);
  assert(last_e == 0b1 & last_trapnum == trapnum_block_trap());
  assert(bior_record_count == 0b10 & bior1_execmask == 0b1);
  reset_v0591_hard_break_case();
  decode_execute32(0x0401_0013);
  last_e = 0b0;
  last_trapnum = sail_zeros(6);
  decode_execute32(0x0000_0013);
  assert(last_e == 0b1 & last_trapnum == trapnum_block_trap());
  assert(bior_record_count == 0b01 & bior0_execmask == 0b1);

  // Each selector field independently rejects reserved codes 24..31 before
  // any B.IOR record is installed.
  assert_reserved32(0x0000_0C13); // RegDst=24
  assert(bior_record_count == 0b00);
  assert_reserved32(0x000C_0013); // RegSrc0=24
  assert(bior_record_count == 0b00);
  assert_reserved32(0x0180_0013); // RegSrc1=24
  assert(bior_record_count == 0b00);
  assert_reserved32(0xC000_0013); // RegSrc2=24
  assert(bior_record_count == 0b00);

  // F-H remain active: representative 48-bit HL and 64-bit L block entries
  // establish a block argument instead of falling into a reservation guard.
  reset_v0591_hard_break_case();
  decode_execute48(0x0000_1101_000E); // HL.BSTART.FP FALL
  assert(last_e == 0b0);
  assert(barg_valid);
  reset_v0591_hard_break_case();
  decode_execute64(0x0000_000F_0000_1001); // L.BSTART.STD FALL
  assert(last_e == 0b0);
  assert(barg_valid);

  // Group I remains encoding-only and rejects before effects.
  reset_v0591_hard_break_case();
  exec_mcopy_ds(0b00100, 0b00001, 0b00010, 0b00011);
  assert_v0591_hard_break_state();
  reset_v0591_hard_break_case();
  exec_mcopy_dl(0b00100, 0b00001, 0b00010, 0b00011);
  assert_v0591_hard_break_state();
  reset_v0591_hard_break_case();
  exec_dma_free_s(0b00001);
  assert_v0591_hard_break_state();
  reset_v0591_hard_break_case();
  exec_dma_free_l(0b00001);
  assert_v0591_hard_break_state()
}

function main() : unit -> unit = {
  verify_v0591_hard_break()
}
