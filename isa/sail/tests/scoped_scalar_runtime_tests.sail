function verify_scoped_scalar_runtime() -> unit = {
  let lwi : bits(64) = 0x0000FFF22219051F; // lwi.intra [r4, -4], ->r4
  let sdi : bits(64) = 0x04513059000E0A1F; // hl.sdi.inter r2, [r5, 16]
  let pcr : bits(64) = 0x0000FFFF21B9041F; // lw.pcr.private -8, ->r3
  let sbi : bits(64) = 0x000000510059041F; // sbi.private r2, [r5, 0]
  let old_cstate = ssr_cstate;
  ssr_cstate = 0x0000000000000004;
  tpc = 0x0000000000001002;
  write_reg5(0b00100, 0x0000000000000000);
  match prepare_scoped_scalar(lwi, 1, 3, 7, true) { ScopedPrepared => (), _ => assert(false) };
  assert(is_none(issue_scoped_scalar(false)));
  assert(tpc == 0x0000000000001002);
  match prepare_scoped_scalar(sdi, 1, 3, 7, true) { ScopedBusy => (), _ => assert(false) };
  write_reg5(0b00100, 0x0000000000005000); // Retry uses the captured base.
  match issue_scoped_scalar(true) {
    Some(request) => {
      match request.shareability { ScalarIntraCore => (), _ => assert(false) };
      assert(request.size == 0x4 & not_bool(request.is_store));
      assert(request.address == 0xFFFFFFFFFFFFFFFC);
      assert(request.source_tpc == 0x0000000000001002 & request.instruction == lwi);
      assert(request.core == 1 & request.agent == 3 & request.invocation == 7 & request.acr == 0x4);
      assert(is_none(issue_scoped_scalar(true)));
      assert(not_bool(complete_scoped_scalar(request.token + 1, ScopedMemoryCommitted, 0x0000000000000000)));
      assert(complete_scoped_scalar(request.token, ScopedMemoryBlocked, 0x0000000000000000));
      assert(read_reg5(0b00100) == 0x0000000000005000);
      assert(tpc == 0x0000000000001002);
      match issue_scoped_scalar(true) {
        Some(retry) => {
          assert(retry.token == request.token & retry.address == request.address);
          assert(complete_scoped_scalar(retry.token, ScopedMemoryCommitted, 0xFACECAFE80000005));
          assert(not_bool(complete_scoped_scalar(retry.token, ScopedMemoryCommitted, 0x0000000000000000)))
        },
        None() => assert(false)
      }
    },
    None() => assert(false)
  };
  assert(tpc == 0x000000000000100A);
  assert(read_reg5(0b00100) == 0xFFFFFFFF80000005);

  write_reg5(0b00010, 0xFEDCBA9876543210);
  write_reg5(0b00101, 0x0000000000003000);
  match prepare_scoped_scalar(sdi, 1, 3, 7, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(store) => {
      match store.shareability { ScalarInterCore => (), _ => assert(false) };
      assert(store.size == 0x8 & store.is_store & store.address == 0x0000000000003010);
      assert(store.store_data == 0xFEDCBA9876543210);
      assert(complete_scoped_scalar(store.token, ScopedMemoryCommitted, 0x0000000000000000))
    },
    None() => assert(false)
  };
  assert(tpc == 0x0000000000001012);

  write_reg5(0b00011, 0xBBBBBBBBBBBBBBBB);
  match prepare_scoped_scalar(pcr, 1, 3, 7, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(load) => {
      match load.shareability { ScalarPrivate => (), _ => assert(false) };
      assert(load.address == 0x0000000000001008);
      assert(complete_scoped_scalar(load.token, ScopedMemoryPageFault, 0x123456789ABCDEF0))
    },
    None() => assert(false)
  };
  assert(tpc == 0x0000000000001012 & last_traparg0 == 0x0000000000001008);
  assert(last_trapnum == trapnum_data_page_fault() & read_reg5(0b00011) == 0xBBBBBBBBBBBBBBBB);

  match prepare_scoped_scalar(sbi, 1, 3, 7, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(store) => {
      assert(store.size == 0x1 & store.address == 0x0000000000003000);
      assert(store.store_data == 0x0000000000000010);
      assert(complete_scoped_scalar(store.token, ScopedMemoryCommitted, 0x0000000000000000))
    },
    None() => assert(false)
  };
  assert(tpc == 0x000000000000101A);
  write_reg5(0b00100, 0x0000000000005001);
  match prepare_scoped_scalar(lwi, 1, 3, 7, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(load) => {
      assert(load.address == 0x0000000000004FFD);
      assert(complete_scoped_scalar(load.token, ScopedMemoryAlignment, 0x0000000000000000))
    },
    None() => assert(false)
  };
  assert(last_trapnum == 0b100010 & tpc == 0x000000000000101A & read_reg5(0b00100) == 0x0000000000005001);

  match prepare_scoped_scalar(lwi, 1, 3, 7, false) { ScopedBundleFault => (), _ => assert(false) };
  assert(last_trapnum == trapnum_block_trap());
  match prepare_scoped_scalar(0x00000000001A031F, 1, 3, 7, false) { ScopedIllegal => (), _ => assert(false) };
  assert(last_trapnum == trapnum_illegal_inst() & last_traparg0 == tpc);
  match prepare_scoped_scalar(0x00000000001A001F, 1, 3, 7, true) { ScopedUnimplemented => (), _ => assert(false) };
  match prepare_scoped_scalar(0x0000000CB119041F, 1, 3, 7, true) { ScopedUnimplemented => (), _ => assert(false) };
  assert(is_none(issue_scoped_scalar(true)) & tpc == 0x000000000000101A);
  ssr_cstate = old_cstate
}
