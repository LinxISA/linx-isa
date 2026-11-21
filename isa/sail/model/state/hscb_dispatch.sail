// Resident worker service from PTO-ARCH-HSCB-DISPATCH-001 and
// PTO-ARCH-HSCB-BLOCK-LAUNCH-001 at PTO v0.59.1.0.

// Platform-provided Core/PE/thread and invocation for architectural SSR reads.
// ACR is taken from the live scalar state.
register msgb_platform_context : option(msgb_bse_context) = None()

function hscb_read_geometry(address : bits(24)) -> option(bits(64)) = {
  if address != 0x000050 & address != 0x000051 then None()
  else match msgb_platform_context {
    None() => None(),
    Some(platform) => {
      let key = { platform.key with acr = current_acr_id() };
      let context = { platform with key = key };
      let bank = msgb_endpoints[msgb_context_index(context)];
      if msgb_kernel_context_active(context, bank) & is_some(bank.dispatch_id) then
        Some(if address == 0x000050 then bank.blocknum else bank.blockid)
      else None()
    }
  }
}

function hscb_enable_service() -> unit = {
  let service = msgb_endpoints[msgb_service_index];
  if not_bool(service.enabled) then {
    let receive = { service.receive with epoch = 0x0001 };
    let enabled = {
      service with enabled = true, domain_bound = true, domain = 0x0000000000000001,
      invocation = 1, source_epoch = 0x00000001, receive = receive
    };
    msgb_endpoints = vector_update(msgb_endpoints, msgb_service_index, enabled)
  } else ()
}

function hscb_observe_wait(ctx : msgb_bse_context) -> unit = {
  let index = msgb_context_index(ctx);
  let bank = msgb_endpoints[index];
  if msgb_endpoints[msgb_service_index].enabled & msgb_kernel_context_active(ctx, bank) then {
    let waiting = { bank with waiting = is_none(bank.receive.queued) };
    msgb_endpoints = vector_update(msgb_endpoints, index, waiting)
  } else ()
}

function hscb_worker_accepts_launch(ctx : msgb_bse_context) -> bool = {
  let bank = msgb_endpoints[msgb_context_index(ctx)];
  if not_bool(msgb_kernel_context_active(ctx, bank)) then false
  else match (bank.dispatch_id, bank.receive.snapshot) {
    (Some(id), Some(claim)) =>
      claim.owner_invocation == ctx.key.invocation & not_bool(claim.acked) &
      claim.packet.word_count == 4 & msgb_receive_complete(claim) &
      claim.packet.message_id_hi[63..32] == msgb_service_address &
      claim.packet.message_id_hi == bank.launch_id_hi &
      claim.packet.message_id_lo == bank.launch_id_lo &
      claim.packet.words[0] == 0x0000000000000002 &
      claim.packet.words[1] == id &
      claim.packet.words[2] != 0x0000000000000000 &
      claim.packet.words[2][0] == 0b0,
    _ => false
  }
}

function hscb_issued_id_seen(issued : vector(16, option(bits(64))), id : bits(64)) -> bool = {
  var seen : bool = false;
  foreach (slot from 0 to 15) {
    match issued[slot] {
      Some(previous) if previous == id => seen = true,
      _ => ()
    }
  };
  seen
}

function hscb_free_issue_slot(issued : vector(16, option(bits(64))))
    -> option(msgb_receipt_index) = {
  var found : option(msgb_receipt_index) = None();
  foreach (slot from 0 to 15) {
    if is_none(issued[slot]) & is_none(found) then found = Some(slot) else ()
  };
  found
}

