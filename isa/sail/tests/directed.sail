// Directed executable checks for the canonical LinxISA v0.58 Sail model.

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

function reset_tile_effect_case() -> unit = {
  tile_effect_reset_arch();
  bdesc_reset();
  bcatr_raw = sail_zeros(64);
  bdatr_raw = sail_zeros(64);
  ssr_lb0 = 0x0000_0000_0000_0002;
  ssr_lb1 = 0x0000_0000_0000_0003;
  ssr_lb2 = 0x0000_0000_0000_0041;
  last_trapnum = sail_zeros(6);
  block_marker_strict = false
}

function reset_first_use_case(base_pc : bits(64)) -> unit = {
  pc = base_pc;
  tpc = base_pc;
  ssr_cstate = 0x0000_0000_0000_0002;
  ssr_econfig_acr1 = 0x0000_0003_0000_0008;
  last_e = 0b0;
  last_argv = 0b0;
  last_trapnum = sail_zeros(6);
  last_cause = sail_zeros(24);
  last_traparg0 = sail_zeros(64);
  last_bi = 0b0;
  barg_valid = false;
  barg_commit_seqno = sail_zeros(64);
  barg_bpc_cur = sail_zeros(64);
  barg_bpc_tgt = sail_zeros(64);
  tile_effect_pending = false;
  tile_effect_commit_seq = sail_zeros(64);
  decoded_block_target_pc_shadow = base_pc + 2;
  decoded_block_type_shadow = 0b0000;
  decoded_block_xfer_kind_shadow = block_xfer_fall();
  decoded_block_contract_kind_shadow = 0b0000;
  block_marker_strict = false;
  bdesc_reset()
}

