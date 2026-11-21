// Enabled-context BSE from PTO-ARCH-MSGB-SEND-001 at v0.59.1.0.
// Instruction dispatch supplies the current kernel context and GM recovery gate.

struct msgb_bse_context = {
  core : range(0, 1),
  pe : range(0, 3),
  slot : range(0, 1),
  key : msgb_send_key,
  kernel_origin : bool,
  atomic : bool,
  far : bool,
  gm_permits : bool
}

enum msgb_bse_outcome = {
  MSGB_BSE_COMPLETED,
  MSGB_BSE_BAD_CONTEXT,
  MSGB_BSE_BAD_ENVELOPE,
  MSGB_BSE_BLOCKED
}

function msgb_find_replay(
  receipts : vector(16, option(msgb_send_receipt)), key : msgb_send_key
) -> option(msgb_send_receipt) = {
  var found : option(msgb_send_receipt) = None();
  foreach (slot from 0 to 15) {
    match receipts[slot] {
      Some(receipt) if receipt.key.invocation == key.invocation &
                       receipt.key.acr == key.acr &
                       receipt.key.execution_domain == key.execution_domain &
                       receipt.key.tpc == key.tpc =>
        found = Some(receipt),
      _ => ()
    }
  };
  found
}

function msgb_find_free(
  receipts : vector(16, option(msgb_send_receipt)), reserve : bool
) -> option(msgb_receipt_index) = {
  var found : option(msgb_receipt_index) = None();
  var skip : bool = reserve;
  foreach (slot from 0 to 15) {
    if is_none(receipts[slot]) & is_none(found) then {
      if skip then skip = false else found = Some(slot)
    } else ()
  };
  found
}

function msgb_store_tx_result(index : msgb_endpoint_index, result : bits(8)) -> unit = {
  let bank = msgb_endpoints[index];
  let diagnosed = { bank with tx_result = result, tx_result_valid = true };
  msgb_endpoints = vector_update(msgb_endpoints, index, diagnosed)
}

function msgb_kernel_invocation_live(ctx : msgb_bse_context) -> bool = {
  if not_bool(ctx.kernel_origin) | ctx.key.invocation == 0 then false
  else match msgb_cores[ctx.core].active_invocation {
    Some(invocation) => invocation == ctx.key.invocation,
    None() => false
  }
}

function msgb_kernel_context_active(ctx : msgb_bse_context, bank : msgb_endpoint) -> bool = {
  bank.enabled & ctx.key.invocation == bank.invocation & msgb_kernel_invocation_live(ctx)
}

function msgb_context_index(ctx : msgb_bse_context) -> msgb_endpoint_index = {
  let acr = unsigned(ctx.key.acr);
  ctx.core * 128 + ctx.slot * 64 + ctx.pe * 16 + acr
}

function msgb_bse(ctx : msgb_bse_context, control : bits(64)) -> msgb_bse_outcome = {
  let index = msgb_context_index(ctx);
  let bank = msgb_endpoints[index];
  if not_bool(msgb_kernel_context_active(ctx, bank)) then MSGB_BSE_BAD_CONTEXT
  else if ctx.atomic | ctx.far then MSGB_BSE_BAD_ENVELOPE
  else if not_bool(ctx.gm_permits) then MSGB_BSE_BLOCKED
  else match msgb_find_replay(bank.receipts, ctx.key) {
    Some(receipt) => {
      if control == receipt.control then {
        let replayed = {
          bank with tx_control = receipt.control, tx_id_hi = receipt.id_hi,
          tx_id_lo = receipt.id_lo, tx_result = msgb_duplicate, tx_result_valid = true
        };
        msgb_endpoints = vector_update(msgb_endpoints, index, replayed)
      } else msgb_store_tx_result(index, msgb_bad_command);
      MSGB_BSE_COMPLETED
    },
    None() => {
      let done = msgb_matches_done(bank, control);
      let slot = msgb_find_free(bank.receipts, is_some(bank.dispatch_id) & not_bool(done));
      let result = if msgb_cores[ctx.core].draining & not_bool(done) then msgb_bad_command
                   else msgb_admit_packet(index, control, is_some(slot));
      match slot {
        Some(receipt_index) if result == msgb_ok => {
          // Admission can also have updated this bank as the receiver.
          let admitted = msgb_endpoints[index];
          let receipt : msgb_send_receipt = struct {
            key = ctx.key, control = control, id_hi = admitted.tx_id_hi, id_lo = admitted.tx_id_lo
          };
          let receipts = vector_update(admitted.receipts, receipt_index, Some(receipt));
          msgb_endpoints = vector_update(msgb_endpoints, index, { admitted with receipts = receipts })
        },
        _ => ()
      };
      msgb_store_tx_result(index, result);
      MSGB_BSE_COMPLETED
    }
  }
}
