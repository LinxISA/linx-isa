// Architectural MSGB register transitions, PTO-ARCH-MSGB-SSR-001 and
// PTO-ARCH-MSGB-LIFECYCLE-001, published PTO v0.59.1.0.

register msgb_config_selection : vector(16, bits(4)) = vector_init(16, 0x0)
register msgb_instruction_blocked : bool = false

enum execution_control_request = { SendEvent, WaitEvent }
register last_control_request : execution_control_request = SendEvent
register control_request_operand : bits(64) = 0x0000000000000000
register architecture_request_epoch : int = 0

function publish_execution_control(request : execution_control_request, operand : bits(64)) -> unit = {
  last_control_request = request;
  control_request_operand = operand;
  architecture_request_epoch = architecture_request_epoch + 1
}

function msgb_platform_instruction_context() -> option(msgb_bse_context) = {
  match msgb_platform_context {
    None() => None(),
    Some(platform) => {
      let key = { platform.key with acr = current_acr_id(), tpc = read_tpc() };
      Some({ platform with key = key })
    }
  }
}

function msgb_address(address : bits(24)) -> bool = {
  address[23..12] == 0x000 & unsigned(address[11..0]) >= unsigned(0x830) &
  unsigned(address[11..0]) <= unsigned(0x84B)
}

function msgb_config_address(address : bits(24)) -> bool = {
  address == 0x000849 | address == 0x00084A | address == 0x00084B
}

function msgb_word_address(address : bits(24)) -> bool = {
  address[23..4] == 0x00083 & address[3..0] != 0x0 & unsigned(address[3..0]) <= 10
}

function msgb_selection_index(ctx : msgb_bse_context) -> range(0, 15) = {
  ctx.core * 8 + ctx.slot * 4 + ctx.pe
}

function msgb_selected_endpoint(ctx : msgb_bse_context) -> msgb_endpoint_index = {
  let selection = msgb_selection_index(ctx);
  let key = { ctx.key with acr = msgb_config_selection[selection] };
  msgb_context_index({ ctx with key = key })
}

function msgb_effect_preflight(ctx : msgb_bse_context, is_config : bool) -> msgb_bse_outcome = {
  if not_bool(msgb_kernel_invocation_live(ctx)) |
     (is_config & ctx.key.acr != 0x0) |
     (not_bool(is_config) & not_bool(msgb_kernel_context_active(ctx, msgb_endpoints[msgb_context_index(ctx)])))
  then MSGB_BSE_BAD_CONTEXT
  else if ctx.atomic | ctx.far then MSGB_BSE_BAD_ENVELOPE
  else if not_bool(ctx.gm_permits) then MSGB_BSE_BLOCKED
  else MSGB_BSE_COMPLETED
}

function msgb_bank_quiescent(bank : msgb_endpoint) -> bool = {
  is_none(bank.receive.queued) & is_none(bank.receive.snapshot)
}

function msgb_configure_bank(bank : msgb_endpoint, invocation : int, value : bits(64))
    -> option(msgb_endpoint) = {
  if value[15..1] != 0b000000000000000 | not_bool(msgb_bank_quiescent(bank)) then None()
  else if value[0] == 0b0 then {
    if value != 0x0000000000000000 | is_some(bank.dispatch_id) then None()
    else Some({ bank with enabled = false, waiting = false })
  } else {
    let epoch = value[31..16];
    let source = value[63..32];
    let old_epoch = bank.receive.epoch;
    let old_source = bank.source_epoch;
    let first = old_epoch == 0x0000 & old_source == 0x00000000;
    let same = epoch == old_epoch & source == old_source;
    let advance = old_epoch != 0xFFFF & old_source != 0xFFFFFFFF &
                  epoch == old_epoch + 1 & source == old_source + 1;
    if invocation == 0 | not_bool(bank.domain_bound) | epoch == 0x0000 |
       source == 0x00000000 | not_bool(first | same | advance) then None()
    else {
      let receive = if first | advance then
        { bank.receive with epoch = epoch, sequence = 0x000000000000 } else bank.receive;
      let diagnostics = if advance then {
        receive with last_success = None(), ack_result_valid = false, rx_result = 0x00
      } else receive;
      let tx_sequence = if first | advance then 0x0000000000000000 else bank.tx_sequence;
      let configured = {
        bank with receive = diagnostics, source_epoch = source, tx_sequence = tx_sequence
      };
      let active = if bank.invocation == invocation then configured
                   else msgb_clear_endpoint_invocation(configured);
      Some({ active with invocation = invocation, enabled = true })
    }
  }
}

function msgb_diagnostic_word(result : bits(8), valid : bool) -> bits(64) = {
  sail_zeros(55) @ (if valid then 0b1 else 0b0) @ result
}

function msgb_owned_snapshot(bank : msgb_endpoint, invocation : int) -> option(msgb_snapshot) = {
  match bank.receive.snapshot {
    Some(claim) if claim.owner_invocation == invocation => Some(claim),
    _ => None()
  }
}

