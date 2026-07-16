// Directed executable checks for the canonical LinxISA v0.56.5 Sail model.

$include "../model/linxisa.sail"

function reset_fused_call_case(base_pc : bits(64), ra_seed : bits(64)) -> unit = {
  pc = base_pc;
  tpc = base_pc;
  write_reg5(0b01010, ra_seed);
  barg_valid = false;
  barg_block_type_cur = 0b0000;
  barg_xfer_kind_cur = block_xfer_fall();
  barg_bpc_cur = sail_zeros(64);
  barg_bpc_tgt = sail_zeros(64);
  barg_last_committed_bpc = sail_zeros(64);
  barg_last_committed_target = sail_zeros(64);
  barg_commit_seqno = sail_zeros(64);
  barg_carg = sail_zeros(64);
  barg_tgt_reg_valid = false;
  barg_tgt_reg = 0b00000;
  decoded_block_target_pc_shadow = sail_zeros(64);
  decoded_block_type_shadow = 0b0000;
  decoded_block_xfer_kind_shadow = block_xfer_fall();
  decoded_block_contract_kind_shadow = 0b0000;
  block_marker_strict = false;
  block_marker0_valid = false;
  block_marker1_valid = false;
  block_marker2_valid = false;
  block_marker3_valid = false;
  last_trapnum = sail_zeros(6);
  bdesc_reset()
}

function main() : unit -> unit = {
  // Long block targets are signed, halfword-scaled PC-relative offsets.
  pc = 0x0000_0000_0000_1000;
  assert(decode_block_target42(sail_zeros(42) + 1) == 0x0000_0000_0000_1002);
  assert(decode_block_target42(not_vec(sail_zeros(42))) == 0x0000_0000_0000_0FFE);

  // Generic bare calls preserve RA.  Keep this case isolated from the exact
  // aggregate raw-word corpus below.
  reset_fused_call_case(0x0000_0000_0000_1000, 0x1122_3344_5566_7788);
  decoded_block_target_pc_shadow = 0x0000_0000_0000_2000;
  decoded_block_type_shadow = 0b0000;
  decoded_block_xfer_kind_shadow = block_xfer_call();
  exec_bstart_std();
  assert(read_reg5(0b01010) == 0x1122_3344_5566_7788);
  assert(barg_valid);
  assert(barg_xfer_kind_cur == block_xfer_call());
  assert(barg_bpc_tgt == 0x0000_0000_0000_2000);

  // 32-bit exact aggregate, raw decode: simm12=2, uimm5=3.
  reset_fused_call_case(0x0000_0000_0000_1000, 0xAAAA_AAAA_AAAA_AAAA);
  decode_execute32(0x50D6_0022);
  assert(read_reg5(0b01010) == 0x0000_0000_0000_1008);
  assert(pc == 0x0000_0000_0000_1000);
  assert(barg_valid);
  assert(barg_xfer_kind_cur == block_xfer_call());
  assert(barg_bpc_cur == 0x0000_0000_0000_1000);
  assert(barg_bpc_tgt == 0x0000_0000_0000_1004);

  // Same simm12, uimm5=29: call target is invariant, only ra changes.
  reset_fused_call_case(0x0000_0000_0000_1000, 0xBBBB_BBBB_BBBB_BBBB);
  decode_execute32(0x5756_0022);
  assert(barg_bpc_tgt == 0x0000_0000_0000_1004);
  assert(read_reg5(0b01010) == 0x0000_0000_0000_103C);

  // Same uimm5=3, simm12=-1: ra is invariant, only call target changes.
  reset_fused_call_case(0x0000_0000_0000_1000, 0xCCCC_CCCC_CCCC_CCCC);
  decode_execute32(0x50D6_FFF2);
  assert(barg_bpc_tgt == 0x0000_0000_0000_0FFE);
  assert(read_reg5(0b01010) == 0x0000_0000_0000_1008);

  // 48-bit exact aggregate, raw decode: simm25=2, uimm5=5.  The return
  // calculation must use the embedded C.SETRET position P+4, not P+2.
  reset_fused_call_case(0x0000_0000_0000_1000, 0xDDDD_DDDD_DDDD_DDDD);
  decode_execute48(0x5156_0000_0111);
  assert(read_reg5(0b01010) == 0x0000_0000_0000_100E);
  assert(pc == 0x0000_0000_0000_1000);
  assert(barg_valid);
  assert(barg_xfer_kind_cur == block_xfer_call());
  assert(barg_bpc_cur == 0x0000_0000_0000_1000);
  assert(barg_bpc_tgt == 0x0000_0000_0000_1004);

  // Same simm25, uimm5=31: call target is invariant, only ra changes.
  reset_fused_call_case(0x0000_0000_0000_1000, 0xEEEE_EEEE_EEEE_EEEE);
  decode_execute48(0x57D6_0000_0111);
  assert(barg_bpc_tgt == 0x0000_0000_0000_1004);
  assert(read_reg5(0b01010) == 0x0000_0000_0000_1042);

  // Same uimm5=5, simm25=-1: ra is invariant, only call target changes.
  reset_fused_call_case(0x0000_0000_0000_1000, 0xFFFF_FFFF_FFFF_FFFF);
  decode_execute48(0x5156_FFFF_FF91);
  assert(barg_bpc_tgt == 0x0000_0000_0000_0FFE);
  assert(read_reg5(0b01010) == 0x0000_0000_0000_100E);

  // Standalone SETRET forms retain their own current-instruction PC base.
  pc = 0x0000_0000_0000_1000;
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
