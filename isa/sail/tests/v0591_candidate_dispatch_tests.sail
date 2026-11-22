// Directed success, fault, retry and ordinary-decode checks for the opt-in entry.

$include "../model/linxisa_v0591_candidate.sail"

function v0591_test_context(invocation : int, atomic : bool, far : bool,
    gm_permits : bool) -> msgb_bse_context = {
  struct {
    core = 0, pe = 2, slot = 0,
    key = struct {
      invocation = invocation, acr = current_acr_id(), execution_domain = 9,
      tpc = read_tpc()
    },
    kernel_origin = true, atomic = atomic, far = far, gm_permits = gm_permits
  }
}

function reset_v0591_dispatch_case() -> unit = {
  scoped_scalar_pending = None();
  v0591_scoped_pending_owner = None();
  scoped_scalar_next_token = 0;
  scoped_queue_binding = None();
  msgb_cores = vector_init(2, struct { active_invocation = None(), draining = false });
  msgb_cores = vector_update(msgb_cores, 0,
    struct { active_invocation = Some(41), draining = false });
  msgb_platform_context = Some(v0591_test_context(41, false, false, true));
  ssr_cstate = 0x0000000000000000;
  tpc = 0x0000000000001002;
  last_e = 0b0;
  last_trapnum = sail_zeros(6);
  last_traparg0 = sail_zeros(64)
}

