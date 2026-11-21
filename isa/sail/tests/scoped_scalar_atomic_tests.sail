function verify_scoped_scalar_atomic_runtime() -> unit = {
  let casb : bits(64) = 0x00001C22029B041F;
  let hl_casw : bits(64) = 0x2E22628B00CE091F;
  let lrw : bits(64) = 0x00001402028B061F;
  let scw : bits(64) = 0x00001241930B061F;
  let lw_add : bits(64) = 0x00000632228B051F;
  let sb_add : bits(64) = 0x00008232300B041F;
  let lrw_ignored_srczero : bits(64) = 0x00001012028B061F;
  let old_cstate = ssr_cstate;
  ssr_cstate = 0x0000000000000004;
  tpc = 0x0000000000004002;
  write_reg5(0b00010, 0x11111111111111AA); // compare
  write_reg5(0b00011, 0x22222222222222BB); // desired / operand
  write_reg5(0b00100, 0x0000000000008000); // address
  write_reg5(0b00101, 0xAAAAAAAAAAAAAAAA); // result
  write_reg5(0b00110, 0xBBBBBBBBBBBBBBBB); // SC status

  match prepare_scoped_scalar(casb, 2, 3, 11, true) { ScopedPrepared => (), _ => assert(false) };
  write_reg5(0b00010, 0x0000000000000000);
  write_reg5(0b00011, 0x0000000000000000);
  write_reg5(0b00100, 0x0000000000009000);
  match issue_scoped_scalar(true) {
    Some(request) => {
      match request.atomic {
        Some(transaction) => {
          match transaction.kind { ScopedAtomicCompareAndSwap => (), _ => assert(false) };
          assert(transaction.compare == 0x00000000000000AA);
          assert(transaction.operand == 0x00000000000000BB);
          assert(transaction.acquire & not_bool(transaction.release) & not_bool(transaction.far))
        },
        None() => assert(false)
      };
      match request.shareability { ScalarPrivate => (), _ => assert(false) };
      assert(request.address == 0x0000000000008000 & request.size == 0x1);
      assert(complete_scoped_scalar(request.token, ScopedMemoryBlocked, 0x00000000000000FF));
      assert(read_reg5(0b00101) == 0xAAAAAAAAAAAAAAAA & tpc == 0x0000000000004002);
      match issue_scoped_scalar(true) {
        Some(retry) => {
          assert(retry.token == request.token & retry.address == request.address);
          assert(complete_scoped_scalar(retry.token, ScopedMemoryCommitted, 0x123456789ABCDEFF))
        },
        None() => assert(false)
      }
    },
    None() => assert(false)
  };
  assert(read_reg5(0b00101) == 0x00000000000000FF & tpc == 0x000000000000400A);

  write_reg5(0b00010, 0x0000000080000001);
  write_reg5(0b00011, 0x000000007FFFFFFF);
  write_reg5(0b00100, 0x000000000000A000);
  match prepare_scoped_scalar(hl_casw, 2, 3, 11, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(request) => {
      match request.atomic {
        Some(transaction) => {
          match transaction.kind { ScopedAtomicCompareAndSwap => (), _ => assert(false) };
          assert(transaction.compare == 0x0000000080000001);
          assert(transaction.operand == 0x000000007FFFFFFF);
          assert(transaction.acquire & transaction.release & transaction.far)
        },
        None() => assert(false)
      };
      match request.shareability { ScalarIntraCore => (), _ => assert(false) };
      assert(request.size == 0x4);
      assert(complete_scoped_scalar(request.token, ScopedMemoryCommitted, 0x0000000080000001))
    },
    None() => assert(false)
  };
  assert(read_reg5(0b00101) == 0xFFFFFFFF80000001 & tpc == 0x0000000000004012);

  write_reg5(0b00100, 0x000000000000B000);
  write_reg5(0b00101, 0xCCCCCCCCCCCCCCCC);
  match prepare_scoped_scalar(lrw, 2, 3, 11, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(request) => {
      match request.atomic {
        Some(transaction) => match transaction.kind { ScopedAtomicLoadReserved => (), _ => assert(false) },
        None() => assert(false)
      };
      match request.shareability { ScalarInterCore => (), _ => assert(false) };
      assert(not_bool(request.is_store) & request.address == 0x000000000000B000);
      assert(complete_scoped_scalar(request.token, ScopedMemoryPageFault, 0x0000000087654321))
    },
    None() => assert(false)
  };
  assert(read_reg5(0b00101) == 0xCCCCCCCCCCCCCCCC & tpc == 0x0000000000004012);
  assert(last_traparg0 == 0x000000000000B000);

  match prepare_scoped_scalar(lrw, 2, 3, 11, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(request) => assert(complete_scoped_scalar(request.token, ScopedMemoryCommitted,
      0x0000000087654321)),
    None() => assert(false)
  };
  assert(read_reg5(0b00101) == 0xFFFFFFFF87654321 & tpc == 0x000000000000401A);

  write_reg5(0b00011, 0xDEADBEEF12345678);
  write_reg5(0b00100, 0x000000000000B020);
  write_reg5(0b00110, 0xBBBBBBBBBBBBBBBB);
  match prepare_scoped_scalar(scw, 2, 3, 11, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(request) => {
      match request.atomic {
        Some(transaction) => {
          match transaction.kind { ScopedAtomicStoreConditional => (), _ => assert(false) };
          assert(transaction.operand == 0x0000000012345678);
          assert(not_bool(transaction.acquire) & transaction.release)
        },
        None() => assert(false)
      };
      assert(request.address == 0x000000000000B020 & request.is_store);
      assert(not_bool(complete_scoped_scalar(request.token, ScopedMemoryCommitted, 0x0000000000000002)));
      assert(read_reg5(0b00110) == 0xBBBBBBBBBBBBBBBB & tpc == 0x000000000000401A);
      assert(complete_scoped_scalar(request.token, ScopedMemoryCommitted, 0x0000000000000001))
    },
    None() => assert(false)
  };
  assert(read_reg5(0b00110) == 0x0000000000000001 & tpc == 0x0000000000004022);

  write_reg5(0b00011, 0x0000000000000007);
  write_reg5(0b00100, 0x000000000000C000);
  write_reg5(0b00101, 0xDDDDDDDDDDDDDDDD);
  match prepare_scoped_scalar(lw_add, 2, 3, 11, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(request) => {
      match request.atomic {
        Some(transaction) => {
          match transaction.operation { ScopedAtomicAdd => (), _ => assert(false) };
          assert(transaction.operand == 0x0000000000000007 & transaction.acquire & transaction.release)
        },
        None() => assert(false)
      };
      assert(complete_scoped_scalar(request.token, ScopedMemoryCommitted, 0x0000000080000002))
    },
    None() => assert(false)
  };
  assert(read_reg5(0b00101) == 0xFFFFFFFF80000002 & tpc == 0x000000000000402A);

  write_reg5(0b00011, 0x00000000000000F0);
  write_reg5(0b00100, 0x000000000000C100);
  write_reg5(0b00101, 0xEEEEEEEEEEEEEEEE);
  match prepare_scoped_scalar(sb_add, 2, 3, 11, true) { ScopedPrepared => (), _ => assert(false) };
  match issue_scoped_scalar(true) {
    Some(request) => {
      match request.atomic {
        Some(transaction) => {
          match transaction.operation { ScopedAtomicAdd => (), _ => assert(false) };
          assert(transaction.operand == 0x00000000000000F0 & transaction.release)
        },
        None() => assert(false)
      };
      assert(complete_scoped_scalar(request.token, ScopedMemoryCommitted, 0x0000000000000001))
    },
    None() => assert(false)
  };
  assert(read_reg5(0b00101) == 0xEEEEEEEEEEEEEEEE & tpc == 0x0000000000004032);

  write_reg5(0b00100, 0x000000000000B000);
  match prepare_scoped_scalar(lrw_ignored_srczero, 2, 3, 11, true) {
    ScopedPrepared => (), _ => assert(false)
  };
  match issue_scoped_scalar(true) {
    Some(request) => {
      match request.atomic {
        Some(transaction) => {
          match transaction.kind { ScopedAtomicLoadReserved => (), _ => assert(false) };
          assert(transaction.operand == 0x0000000000000000 &
                 transaction.compare == 0x0000000000000000)
        },
        None() => assert(false)
      };
      match request.shareability { ScalarInterCore => (), _ => assert(false) };
      assert(request.address == 0x000000000000B000 & request.size == 0x4);
      assert(complete_scoped_scalar(request.token, ScopedMemoryCommitted,
        0x0000000087654321))
    },
    None() => assert(false)
  };
  assert(read_reg5(0b00101) == 0xFFFFFFFF87654321 & tpc == 0x000000000000403A);
  ssr_cstate = old_cstate
}