function main() : unit -> unit = {
  // VECTOR first use is a precise E_INST(EC_PERM) exception before BARG or
  // queue state changes.
  reset_first_use_case(0x0000_0000_0000_0800);
  exec_bstart_mpar();
  assert(last_e == 0b1);
  assert(last_argv == 0b1);
  assert(last_trapnum == trapnum_e_inst());
  assert(last_cause == 0x000004);
  assert(last_traparg0 == 0x0000_0000_0000_0000);
  assert(last_bi == 0b0);
  assert(not_bool(barg_valid));
  assert(barg_commit_seqno == 0x0000_0000_0000_0000);
  assert(not_bool(tile_effect_pending));

  // An invalid target is rejected before the first-use check and therefore
  // remains E_BLOCK(EC_CFI), not E_INST(EC_PERM).
  reset_first_use_case(0x0000_0000_0000_0810);
  block_marker_strict = true;
  exec_bstart_mseq();
  assert(last_trapnum == trapnum_block_trap());
  assert(last_cause != 0x000004);
  assert(last_traparg0 == 0x0000_0000_0000_0810);
  assert(not_bool(barg_valid));

  // Clearing only V permits VECTOR retry but leaves CUBE first use armed.
  reset_first_use_case(0x0000_0000_0000_0820);
  ssr_econfig_acr1[32] = 0b0;
  exec_bstart_vseq();
  assert(last_e == 0b0);
  assert(barg_valid);
  assert(barg_commit_seqno == 0x0000_0000_0000_0000);
  last_e = 0b0;
  last_argv = 0b0;
  last_trapnum = sail_zeros(6);
  last_cause = sail_zeros(24);
  last_traparg0 = sail_zeros(64);
  barg_valid = false;
  barg_commit_seqno = sail_zeros(64);
  exec_bstart_tmatmul();
  assert(last_e == 0b1);
  assert(last_argv == 0b1);
  assert(last_trapnum == trapnum_e_inst());
  assert(last_cause == 0x000004);
  assert(last_traparg0 == 0x0000_0000_0000_0001);
  assert(not_bool(barg_valid));
  assert(not_bool(tile_effect_pending));

  // Clearing C after the CUBE trap permits exact retry and begins the CUBE
  // header without reporting another exception.
  ssr_econfig_acr1[33] = 0b0;
  last_e = 0b0;
  last_argv = 0b0;
  last_trapnum = sail_zeros(6);
  last_cause = sail_zeros(24);
  last_traparg0 = sail_zeros(64);
  exec_bstart_tmatmul();
  assert(last_e == 0b0);
  assert(barg_valid);
  assert(tile_effect_pending);
  assert(barg_commit_seqno == 0x0000_0000_0000_0000);
  tile_effect_reset_arch();
  bdesc_reset();

  // SrcRType arithmetic codes are 00=.sw, 01=.uw, 10=.neg, 11=none.
  assert(apply_srcrtype_arith64(0b00, 0x1234_5678_8000_0001) == 0xFFFF_FFFF_8000_0001);
  assert(apply_srcrtype_arith64(0b01, 0x1234_5678_8000_0001) == 0x0000_0000_8000_0001);
  assert(apply_srcrtype_arith64(0b10, 0x1234_5678_8000_0001) == 0xEDCB_A987_7FFF_FFFF);
  assert(apply_srcrtype_arith64(0b11, 0x1234_5678_8000_0001) == 0x1234_5678_8000_0001);

  // LBU host memory is outside this REPL proof boundary: read_mem8/write_mem8
  // require host primops here.  Mirror exec_lbu's executable composition:
  // apply SrcRType first, shift that modifier, add base, then zext8_from8.
  let lbu_base : bits(64) = 0x0000_0010_0000_1000;
  let lbu_src : bits(64) = 0x0000_0001_8000_0004;
  assert(lbu_base + sail_shiftleft(apply_srcrtype_arith64(0b00, lbu_src), unsigned(0b00000)) == 0x0000_000F_8000_1004);
  assert(lbu_base + sail_shiftleft(apply_srcrtype_arith64(0b01, lbu_src), unsigned(0b00000)) == 0x0000_0010_8000_1004);
  assert(lbu_base + sail_shiftleft(apply_srcrtype_arith64(0b10, lbu_src), unsigned(0b00000)) == 0x0000_000E_8000_0FFC);
  assert(lbu_base + sail_shiftleft(apply_srcrtype_arith64(0b11, lbu_src), unsigned(0b00000)) == 0x0000_0011_8000_1004);
  assert(lbu_base + sail_shiftleft(apply_srcrtype_arith64(0b00, lbu_src), unsigned(0b00001)) == 0x0000_000F_0000_1008);
  assert(lbu_base + sail_shiftleft(apply_srcrtype_arith64(0b01, lbu_src), unsigned(0b00001)) == 0x0000_0011_0000_1008);
  assert(lbu_base + sail_shiftleft(apply_srcrtype_arith64(0b10, lbu_src), unsigned(0b00001)) == 0x0000_000D_0000_0FF8);
  assert(lbu_base + sail_shiftleft(apply_srcrtype_arith64(0b11, lbu_src), unsigned(0b00001)) == 0x0000_0013_0000_1008);
  assert(zext8_from8(0x81) == 0x0000_0000_0000_0081);
  assert(zext8_from8(0x42) == 0x0000_0000_0000_0042);
  assert(zext8_from8(0xA5) == 0x0000_0000_0000_00A5);
  assert(zext8_from8(0x7E) == 0x0000_0000_0000_007E);

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

  // PTO/Linx 0.58 permanently remove the B.IOD spelling and reuse its former
  // slot for B.IOS. PE_MASK=0000 is a strict no-op; a participating mask binds
  // the absolute Shared register and per-PE TSize.
  shared_tile_binding_valid = false;
  last_e = 0b0;
  last_trapnum = sail_zeros(6);
  decode_execute32(0x0000_1013);
  assert(last_e == 0b0);
  assert(not_bool(shared_tile_binding_valid));
  decode_execute32(0x02A5_9613);
  assert(shared_tile_binding_valid);
  assert(shared_tile_binding_id == 0x2A);
  assert(shared_tile_binding_pe_mask == 0xB);
  assert(shared_tile_binding_tsize == 0b011);

  // BSTART.PAR is also permanently removed as a spelling, but its historical
  // bits are not reserved: the current catalog assigns this word to
  // BSTART.MPAR, so it must decode rather than trap.
  last_e = 0b0;
  last_trapnum = sail_zeros(6);
  decode_execute32(0x0200_1181);
  assert(last_e == 0b0);

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
  assert(fp64_eq(0x0000_0000_0000_0000, 0x8000_0000_0000_0000));

  // PTO 0.58 differential operand maps match the frozen catalog/QEMU
  // function identities, including implicit ACC and MX scale operands.
  assert(tile_tlsu_required_sources(0b00100) == 0b00_0001);
  assert(tile_tlsu_required_sources(0b00110) == 0b00_0010);
  assert(tile_tlsu_required_sources(0b00101) == 0b00_0010);
  assert(tile_tlsu_required_sources(0b00111) == 0b00_0011);
  assert(tile_tlsu_required_sources(0b01000) == 0b00_0011);
  assert(tile_cube_required_sources(0b10000) == 0b00_0010);
  assert(tile_cube_required_sources(0b10001) == 0b00_0011);
  assert(tile_cube_required_sources(0b10100) == 0b00_0100);
  assert(tile_cube_required_sources(0b10101) == 0b00_0101);
  assert(tile_cube_required_sources(0b10110) == 0b00_0100);
  assert(tile_mask_lane_effect(false) == 0b0000);
  assert(tile_mask_lane_effect(true) == 0b1111);

  // Positive masked gather: one descriptor carries indices+mask and one
  // destination.  Only a successful complete preflight publishes effects and
  // last-use releases; false mask lanes are recorded as access-suppressing.
  reset_tile_effect_case();
  bdesc_mark_datr();
  bdesc_mark_ior();
  bdatr_raw = 0x0000_0000_0800_0000; // PadValue=01
  decoded_tile_datatype_shadow = 0b00001;
  tile_effect_begin(0b01, 0b00110);
  tile_effect_append_iot(0x0000_0000_0819_C013);
  assert(tile_effect_finalize());
  assert(tile_effect_commit_seq == 0x0000_0000_0000_0001);
  assert(tile_effect_memory_seq == 0x0000_0000_0000_0001);
  assert(tile_effect_tile_seq == 0x0000_0000_0000_0001);
  assert(tile_effect_lifetime_releases == 0x0000_0000_0000_0002);
  assert(tile_effect_last_masked);
  assert(tile_effect_last_mask_suppresses_access);
  assert(tile_effect_last_pad == 0b01);

  // Negative/retry path: a failed full access-set preflight reports the first
  // original address and commits no memory, Tile, ACC, or lifetime effect.
  reset_tile_effect_case();
  bdesc_mark_datr();
  bdesc_mark_ior();
  decoded_tile_datatype_shadow = 0b00001;
  tile_effect_begin(0b01, 0b00100);
  tile_effect_append_iot(0x0000_0000_0019_D013); // one source + dst, size=3
  tile_effect_access_set_valid = false;
  tile_effect_fault_address = 0x0000_0000_DEAD_0040;
  assert(not_bool(tile_effect_finalize()));
  assert(tile_effect_pending);
  assert(tile_effect_restart_pending);
  assert(tile_effect_commit_seq == 0x0000_0000_0000_0000);
  assert(tile_effect_memory_seq == 0x0000_0000_0000_0000);
  assert(tile_effect_tile_seq == 0x0000_0000_0000_0000);
  assert(tile_effect_lifetime_releases == 0x0000_0000_0000_0000);
  assert(last_trapnum == trapnum_data_page_fault());
  assert(last_traparg0 == 0x0000_0000_DEAD_0040);
  tile_effect_access_set_valid = true;
  assert(tile_effect_finalize());
  assert(tile_effect_commit_seq == 0x0000_0000_0000_0001);
  assert(tile_effect_memory_seq == 0x0000_0000_0000_0001);
  assert(tile_effect_tile_seq == 0x0000_0000_0000_0001);

  // TPREFETCH performs the same complete address/translation preflight but is
  // destination-free and publishes no memory-data or Tile payload effect.
  reset_tile_effect_case();
  bdesc_mark_datr();
  bdesc_mark_ior();
  decoded_tile_datatype_shadow = 0b00001;
  tile_effect_begin(0b01, 0b00011);
  assert(tile_effect_finalize());
  assert(tile_effect_preflight_seq == 0x0000_0000_0000_0001);
  assert(tile_effect_memory_seq == 0x0000_0000_0000_0000);
  assert(tile_effect_tile_seq == 0x0000_0000_0000_0000);

  // MX+BIAS uses authored source order A,B,ScaleA,ScaleB,Bias.  E8M0 scales
  // cover ceil(K/32)=3 groups for K=65 and ordinary/MX writes implicit ACC.
  reset_tile_effect_case();
  bdesc_mark_datr();
  bdesc_mark_dim();
  decoded_tile_datatype_shadow = 0b00001; // FP32 header/ACC for MX
  tile_effect_begin(0b10, 0b10101);
  exec_b_fpatr(0b000000, 0b000, 0x0, 0b0, 0b0, 0b0, 0b0);
  tile_effect_append_iot(0x0000_0000_0810_4013);
  tile_effect_append_iot(0x0000_0000_1030_4013);
  tile_effect_append_iot(0x0000_0000_0058_5013);
  assert(tile_effect_finalize());
  assert(tile_acc_valid);
  assert(tile_effect_acc_seq == 0x0000_0000_0000_0001);
  assert(tile_effect_last_mx);
  assert(tile_effect_last_bias);
  assert(tile_effect_last_scale_a_rows == 0x0000_0000_0000_0002);
  assert(tile_effect_last_scale_a_cols == 0x0000_0000_0000_0003);
  assert(tile_effect_last_scale_b_rows == 0x0000_0000_0000_0003);
  assert(tile_effect_last_scale_b_cols == 0x0000_0000_0000_0003);
  assert(tile_effect_last_scale_a_source == 0b00_0010);
  assert(tile_effect_last_scale_b_source == 0b00_0011);

  // .ACC is implicit: it has no B.IOT pseudo-destination and must preserve the
  // prior accumulator on descriptor/shape failure, then update it on success.
  reset_tile_effect_case();
  bdesc_mark_datr();
  bdesc_mark_dim();
  decoded_tile_datatype_shadow = 0b00001;
  tile_effect_begin(0b10, 0b10010);
  exec_b_fpatr(0b000000, 0b000, 0x0, 0b0, 0b0, 0b0, 0b0);
  tile_effect_append_iot(0x0000_0000_0818_4013);
  assert(not_bool(tile_effect_finalize()));
  assert(tile_effect_acc_seq == 0x0000_0000_0000_0000);
  assert(not_bool(tile_acc_valid));
  tile_effect_pending = false;
  tile_effect_restart_pending = false;
  tile_effect_reset_descriptors();
  tile_effect_begin(0b10, 0b10000);
  exec_b_fpatr(0b000000, 0b000, 0x0, 0b0, 0b0, 0b0, 0b0);
  tile_effect_append_iot(0x0000_0000_0818_4013);
  assert(tile_effect_finalize());
  assert(tile_acc_valid);
  tile_effect_reset_descriptors();
  tile_effect_begin(0b10, 0b10010);
  exec_b_fpatr(0b000000, 0b000, 0x0, 0b0, 0b0, 0b0, 0b0);
  tile_effect_append_iot(0x0000_0000_0818_4013);
  assert(tile_effect_finalize());
  assert(tile_effect_acc_seq == 0x0000_0000_0000_0002);
  assert(tile_effect_last_accumulate)
}
