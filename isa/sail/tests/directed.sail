// Directed executable checks for the canonical LinxISA v0.56.5 Sail model.

$include "../model/linxisa.sail"

function main() : unit -> unit = {
  // Long block targets are signed, halfword-scaled PC-relative offsets.
  pc = 0x0000_0000_0000_1000;
  assert(decode_block_target42(sail_zeros(42) + 1) == 0x0000_0000_0000_1002);
  assert(decode_block_target42(not_vec(sail_zeros(42))) == 0x0000_0000_0000_0FFE);

  // Bare call block starts do not write RA; SETRET/C.SETRET do so explicitly.
  write_reg5(0b01010, 0x1122_3344_5566_7788);
  decoded_block_target_pc_shadow = 0x0000_0000_0000_2000;
  decoded_block_type_shadow = 0b0000;
  decoded_block_xfer_kind_shadow = block_xfer_call();
  block_marker_strict = false;
  exec_bstart_call();
  assert(read_reg5(0b01010) == 0x1122_3344_5566_7788);
  assert(barg_valid);
  assert(barg_xfer_kind_cur == block_xfer_call());
  assert(barg_bpc_tgt == 0x0000_0000_0000_2000);
  exec_setret(0x00003);
  assert(read_reg5(0b01010) == 0x0000_0000_0000_1006);
  exec_c_setret(0b00101);
  assert(read_reg5(0b01010) == 0x0000_0000_0000_100A);

  // Retired B.IOD encoding space must trap as illegal; the old PAR spelling is
  // not represented in Sail and its bit pattern decodes as canonical TEPL.
  last_trapnum = sail_zeros(6);
  decode_execute32(0x0000_1013);
  assert(last_trapnum == trapnum_illegal_inst());
  last_trapnum = sail_zeros(6);
  decode_execute32(0x0200_1181);
  assert(last_trapnum == sail_zeros(6));
  assert(barg_block_type_cur == 0b1011);

  // Trap records retain precise source state and the block-interrupted bit.
  trap_block_cfi(0x1, 0xCAFE_BABE_DEAD_BEEF);
  assert(last_trapnum == trapnum_block_trap());
  assert(last_traparg0 == 0xCAFE_BABE_DEAD_BEEF);
  assert(last_bi == 0b0);
  trap_bfetch(0x0000_0000_1234_5000);
  assert(last_bi == 0b1);
  assert(last_traparg0 == 0x0000_0000_1234_5000);

  // Atomic operation cores cover arithmetic, signed, and unsigned selection.
  assert(rmw64_add(0xFFFF_FFFF_FFFF_FFFF, 0x0000_0000_0000_0001) == 0x0000_0000_0000_0000);
  assert(rmw64_and(0xF0F0_F0F0_F0F0_F0F0, 0x0FF0_0FF0_0FF0_0FF0) == 0x00F0_00F0_00F0_00F0);
  assert(rmw64_smax(0xFFFF_FFFF_FFFF_FFFF, 0x0000_0000_0000_0001) == 0x0000_0000_0000_0001);
  assert(rmw64_umax(0xFFFF_FFFF_FFFF_FFFF, 0x0000_0000_0000_0001) == 0xFFFF_FFFF_FFFF_FFFF);

  // IEEE-754 edge cases: NaNs are unordered and signed zero compares equal.
  assert(fp32_is_nan(0x7FC0_0001));
  assert(not_bool(fp32_eq(0x7FC0_0001, 0x7FC0_0001)));
  assert(fp32_eq(0x0000_0000, 0x8000_0000));
  assert(fp32_class_mask(0x7F80_0000) == 0x0000_0080);
  assert(fp64_is_nan(0x7FF8_0000_0000_0001));
  assert(fp64_eq(0x0000_0000_0000_0000, 0x8000_0000_0000_0000))
}
