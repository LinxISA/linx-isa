function verify_scoped_scalar_queues() -> unit = {
  let clw : bits(64) = 0x00000000F90A011F;
  let csd : bits(64) = 0x00000000093A021F;
  let lwi : bits(64) = 0x0000000E2F19041F; // U#1 as base, ->U
  let empty : vector(4, option(bits(64))) = vector_init(4, None());
  let u = vector_update(empty, 0, Some(0x0000000000007000));
  assert(bind_scoped_scalar_queues(1, 3, 41, empty, u));
  tpc = 0x0000000000008002;
  write_reg5(0b00100, 0x0000000000006000);
  write_reg5(0b11111, 0xBBBBBBBBBBBBBBBB); // Legacy bring-up aliases stay separate.

  match prepare_scoped_scalar(csd, 1, 3, 42, true) { ScopedUnimplemented => (), _ => assert(false) };
  match prepare_scoped_scalar(csd, 1, 3, 41, true) { ScopedIllegal => (), _ => assert(false) };
  assert(is_none(issue_scoped_scalar(true)));
  assert(last_trapnum == trapnum_illegal_inst() & last_traparg0 == tpc);

  match prepare_scoped_scalar(clw, 1, 3, 41, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(load) => {
      assert(load.address == 0x0000000000005FFC & load.size == 0x4);
      assert(not_bool(bind_scoped_scalar_queues(1, 3, 42, empty, empty)));
      assert(complete_scoped_scalar(load.token, ScopedMemoryPageFault, 0x0000000080000005));
      assert(not_bool(scoped_source_available(0b11000)))
    },
    None() => assert(false)
  };
  assert(tpc == 0x0000000000008002);

  match prepare_scoped_scalar(clw, 1, 3, 41, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(load) => assert(complete_scoped_scalar(load.token, ScopedMemoryCommitted, 0x0000000080000005)),
    None() => assert(false)
  };
  assert(read_scoped_reg5(0b11000) == 0xFFFFFFFF80000005);
  assert(read_reg5(0b11111) == 0xBBBBBBBBBBBBBBBB);
  assert(tpc == 0x000000000000800A);

  match prepare_scoped_scalar(csd, 1, 3, 41, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(store) => {
      assert(store.is_store & store.address == 0x0000000000006008);
      assert(store.store_data == 0xFFFFFFFF80000005);
      assert(complete_scoped_scalar(store.token, ScopedMemoryCommitted, 0x0000000000000000))
    },
    None() => assert(false)
  };
  assert(read_scoped_reg5(0b11000) == 0xFFFFFFFF80000005);

  match prepare_scoped_scalar(lwi, 1, 3, 41, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(load) => {
      assert(load.address == 0x0000000000007000);
      assert(complete_scoped_scalar(load.token, ScopedMemoryCommitted, 0x0000000000000011))
    },
    None() => assert(false)
  };
  assert(read_scoped_reg5(0b11100) == 0x0000000000000011);
  assert(read_scoped_reg5(0b11101) == 0x0000000000007000);
  assert(not_bool(scoped_source_available(0b11110)));
  assert(tpc == 0x000000000000801A)
}