function hscb_issue_block_launch(
  worker : msgb_endpoint_index, id : bits(64), entry : bits(64), argument : bits(64),
  count : bits(64), block : bits(64)
) -> bits(8) = {
  let target = msgb_endpoints[worker];
  let service = msgb_endpoints[msgb_service_index];
  if not_bool(service.enabled) | worker == msgb_service_index |
     msgb_endpoint_address(worker)[3..0] != 0x0 |
     entry == 0x0000000000000000 | entry[0] == 0b1 |
     count == 0x0000000000000000 | count[63..32] != 0x00000000 |
     block[63..32] != 0x00000000 | unsigned(block) >= unsigned(count) |
     not_bool(target.ready) then msgb_bad_command
  else if is_some(target.dispatch_id) | is_some(service.receive.queued) |
          is_some(service.receive.snapshot) then msgb_busy
  else if hscb_issued_id_seen(target.issued, id) then msgb_bad_command
  else match hscb_free_issue_slot(target.issued) {
    None() => msgb_exhausted,
    Some(slot) => {
      let host_claims_left = unsigned(0xFFFFFFFFFFFF) - unsigned(service.receive.sequence);
      if is_none(msgb_find_free(target.receipts, false)) |
         target.tx_sequence == 0xFFFFFFFFFFFFFFFF | target.receive.sequence == 0xFFFFFFFFFFFF |
         host_claims_left <= msgb_outstanding_dispatch_count() then msgb_exhausted
      else {
        let words0 = vector_update(service.staging, 0, 0x0000000000000002);
        let words1 = vector_update(words0, 1, id);
        let words2 = vector_update(words1, 2, entry);
        let words = vector_update(words2, 3, argument);
        msgb_endpoints = vector_update(msgb_endpoints, msgb_service_index, { service with staging = words });
        let control = 0x00000004 @ msgb_endpoint_address(worker);
        let result = msgb_admit_packet(msgb_service_index, control, true);
        if result == msgb_ok then {
          let admitted = msgb_endpoints[worker];
          let host = msgb_endpoints[msgb_service_index];
          let issued = vector_update(admitted.issued, slot, Some(id));
          let running = {
            admitted with dispatch_id = Some(id), issued = issued,
            launch_id_hi = host.tx_id_hi, launch_id_lo = host.tx_id_lo,
            blocknum = count, blockid = block
          };
          msgb_endpoints = vector_update(msgb_endpoints, worker, running)
        } else ();
        result
      }
    }
  }
}

function hscb_issue_launch(worker : msgb_endpoint_index, id : bits(64), entry : bits(64), argument : bits(64))
    -> bits(8) = {
  hscb_issue_block_launch(worker, id, entry, argument, 0x0000000000000001, 0x0000000000000000)
}

function hscb_accept_worker_packet(packet : msgb_packet) -> bits(8) = {
  let source = packet.message_id_hi[63..32];
  if unsigned(source) >= 256 | source[3..0] != 0x0 then msgb_bad_command
  else {
    let worker = unsigned(source[7..0]);
    let bank = msgb_endpoints[worker];
    if not_bool(bank.enabled) | bank.invocation != packet.source_invocation then msgb_not_owner
    else if packet.word_count == 1 & packet.words[0] == 0x0000000000000001 & not_bool(bank.ready) then {
      msgb_endpoints = vector_update(msgb_endpoints, worker, { bank with ready = true });
      msgb_ok
    } else match bank.dispatch_id {
      Some(id) if packet.word_count == 3 & packet.words[0] == 0x0000000000000003 &
                  packet.words[1] == id => {
        let finished = {
          bank with dispatch_id = None(), launch_id_hi = 0x0000000000000000,
          launch_id_lo = 0x0000000000000000, blocknum = 0x0000000000000000,
          blockid = 0x0000000000000000, return_value = packet.words[2]
        };
        msgb_endpoints = vector_update(msgb_endpoints, worker, finished);
        msgb_ok
      },
      _ => msgb_bad_command
    }
  }
}

function hscb_receive_worker_message() -> bits(8) = {
  let service = msgb_endpoints[msgb_service_index];
  if not_bool(service.enabled) then msgb_bad_command
  else {
    var receive : msgb_receive_bank = msgb_receive_claim(service.receive, service.invocation, 0x0000000000000001);
    let result : bits(8) = match receive.snapshot {
      Some(claim) if receive.rx_result == msgb_ok => {
        foreach (word from 0 to 9) {
          if word < claim.packet.word_count then {
            let (next, _) = msgb_receive_read(receive, service.invocation, word);
            receive = next
          } else ()
        };
        receive = msgb_receive_ack(receive, service.invocation, claim.token);
        if receive.ack_result == msgb_ok then {
          receive = msgb_receive_release(receive, service.invocation, claim.token);
          receive.rx_result
        } else receive.ack_result
      },
      _ => receive.rx_result
    };
    msgb_endpoints = vector_update(msgb_endpoints, msgb_service_index, { service with receive = receive });
    if result != msgb_ok then result
    else match service.receive.queued {
      Some(packet) => hscb_accept_worker_packet(packet),
      None() => msgb_io_error
    }
  }
}
