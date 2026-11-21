// A configured worker announces READY, accepts an identified launch, and
// completes only when the service consumes a matching DONE.

function set_hscb_test_payload(kind : bits(64), id : bits(64), argument : bits(64)) -> unit = {
  let bank = msgb_endpoints[0];
  let words0 = vector_update(bank.staging, 0, kind);
  let words1 = vector_update(words0, 1, id);
  let words = vector_update(words1, 2, argument);
  msgb_endpoints = vector_update(msgb_endpoints, 0, { bank with staging = words })
}

function verify_hscb_dispatch() -> unit = {
  seed_msgb_transport();
  msgb_endpoints = vector_update(msgb_endpoints, msgb_service_index, msgb_empty_endpoint());
  hscb_enable_service();
  hscb_enable_service();
  let key : msgb_send_key = struct {
    invocation = 41, acr = 0x0, execution_domain = 9, tpc = 0x0000000000001020
  };
  let ctx : msgb_bse_context = struct {
    core = 0, pe = 0, slot = 0, key = key, kernel_origin = true,
    atomic = false, far = false, gm_permits = true
  };
  let id : bits(64) = 0x0000000000000123;
  let entry : bits(64) = 0x0000000000000400;
  let argument : bits(64) = 0x0000000000000200;
  let zero : bits(64) = 0x0000000000000000;
  let one : bits(64) = 0x0000000000000001;
  let two : bits(64) = 0x0000000000000002;
  let three : bits(64) = 0x0000000000000003;
  assert(hscb_issue_launch(0, id, entry, argument) == msgb_bad_command);
  set_hscb_test_payload(one, zero, zero);
  let _ = msgb_bse(ctx, 0x00000001FFFFFFFF);
  assert(msgb_endpoints[0].tx_result == msgb_ok);
  assert(hscb_receive_worker_message() == msgb_ok);
  assert(msgb_endpoints[0].ready);
  hscb_observe_wait(ctx);
  assert(msgb_endpoints[0].waiting);
  assert(hscb_issue_block_launch(0, id, entry, argument, zero, zero) == msgb_bad_command);
  assert(hscb_issue_block_launch(0, id, entry, argument, three, two) == msgb_ok);
  assert(not_bool(msgb_endpoints[0].waiting));
  assert(msgb_endpoints[0].blocknum == three);
  assert(msgb_endpoints[0].blockid == two);
  let old_cstate = ssr_cstate;
  ssr_cstate = 0x0000000000000000;
  msgb_platform_context = Some(ctx);
  decode_execute32(0x050001BB);
  assert(read_reg5(0b00011) == three);
  decode_execute32(0x051001BB);
  assert(read_reg5(0b00011) == two);
  msgb_platform_context = Some({ ctx with slot = 1 });
  decode_execute32(0x050001BB);
  assert(read_reg5(0b00011) == ssr_blocknum);
  msgb_platform_context = Some(ctx);
  assert(not_bool(hscb_worker_accepts_launch(ctx)));
  let bank = msgb_endpoints[0];
  var receive : msgb_receive_bank = msgb_receive_claim(bank.receive, 41, one);
  assert(receive.rx_result == msgb_ok);
  msgb_endpoints = vector_update(msgb_endpoints, 0, { bank with receive = receive });
  assert(not_bool(hscb_worker_accepts_launch(ctx)));
  foreach (word from 0 to 3) {
    let (next, _) = msgb_receive_read(receive, 41, word);
    receive = next
  };
  msgb_endpoints = vector_update(msgb_endpoints, 0, { bank with receive = receive });
  assert(hscb_worker_accepts_launch(ctx));
  assert(not_bool(hscb_worker_accepts_launch({ ctx with slot = 1 })));
  match receive.snapshot {
    Some(claim) => {
      assert(claim.packet.words[2] == entry);
      assert(claim.packet.words[3] == argument);
      let fake_packet = { claim.packet with message_id_hi = 0x0000008000000009 };
      let fake_claim = { claim with packet = fake_packet };
      let fake_receive = { receive with snapshot = Some(fake_claim) };
      msgb_endpoints = vector_update(msgb_endpoints, 0, { bank with receive = fake_receive });
      assert(not_bool(hscb_worker_accepts_launch(ctx)));
      receive = msgb_receive_ack(receive, 41, claim.token);
      assert(receive.ack_result == msgb_ok);
      receive = msgb_receive_release(receive, 41, claim.token)
    },
    None() => assert(false)
  };
  msgb_endpoints = vector_update(msgb_endpoints, 0, { bank with receive = receive });
  assert(not_bool(hscb_worker_accepts_launch(ctx)));

  let wrong_key = { key with tpc = 0x0000000000001024 };
  set_hscb_test_payload(three, id + 1, zero);
  let _ = msgb_bse({ ctx with key = wrong_key }, 0x00000003FFFFFFFF);
  assert(hscb_receive_worker_message() == msgb_bad_command);
  assert(msgb_endpoints[0].blocknum == three);
  let done_key = { key with tpc = 0x0000000000001028 };
  set_hscb_test_payload(three, id, 0x0000000000000067);
  let _ = msgb_bse({ ctx with key = done_key }, 0x00000003FFFFFFFF);
  assert(hscb_receive_worker_message() == msgb_ok);
  assert(is_none(msgb_endpoints[0].dispatch_id));
  assert(msgb_endpoints[0].blocknum == zero);
  assert(msgb_endpoints[0].blockid == zero);
  assert(msgb_endpoints[0].return_value == 0x0000000000000067);
  decode_execute32(0x050001BB);
  assert(read_reg5(0b00011) == ssr_blocknum);
  msgb_platform_context = None();
  ssr_cstate = old_cstate;
  assert(hscb_issue_launch(0, id, entry, argument) == msgb_bad_command);
  assert(hscb_issue_launch(0, id + 1, entry, argument) == msgb_ok);
  assert(msgb_endpoints[0].blocknum == one);
  assert(msgb_endpoints[0].blockid == zero)
}
