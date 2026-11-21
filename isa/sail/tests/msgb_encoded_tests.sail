// Drive the MSGB register path, BSE/BWE and HSCB geometry through decoded words.

function verify_msgb_encoded() -> unit = {
  seed_msgb_transport();
  msgb_endpoints = vector_update(msgb_endpoints, 0, msgb_empty_endpoint());
  msgb_config_selection = vector_init(16, 0x0);
  let old_cstate = ssr_cstate;
  let old_valid = barg_valid;
  let old_block_type = barg_block_type_cur;
  ssr_cstate = 0x0000000000000000;
  barg_valid = true;
  barg_block_type_cur = 0b0001;
  reset_scalar_subset_trap_case(0x0000000000001800);
  let key : msgb_send_key = struct {
    invocation = 41, acr = 0x0, execution_domain = 19, tpc = 0x0000000000000000
  };
  let ctx : msgb_bse_context = struct {
    core = 0, pe = 0, slot = 0, key = key, kernel_origin = true,
    atomic = false, far = false, gm_permits = true
  };
  msgb_platform_context = Some(ctx);
  let first_epoch = architecture_request_epoch;
  write_reg5(0b00100, 0xFEDCBA9876543210);
  decode_execute32(0x0002002B); // Disabled BSE publishes legacy SendEvent.
  match last_control_request { SendEvent => (), _ => assert(false) };
  assert(control_request_operand == 0xFEDCBA9876543210);
  assert(architecture_request_epoch == first_epoch + 1);
  barg_block_type_cur = 0b0000;
  decode_execute32(0x0012002B); // WaitEvent is confined to a SYS block.
  assert(last_trapnum == trapnum_block_trap());
  assert(architecture_request_epoch == first_epoch + 1);
  assert(control_request_operand == 0xFEDCBA9876543210);
  barg_block_type_cur = 0b0001;
  last_e = 0b0;
  write_reg5(0b00100, 0x0000000500010001);
  decode_execute32(0x84A2103B); // SSRSET r4, MSGBCFG before domain binding
  assert(last_trapnum == trapnum_illegal_inst());
  assert(not_bool(msgb_endpoints[0].enabled));
  last_e = 0b0;
  write_reg5(0b00100, 0x0000000000000001);
  decode_execute32(0x84B2103B); // MSGBDOMAIN
  assert(msgb_endpoints[0].domain_bound);
  write_reg5(0b00100, 0x0000000500010001);
  decode_execute32(0x84A2103B); // MSGBCFG
  assert(last_e == 0b0);
  assert(msgb_endpoints[0].enabled);
  decode_execute32(0x84A001BB); // SSRGET MSGBCFG, ->r3
  assert(read_reg5(0b00011) == 0x0000000500010001);
  ssr_cstate = 0x0000000000000001;
  decode_execute32(0x84A001BB);
  assert(last_e == 0b1);
  assert(read_reg5(0b00011) == 0x0000000500010001);
  ssr_cstate = 0x0000000000000000;
  last_e = 0b0;

  msgb_platform_context = Some({ ctx with gm_permits = false, kernel_origin = false, atomic = true });
  decode_execute32(0x84A001BB); // ACR0 configuration reads bypass effect blocking
  assert(not_bool(msgb_instruction_blocked));
  assert(last_e == 0b0);
  assert(read_reg5(0b00011) == 0x0000000500010001);
  msgb_platform_context = Some({ ctx with gm_permits = false });
  decode_execute32(0x848001BB); // MSGBENDPOINT must wait for older GM recovery
  assert(msgb_instruction_blocked);
  assert(last_e == 0b0);
  assert(read_reg5(0b00011) == 0x0000000500010001);
  decode_execute32(0x83B001BB); // SSRGET a write-only register faults first
  assert(not_bool(msgb_instruction_blocked));
  assert(last_trapnum == trapnum_illegal_inst());
  assert(read_reg5(0b00011) == 0x0000000500010001);
  last_e = 0b0;
  decode_execute32(0x842001BB); // ACK is also a write-only command
  assert(last_e == 0b1);
  assert(not_bool(msgb_instruction_blocked));
  assert(read_reg5(0b00011) == 0x0000000500010001);
  last_e = 0b0;
  msgb_platform_context = Some(ctx);
  decode_execute32(0x848001BB);
  assert(not_bool(msgb_instruction_blocked));
  assert(read_reg5(0b00011) == 0x0000000000000000);

  write_reg5(0b00100, 0x0000000000000001);
  decode_execute32(0x8312103B); // SSRSET r4, MSGBD1 (READY)
  let control : bits(64) = 0x00000001FFFFFFFF;
  write_reg5(0b00100, control);
  decode_execute32(0x0002002B); // BSE r4
  assert(last_e == 0b0);
  assert(msgb_endpoints[0].tx_result == msgb_ok);
  assert(hscb_receive_worker_message() == msgb_ok);
  assert(msgb_endpoints[0].ready);
  decode_execute32(0x0012002B); // BWE r4 publishes the exact nonblocking request.
  match last_control_request { WaitEvent => (), _ => assert(false) };
  assert(control_request_operand == control);
  assert(architecture_request_epoch == first_epoch + 2);
  assert(msgb_endpoints[0].waiting);

  write_reg5(0b00100, 0x0000000000000000);
  decode_execute32(0x84A2103B);
  assert(not_bool(msgb_endpoints[0].enabled));
  write_reg5(0b00100, 0x0000000600020001);
  decode_execute32(0x84A2103B);
  assert(msgb_endpoints[0].enabled);
  assert(msgb_endpoints[0].source_epoch == 0x00000006);
  write_reg5(0b00100, control);
  decode_execute32(0x0002002B); // Same dynamic occurrence after epoch advance
  assert(msgb_endpoints[0].tx_result == msgb_duplicate);
  assert(msgb_endpoints[0].tx_id_hi == 0x0000000000000005);
  assert(is_none(msgb_endpoints[msgb_service_index].receive.queued));

  let stale_key = { key with invocation = 42 };
  msgb_platform_context = Some({ ctx with key = stale_key });
  write_reg5(0b00100, 0x0123456789ABCDEF);
  decode_execute32(0x0002002B); // A bank bound to another invocation selects SendEvent.
  assert(last_e == 0b0);
  match last_control_request { SendEvent => (), _ => assert(false) };
  assert(control_request_operand == 0x0123456789ABCDEF);
  assert(architecture_request_epoch == first_epoch + 3);
  assert(msgb_endpoints[0].tx_result == msgb_duplicate);
  assert(is_none(msgb_endpoints[msgb_service_index].receive.queued));
  decode_execute32(0x848001BB); // Operational reads still require the bound context.
  assert(last_trapnum == trapnum_illegal_inst());
  assert(read_reg5(0b00011) == 0x0000000000000000);
  msgb_platform_context = None();
  ssr_cstate = old_cstate;
  barg_valid = old_valid;
  barg_block_type_cur = old_block_type
}
