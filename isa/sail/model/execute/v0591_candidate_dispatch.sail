// Opt-in PTO 0.59.1 scoped Scalar dispatch. The v0.58 entry remains canonical.

enum v0591_candidate_dispatch = {
  V0591Ordinary,
  V0591ScopedPrepared,
  V0591ScopedIllegal,
  V0591ScopedBundleFault,
  V0591ScopedUnimplemented,
  V0591ScopedBusy
}

function v0591_scoped_prefix(inst : bits(64)) -> bool = {
  inst[7..0] == 0x1F
}

function v0591_scoped_envelope_matches(
  id : bits(8), inst : bits(64), ctx : msgb_bse_context
) -> bool = {
  match decode_scoped_atomic(id, inst[63..16]) {
    Some(atomic) => ctx.atomic & (ctx.far == atomic.far),
    None() => not_bool(ctx.atomic) & not_bool(ctx.far)
  }
}

function v0591_scoped_context_owns(ctx : msgb_bse_context) -> bool = {
  msgb_kernel_invocation_live(ctx) &
  ctx.key.acr == current_acr_id() &
  ctx.key.tpc == read_tpc()
}

function v0591_dispatch_result(result : scoped_scalar_start) -> v0591_candidate_dispatch = {
  match result {
    ScopedPrepared => V0591ScopedPrepared,
    ScopedIllegal => V0591ScopedIllegal,
    ScopedBundleFault => V0591ScopedBundleFault,
    ScopedUnimplemented => V0591ScopedUnimplemented,
    ScopedBusy => V0591ScopedBusy
  }
}

function decode_execute64_v0591_candidate(inst : bits(64)) -> v0591_candidate_dispatch = {
  let id = decode_pto_scoped_scalar(inst);
  if id != 0xFF then match msgb_platform_instruction_context() {
    None() => {
      trap_illegal_inst(read_pc_or_tpc());
      V0591ScopedIllegal
    },
    Some(ctx) => {
      let applicable = v0591_scoped_context_owns(ctx) &
        v0591_scoped_envelope_matches(id, inst, ctx);
      v0591_dispatch_result(
        prepare_scoped_scalar(inst, ctx.core, ctx.pe, ctx.key.invocation, applicable)
      )
    }
  }
  else if v0591_scoped_prefix(inst) then {
    trap_illegal_inst(read_pc_or_tpc());
    V0591ScopedIllegal
  }
  else {
    decode_execute64(inst);
    V0591Ordinary
  }
}

function v0591_pending_context_owns(
  attempt : scoped_scalar_attempt, ctx : msgb_bse_context
) -> bool = {
  let envelope : bool = match attempt.request.atomic {
    Some(transaction) => ctx.atomic & (ctx.far == transaction.far),
    None() => not_bool(ctx.atomic) & not_bool(ctx.far)
  };
  v0591_scoped_context_owns(ctx) & envelope &
  attempt.request.core == ctx.core & attempt.request.agent == ctx.pe &
  attempt.request.invocation == ctx.key.invocation
}

function issue_scoped_scalar_v0591_candidate() -> option(scoped_memory_request) = {
  match (scoped_scalar_pending, msgb_platform_instruction_context()) {
    (Some(attempt), Some(ctx)) if v0591_pending_context_owns(attempt, ctx) =>
      issue_scoped_scalar(ctx.gm_permits),
    _ => None()
  }
}

function complete_scoped_scalar_v0591_candidate(token : int,
    completion : scoped_memory_completion, data : bits(64)) -> bool = {
  match (scoped_scalar_pending, msgb_platform_instruction_context()) {
    (Some(attempt), Some(ctx)) if v0591_pending_context_owns(attempt, ctx) =>
      complete_scoped_scalar(token, completion, data),
    _ => false
  }
}

function complete_scoped_scalar_pair_v0591_candidate(token : int,
    completion : scoped_memory_completion, first_data : bits(64),
    second_data : bits(64)) -> bool = {
  match (scoped_scalar_pending, msgb_platform_instruction_context()) {
    (Some(attempt), Some(ctx)) if v0591_pending_context_owns(attempt, ctx) =>
      complete_scoped_scalar_pair(token, completion, first_data, second_data),
    _ => false
  }
}