function verify_v0591_candidate_dispatch() -> unit = {
  let lwi : bits(64) = 0x0000FFF22219051F; // lwi.intra [r4, -4], ->r4
  let casb : bits(64) = 0x00001C22029B041F;
  let hl_casw : bits(64) = 0x2E22628B00CE091F;
  let lpair : bits(64) = 0xFFF2229937DE091F;
  let malformed : bits(64) = 0x00000000001A031F; // reserved shareability
  let ordinary : bits(64) = 0x0000000F00000001; // L.BSTOP

  // Success and GM retry use the captured request and the platform permit.
  reset_v0591_dispatch_case();
  write_reg5(0b00100, 0x0000000000005000);
  msgb_platform_context = Some(v0591_test_context(41, false, false, false));
  match decode_execute64_v0591_candidate(lwi) {
    V0591ScopedPrepared => (), _ => assert(false)
  };
  match decode_execute64_v0591_candidate(ordinary) {
    V0591ScopedBusy => (), _ => assert(false)
  };
  match decode_execute64_v0591_candidate(malformed) {
    V0591ScopedBusy => (), _ => assert(false)
  };
  match scoped_scalar_pending {
    Some(attempt) => assert(attempt.request.token == 0 &
      attempt.request.source_tpc == 0x0000000000001002 & not_bool(attempt.issued)),
    None() => assert(false)
  };
  assert(read_reg5(0b00100) == 0x0000000000005000 &
    tpc == 0x0000000000001002 & last_trapnum == sail_zeros(6));
  assert(is_none(issue_scoped_scalar_v0591_candidate()));
  let stale_slot = v0591_test_context(41, false, false, true);
  msgb_platform_context = Some({ stale_slot with slot = 1 });
  assert(is_none(issue_scoped_scalar_v0591_candidate()));
  let stale_domain = v0591_test_context(41, false, false, true);
  msgb_platform_context = Some({ stale_domain with
    key = { stale_domain.key with execution_domain = 10 } });
  assert(is_none(issue_scoped_scalar_v0591_candidate()));
  msgb_platform_context = Some(v0591_test_context(42, false, false, true));
  assert(is_none(issue_scoped_scalar_v0591_candidate()));
  msgb_platform_context = Some(v0591_test_context(41, false, false, true));
  match issue_scoped_scalar_v0591_candidate() {
    Some(request) => {
      assert(request.core == 0 & request.agent == 2 & request.invocation == 41);
      let owner = v0591_test_context(41, false, false, true);
      msgb_platform_context = Some({ owner with slot = 1 });
      assert(not_bool(complete_scoped_scalar_v0591_candidate(request.token,
        ScopedMemoryCommitted, 0x0000000080000005)));
      match scoped_scalar_pending {
        Some(attempt) => assert(attempt.request.token == request.token &
          attempt.request.address == request.address & attempt.issued),
        None() => assert(false)
      };
      assert(read_reg5(0b00100) == 0x0000000000005000 &
        tpc == 0x0000000000001002);
      msgb_platform_context = Some({ owner with
        key = { owner.key with execution_domain = 10 } });
      assert(not_bool(complete_scoped_scalar_v0591_candidate(request.token,
        ScopedMemoryCommitted, 0x0000000080000005)));
      match scoped_scalar_pending {
        Some(attempt) => assert(attempt.request.token == request.token &
          attempt.request.address == request.address & attempt.issued),
        None() => assert(false)
      };
      assert(read_reg5(0b00100) == 0x0000000000005000 &
        tpc == 0x0000000000001002);
      msgb_platform_context = Some(v0591_test_context(42, false, false, true));
      assert(not_bool(complete_scoped_scalar_v0591_candidate(request.token,
        ScopedMemoryBlocked, 0x0000000000000000)));
      msgb_platform_context = Some(v0591_test_context(41, false, false, true));
      assert(complete_scoped_scalar_v0591_candidate(request.token, ScopedMemoryBlocked,
        0x0000000000000000));
      match issue_scoped_scalar_v0591_candidate() {
        Some(retry) => {
          assert(retry.token == request.token & retry.address == request.address);
          assert(complete_scoped_scalar_v0591_candidate(retry.token, ScopedMemoryCommitted,
            0x0000000080000005))
        },
        None() => assert(false)
      }
    },
    None() => assert(false)
  };
  assert(tpc == 0x000000000000100A);
  assert(is_none(v0591_scoped_pending_owner));

  // Pair completion has the same exact slot/domain owner binding.
  reset_v0591_dispatch_case();
  write_reg5(0b00100, 0x0000000000004000);
  write_reg5(0b00101, 0x1111111111111111);
  write_reg5(0b00110, 0x2222222222222222);
  match decode_execute64_v0591_candidate(lpair) {
    V0591ScopedPrepared => (), _ => assert(false)
  };
  match issue_scoped_scalar_v0591_candidate() {
    Some(request) => {
      let owner = v0591_test_context(41, false, false, true);
      msgb_platform_context = Some({ owner with slot = 1 });
      assert(not_bool(complete_scoped_scalar_pair_v0591_candidate(request.token,
        ScopedMemoryCommitted, 0x0000000080000001, 0x000000007FFFFFFF)));
      msgb_platform_context = Some({ owner with
        key = { owner.key with execution_domain = 10 } });
      assert(not_bool(complete_scoped_scalar_pair_v0591_candidate(request.token,
        ScopedMemoryCommitted, 0x0000000080000001, 0x000000007FFFFFFF)));
      match scoped_scalar_pending {
        Some(attempt) => assert(attempt.request.token == request.token &
          attempt.request.address == request.address & attempt.issued),
        None() => assert(false)
      };
      assert(read_reg5(0b00101) == 0x1111111111111111 &
        read_reg5(0b00110) == 0x2222222222222222 &
        tpc == 0x0000000000001002);
      msgb_platform_context = Some(owner);
      assert(complete_scoped_scalar_pair_v0591_candidate(request.token,
        ScopedMemoryCommitted, 0x0000000080000001, 0x000000007FFFFFFF))
    },
    None() => assert(false)
  };
  assert(tpc == 0x000000000000100A & is_none(v0591_scoped_pending_owner));

  // Missing context and malformed carriers fail closed and never execute ordinary decode.
  reset_v0591_dispatch_case();
  msgb_platform_context = None();
  match decode_execute64_v0591_candidate(lwi) {
    V0591ScopedIllegal => (), _ => assert(false)
  };
  assert(last_trapnum == trapnum_illegal_inst() & is_none(scoped_scalar_pending));
  reset_v0591_dispatch_case();
  match decode_execute64_v0591_candidate(malformed) {
    V0591ScopedIllegal => (), _ => assert(false)
  };
  assert(last_trapnum == trapnum_illegal_inst() & is_none(scoped_scalar_pending));

  // Atomic and Far context must exactly match the decoded transaction envelope.
  reset_v0591_dispatch_case();
  write_reg5(0b00010, 0x00000000000000AA);
  write_reg5(0b00011, 0x00000000000000BB);
  write_reg5(0b00100, 0x0000000000008000);
  msgb_platform_context = Some(v0591_test_context(41, true, false, true));
  match decode_execute64_v0591_candidate(casb) {
    V0591ScopedPrepared => (), _ => assert(false)
  };
  match issue_scoped_scalar_v0591_candidate() {
    Some(request) => {
      match request.atomic {
        Some(transaction) => assert(not_bool(transaction.far)),
        None() => assert(false)
      };
      assert(complete_scoped_scalar_v0591_candidate(request.token, ScopedMemoryCommitted,
        0x00000000000000CC))
    },
    None() => assert(false)
  };
  reset_v0591_dispatch_case();
  write_reg5(0b00010, 0x0000000080000001);
  write_reg5(0b00011, 0x000000007FFFFFFF);
  write_reg5(0b00100, 0x000000000000A000);
  msgb_platform_context = Some(v0591_test_context(41, true, true, true));
  match decode_execute64_v0591_candidate(hl_casw) {
    V0591ScopedPrepared => (), _ => assert(false)
  };
  match issue_scoped_scalar_v0591_candidate() {
    Some(request) => {
      match request.atomic {
        Some(transaction) => assert(transaction.far),
        None() => assert(false)
      };
      assert(complete_scoped_scalar_v0591_candidate(request.token, ScopedMemoryCommitted,
        0x0000000080000001))
    },
    None() => assert(false)
  };

  // Invocation ownership and Atomic/Far envelope mismatches are bundle faults.
  reset_v0591_dispatch_case();
  msgb_platform_context = Some(v0591_test_context(42, false, false, true));
  match decode_execute64_v0591_candidate(lwi) {
    V0591ScopedBundleFault => (), _ => assert(false)
  };
  assert(last_trapnum == trapnum_block_trap() & is_none(scoped_scalar_pending));
  reset_v0591_dispatch_case();
  msgb_platform_context = Some(v0591_test_context(41, true, false, true));
  match decode_execute64_v0591_candidate(lwi) {
    V0591ScopedBundleFault => (), _ => assert(false)
  };
  assert(is_none(scoped_scalar_pending));
  reset_v0591_dispatch_case();
  msgb_platform_context = Some(v0591_test_context(41, true, true, true));
  match decode_execute64_v0591_candidate(casb) {
    V0591ScopedBundleFault => (), _ => assert(false)
  };
  assert(is_none(scoped_scalar_pending));

  // Ordinary 64-bit words continue through the canonical decoder.
  reset_v0591_dispatch_case();
  match decode_execute64_v0591_candidate(ordinary) {
    V0591Ordinary => (), _ => assert(false)
  }
}

function main() : unit -> unit = {
  verify_v0591_candidate_dispatch()
}