// The instruction handler calls these accessors only after effect preflight.
function msgb_register_read(ctx : msgb_bse_context, address : bits(24)) -> option(bits(64)) = {
  let index = if msgb_config_address(address) then msgb_selected_endpoint(ctx)
              else msgb_context_index(ctx);
  let bank = msgb_endpoints[index];
  let owned = msgb_owned_snapshot(bank, ctx.key.invocation);
  if msgb_word_address(address) then {
    let raw = unsigned(address[3..0]);
    let word : range(0, 9) = if raw >= 1 & raw <= 10 then raw - 1 else 0;
    let (receive, value) = msgb_receive_read(bank.receive, ctx.key.invocation, word);
    msgb_endpoints = vector_update(msgb_endpoints, index, { bank with receive = receive });
    value
  } else match address {
    0x000830 => Some(bank.tx_control),
    0x00083C => {
      match owned {
        None() => Some(sail_zero_extend(bank.receive.rx_result, 64)),
        Some(claim) => {
          let count : bits(4) = sail_zeros(4) + claim.packet.word_count;
          Some(sail_zeros(48) @ count @ 0b00 @ (if claim.acked then 0b1 else 0b0) @
               0b1 @ bank.receive.rx_result)
        }
      }
    },
    0x00083D => match owned { Some(claim) => Some(claim.token), None() => Some(sail_zeros(64)) },
    0x00083E => match owned { Some(claim) => Some(claim.packet.message_id_hi), None() => None() },
    0x00083F => match owned { Some(claim) => Some(claim.packet.message_id_lo), None() => None() },
    0x000840 => match owned { Some(claim) => Some(claim.packet.control), None() => None() },
    0x000843 => Some(msgb_diagnostic_word(bank.receive.ack_result, bank.receive.ack_result_valid)),
    0x000844 => Some(bank.receive.ack_id),
    0x000845 => Some(bank.tx_id_hi),
    0x000846 => Some(bank.tx_id_lo),
    0x000847 => Some(msgb_diagnostic_word(bank.tx_result, bank.tx_result_valid)),
    0x000848 => Some(sail_zero_extend(msgb_endpoint_address(index), 64)),
    0x000849 => Some(sail_zero_extend(msgb_config_selection[msgb_selection_index(ctx)], 64)),
    0x00084A => Some(bank.source_epoch @ bank.receive.epoch @ sail_zeros(15) @
                     (if bank.enabled then 0b1 else 0b0)),
    0x00084B => Some(bank.domain),
    _ => None()
  }
}

function msgb_register_writable(address : bits(24)) -> bool = {
  msgb_config_address(address) | msgb_word_address(address) |
  address == 0x00083B | address == 0x000841 | address == 0x000842
}

function msgb_read_preflight(ctx : msgb_bse_context, address : bits(24)) -> msgb_bse_outcome = {
  if address == 0x00083B | address == 0x000841 | address == 0x000842 then
    MSGB_BSE_BAD_CONTEXT
  else if msgb_config_address(address) then
    if ctx.key.acr == 0x0 then MSGB_BSE_COMPLETED else MSGB_BSE_BAD_CONTEXT
  else msgb_effect_preflight(ctx, false)
}

function msgb_register_write(ctx : msgb_bse_context, address : bits(24), value : bits(64))
    -> bool = {
  if address == 0x000849 then {
    if value[63..4] != 0x000000000000000 then false
    else {
      msgb_config_selection = vector_update(msgb_config_selection, msgb_selection_index(ctx), value[3..0]);
      true
    }
  } else {
    let index = if msgb_config_address(address) then msgb_selected_endpoint(ctx)
                else msgb_context_index(ctx);
    let bank = msgb_endpoints[index];
    let updated : option(msgb_endpoint) =
      if msgb_word_address(address) then {
        let raw = unsigned(address[3..0]);
        let word : range(0, 9) = if raw >= 1 & raw <= 10 then raw - 1 else 0;
        Some({ bank with staging = vector_update(bank.staging, word, value) })
      } else match address {
        0x00083B => Some({ bank with receive = msgb_receive_claim(bank.receive, ctx.key.invocation, value) }),
        0x000841 => Some({ bank with receive = msgb_receive_release(bank.receive, ctx.key.invocation, value) }),
        0x000842 => Some({ bank with receive = msgb_receive_ack(bank.receive, ctx.key.invocation, value) }),
        0x00084A => msgb_configure_bank(bank, ctx.key.invocation, value),
        0x00084B =>
          if bank.enabled | not_bool(msgb_bank_quiescent(bank)) |
             (bank.domain_bound & bank.domain != value) then None()
          else Some({ bank with domain = value, domain_bound = true }),
        _ => None()
      };
    match updated {
      Some(next) => {
        msgb_endpoints = vector_update(msgb_endpoints, index, next);
        true
      },
      None() => false
    }
  }
}
