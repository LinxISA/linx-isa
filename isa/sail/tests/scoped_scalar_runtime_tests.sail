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

function verify_scoped_scalar_pairs() -> unit = {
  let lpair : bits(64) = 0xFFF2229937DE091F; // words from r4 - 4 -> r5,r6
  let spair : bits(64) = 0x0241305900DE0A1F; // doublewords r2,r3 -> r4 + 8
  tpc = 0x0000000000003002;
  write_reg5(0b00010, 0x1111111111111111);
  write_reg5(0b00011, 0x2222222222222222);
  write_reg5(0b00100, 0x0000000000004000);
  write_reg5(0b00101, 0x3333333333333333);
  write_reg5(0b00110, 0x4444444444444444);

  match prepare_scoped_scalar(lpair, 0, 2, 7, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(load) => {
      assert(load.address == 0x0000000000003FFC & load.size == 0x4);
      match load.second { Some((second_address, _)) => assert(second_address == 0x0000000000004000),
        None() => assert(false) };
      assert(not_bool(complete_scoped_scalar(load.token, ScopedMemoryCommitted, 0x0000000000000000)));
      assert(complete_scoped_scalar_pair(load.token, ScopedMemorySecondPageFault,
        0x0000000011111111, 0x0000000022222222))
    },
    None() => assert(false)
  };
  assert(last_traparg0 == 0x0000000000004000 & last_trapnum == trapnum_data_page_fault());
  assert(tpc == 0x0000000000003002 & read_reg5(0b00101) == 0x3333333333333333);
  assert(read_reg5(0b00110) == 0x4444444444444444);

  match prepare_scoped_scalar(lpair, 0, 2, 7, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(load) => assert(complete_scoped_scalar_pair(load.token, ScopedMemoryCommitted,
      0x0000000080000001, 0x000000007FFFFFFF)),
    None() => assert(false)
  };
  assert(tpc == 0x000000000000300A & read_reg5(0b00101) == 0xFFFFFFFF80000001);
  assert(read_reg5(0b00110) == 0x000000007FFFFFFF);

  write_reg5(0b00100, 0xFFFFFFFFFFFFFFF0);
  match prepare_scoped_scalar(spair, 0, 2, 7, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(store) => {
      match store.shareability { ScalarInterCore => (), _ => assert(false) };
      assert(store.is_store & store.address == 0xFFFFFFFFFFFFFFF8 & store.size == 0x8);
      assert(store.store_data == 0x1111111111111111);
      match store.second {
        Some((second_address, value)) => assert(second_address == 0x0000000000000000 & value == 0x2222222222222222),
        None() => assert(false)
      };
      assert(complete_scoped_scalar_pair(store.token, ScopedMemoryCommitted, 0x0000000000000000,
        0x0000000000000000))
    },
    None() => assert(false)
  };
  assert(tpc == 0x0000000000003012)
}

function verify_scoped_scalar_writeback() -> unit = {
  let ldi_post : bits(64) = 0xFFE232992FFE091F; // r4 - 16, both results to r5
  let lw_pre : bits(64) = 0x12622289382E0A1F; // r4 + (r6.sw << 2), ->r5,r7
  let sw_post : bits(64) = 0x14622049203E081F; // r2, r4 + (r6.uw << 2), ->r4
  tpc = 0x0000000000002002;
  write_reg5(0b00010, 0x123456789ABCDEF0);
  write_reg5(0b00100, 0x0000000000004000);
  write_reg5(0b00101, 0x1111111111111111);
  write_reg5(0b00110, 0xBAADF00DFFFFFFFF);
  write_reg5(0b00111, 0x2222222222222222);

  match prepare_scoped_scalar(ldi_post, 0, 2, 7, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(load) => {
      assert(load.address == 0x0000000000004000 & load.size == 0x8);
      assert(complete_scoped_scalar(load.token, ScopedMemoryCommitted, 0xABCDEF0123456789));
      assert(read_reg5(0b00101) == 0x0000000000003FF0) // Writeback publishes after the aliased result.
    },
    None() => assert(false)
  };
  assert(tpc == 0x000000000000200A);

  match prepare_scoped_scalar(lw_pre, 0, 2, 7, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(load) => {
      assert(load.address == 0x0000000000003FFC & load.size == 0x4);
      assert(complete_scoped_scalar(load.token, ScopedMemoryPageFault, 0x5555555555555555));
      assert(read_reg5(0b00101) == 0x0000000000003FF0);
      assert(read_reg5(0b00111) == 0x2222222222222222)
    },
    None() => assert(false)
  };
  assert(tpc == 0x000000000000200A);

  match prepare_scoped_scalar(sw_post, 0, 2, 7, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(store) => {
      assert(store.address == 0x0000000000004000 & store.size == 0x4);
      assert(store.store_data == 0x000000009ABCDEF0);
      assert(complete_scoped_scalar(store.token, ScopedMemoryBlocked, 0x0000000000000000));
      assert(read_reg5(0b00100) == 0x0000000000004000);
      write_reg5(0b00110, 0x0000000000000000);
      match issue_scoped_scalar(true) {
        Some(retry) => {
          assert(retry.token == store.token & retry.address == store.address);
          assert(complete_scoped_scalar(retry.token, ScopedMemoryCommitted, 0x0000000000000000))
        },
        None() => assert(false)
      };
      assert(read_reg5(0b00100) == 0x0000000400003FFC)
    },
    None() => assert(false)
  };
  assert(tpc == 0x0000000000002012)
}
