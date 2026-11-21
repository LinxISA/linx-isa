// Directed tests start with platform-configured endpoints and live invocations.

function seed_msgb_transport() -> unit = {
  let empty = msgb_empty_endpoint();
  let staging = vector_update(vector_init(10, 0x0000000000001357), 1, 0x0000000000002468);
  let sender = {
    empty with enabled = true, domain_bound = true, domain = 0x0000000000000001, invocation = 41,
    source_epoch = 0x00000005, receive = msgb_receive_reset(0x0001), staging = staging
  };
  let receiver = {
    empty with enabled = true, domain_bound = true, domain = 0x0000000000000001, invocation = 42,
    source_epoch = 0x00000009, receive = msgb_receive_reset(0x0002), waiting = true
  };
  let service = { receiver with invocation = 1 };
  msgb_endpoints = vector_init(257, empty);
  msgb_endpoints = vector_update(msgb_endpoints, 0, sender);
  msgb_endpoints = vector_update(msgb_endpoints, 128, receiver);
  msgb_endpoints = vector_update(msgb_endpoints, msgb_service_index, service);
  msgb_cores = vector_init(2, struct { active_invocation = Some(41), draining = false });
  msgb_cores = vector_update(msgb_cores, 1, struct { active_invocation = Some(42), draining = false })
}

function verify_msgb_transport() -> unit = {
  let control : bits(64) = 0x0000000200000080;
  seed_msgb_transport();
  assert(msgb_admit_packet(0, 0x0000000B00000080, true) == msgb_bad_command);
  assert(msgb_admit_packet(0, 0x0000000200000100, true) == msgb_bad_command);
  assert(msgb_admit_packet(0, control, false) == msgb_busy);
  assert(msgb_endpoints[0].tx_sequence == 0x0000000000000000);
  assert(is_none(msgb_endpoints[128].receive.queued));
  assert(msgb_admit_packet(0, control, true) == msgb_ok);
  assert(msgb_endpoints[0].tx_sequence == 0x0000000000000001);
  assert(msgb_endpoints[0].tx_id_hi == 0x0000000000000005);
  assert(msgb_endpoints[0].tx_control == control);
  assert(not_bool(msgb_endpoints[128].waiting));
  assert(msgb_admit_packet(0, control, true) == msgb_busy);
  assert(msgb_endpoints[0].tx_sequence == 0x0000000000000001);
  match msgb_endpoints[128].receive.queued {
    Some(packet) => {
      assert(packet.source_invocation == 41);
      assert(packet.destination_invocation == 42);
      assert(packet.message_id_lo == 0x0000000000000001);
      assert(packet.word_count == 2);
      assert(packet.words[0] == 0x0000000000001357);
      assert(packet.words[1] == 0x0000000000002468);
      assert(packet.words[2] == 0x0000000000000000)
    },
    None() => assert(false)
  };

  seed_msgb_transport();
  let core = msgb_cores[1];
  msgb_cores = vector_update(msgb_cores, 1, { core with draining = true });
  assert(msgb_admit_packet(0, control, true) == msgb_bad_command);
  assert(is_none(msgb_endpoints[128].receive.queued));
  seed_msgb_transport();
  let target = msgb_endpoints[128];
  let exhausted = { target.receive with sequence = 0xFFFFFFFFFFFF };
  msgb_endpoints = vector_update(msgb_endpoints, 128, { target with receive = exhausted });
  assert(msgb_admit_packet(0, control, true) == msgb_exhausted);
  assert(is_none(msgb_endpoints[128].receive.queued));

  // The final TX identity and the final service RX claim are reserved for DONE.
  seed_msgb_transport();
  let sender = msgb_endpoints[0];
  let done_words = vector_update(vector_update(sender.staging, 0, 0x0000000000000003), 1, 0x0000000000000123);
  let running = {
    sender with dispatch_id = Some(0x0000000000000123),
    tx_sequence = 0xFFFFFFFFFFFFFFFE, staging = done_words
  };
  msgb_endpoints = vector_update(msgb_endpoints, 0, running);
  let service = msgb_endpoints[msgb_service_index];
  let service_rx = { service.receive with sequence = 0xFFFFFFFFFFFE };
  msgb_endpoints = vector_update(msgb_endpoints, msgb_service_index, { service with receive = service_rx });
  assert(msgb_admit_packet(0, 0x00000001FFFFFFFF, true) == msgb_exhausted);
  assert(is_none(msgb_endpoints[msgb_service_index].receive.queued));
  assert(msgb_admit_packet(0, 0x00000003FFFFFFFF, true) == msgb_ok);
  assert(msgb_endpoints[0].tx_sequence == 0xFFFFFFFFFFFFFFFF);
  assert(is_some(msgb_endpoints[msgb_service_index].receive.queued));

  // One atomic update keeps both sides of a self-addressed send.
  seed_msgb_transport();
  assert(msgb_admit_packet(0, 0x0000000100000000, true) == msgb_ok);
  assert(msgb_endpoints[0].tx_sequence == 0x0000000000000001);
  assert(is_some(msgb_endpoints[0].receive.queued))
}

function verify_msgb_bse() -> unit = {
  seed_msgb_transport();
  let key : msgb_send_key = struct {
    invocation = 41, acr = 0x0, execution_domain = 9, tpc = 0x0000000000001000
  };
  let context : msgb_bse_context = struct {
    core = 0, pe = 0, slot = 0, key = key, kernel_origin = true,
    atomic = false, far = false, gm_permits = true
  };
  let control : bits(64) = 0x0000000200000080;
  match msgb_bse({ context with gm_permits = false }, control) {
    MSGB_BSE_BLOCKED => (),
    _ => assert(false)
  };
  match msgb_bse({ context with far = true }, control) {
    MSGB_BSE_BAD_ENVELOPE => (),
    _ => assert(false)
  };
  assert(not_bool(msgb_endpoints[0].tx_result_valid));
  assert(is_none(msgb_endpoints[128].receive.queued));
  match msgb_bse(context, control) {
    MSGB_BSE_COMPLETED => (),
    _ => assert(false)
  };
  assert(msgb_endpoints[0].tx_result == msgb_ok);
  assert(msgb_endpoints[0].tx_sequence == 0x0000000000000001);
  let target = msgb_endpoints[128];
  let receive = { target.receive with queued = None() };
  msgb_endpoints = vector_update(msgb_endpoints, 128, { target with receive = receive });
  let later_key = { key with tpc = 0x0000000000001004 };
  let later_context = { context with key = later_key };
  let _ = msgb_bse(later_context, control);
  assert(msgb_endpoints[0].tx_result == msgb_ok);
  assert(msgb_endpoints[0].tx_sequence == 0x0000000000000002);
  // The prior instruction replay returns its original identity without
  // replacing the already queued second message.
  let _ = msgb_bse(context, control);
  assert(msgb_endpoints[0].tx_result == msgb_duplicate);
  assert(msgb_endpoints[0].tx_id_lo == 0x0000000000000001);
  assert(msgb_endpoints[0].tx_sequence == 0x0000000000000002);
  match msgb_endpoints[128].receive.queued {
    Some(packet) => assert(packet.message_id_lo == 0x0000000000000002),
    None() => assert(false)
  };
  let _ = msgb_bse(context, 0x0000000100000080);
  assert(msgb_endpoints[0].tx_result == msgb_bad_command);
  assert(msgb_endpoints[0].tx_control == control);
  assert(msgb_endpoints[0].tx_id_lo == 0x0000000000000001);

  // Draining blocks new admission. Retiring the source preserves a remote
  // packet and the source bank's non-wrapping identity counters.
  msgb_begin_drain(0);
  let fresh_key = { key with tpc = 0x0000000000001008 };
  let _ = msgb_bse({ context with key = fresh_key }, control);
  assert(msgb_endpoints[0].tx_result == msgb_bad_command);
  assert(not_bool(msgb_retire_invocation(1, 42)));
  assert(msgb_retire_invocation(0, 41));
  assert(not_bool(msgb_endpoints[0].enabled));
  assert(msgb_endpoints[0].domain_bound);
  assert(msgb_endpoints[0].tx_sequence == 0x0000000000000002);
  assert(not_bool(msgb_endpoints[0].tx_result_valid));
  assert(is_none(msgb_endpoints[0].receipts[0]));
  assert(is_some(msgb_endpoints[128].receive.queued))
}
