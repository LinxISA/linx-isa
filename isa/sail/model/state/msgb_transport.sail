// Atomic transport admission from PTO-ARCH-HSCB-TRANSPORT-001 at v0.59.1.0.
// The reference models two cores, eight workers per core, and 16 ACRs per worker.

type msgb_endpoint_index = range(0, 256)
type msgb_receipt_index = range(0, 15)
let msgb_service_index : int(256) = 256
let msgb_service_address : bits(32) = 0xFFFFFFFF

struct msgb_send_key = {
  invocation : int,
  acr : bits(4),
  execution_domain : int,
  tpc : bits(64)
}

struct msgb_send_receipt = {
  key : msgb_send_key,
  control : bits(64),
  id_hi : bits(64),
  id_lo : bits(64)
}

struct msgb_endpoint = {
  enabled : bool,
  domain_bound : bool,
  domain : bits(64),
  invocation : int,
  source_epoch : bits(32),
  tx_sequence : bits(64),
  tx_control : bits(64),
  tx_id_hi : bits(64),
  tx_id_lo : bits(64),
  tx_result : bits(8),
  tx_result_valid : bool,
  receipts : vector(16, option(msgb_send_receipt)),
  staging : vector(10, bits(64)),
  receive : msgb_receive_bank,
  dispatch_id : option(bits(64)),
  ready : bool,
  issued : vector(16, option(bits(64))),
  launch_id_hi : bits(64),
  launch_id_lo : bits(64),
  blocknum : bits(64),
  blockid : bits(64),
  return_value : bits(64),
  waiting : bool
}

struct msgb_core_state = {
  active_invocation : option(int),
  draining : bool
}

function msgb_empty_endpoint() -> msgb_endpoint = {
  struct {
    enabled = false,
    domain_bound = false,
    domain = 0x0000000000000000,
    invocation = 0,
    source_epoch = 0x00000000,
    tx_sequence = 0x0000000000000000,
    tx_control = 0x0000000000000000,
    tx_id_hi = 0x0000000000000000,
    tx_id_lo = 0x0000000000000000,
    tx_result = 0x00,
    tx_result_valid = false,
    receipts = vector_init(16, None()),
    staging = vector_init(10, 0x0000000000000000),
    receive = msgb_receive_reset(0x0000),
    dispatch_id = None(),
    ready = false,
    issued = vector_init(16, None()),
    launch_id_hi = 0x0000000000000000,
    launch_id_lo = 0x0000000000000000,
    blocknum = 0x0000000000000000,
    blockid = 0x0000000000000000,
    return_value = 0x0000000000000000,
    waiting = false
  }
}

register msgb_endpoints : vector(257, msgb_endpoint) =
  vector_init(257, msgb_empty_endpoint())
register msgb_cores : vector(2, msgb_core_state) =
  vector_init(2, struct { active_invocation = None(), draining = false })

function msgb_core_quiescent(core : range(0, 1)) -> bool = {
  var quiescent : bool = true;
  foreach (offset from 0 to 127) {
    let bank = msgb_endpoints[core * 128 + offset].receive;
    if is_some(bank.queued) | is_some(bank.snapshot) then quiescent = false
    else ()
  };
  quiescent
}

function msgb_begin_drain(core : range(0, 1)) -> unit = {
  let state = msgb_cores[core];
  msgb_cores = vector_update(msgb_cores, core, { state with draining = true })
}

// The kernel lifecycle checks completion and drain before asking transport to
// retire a bank. Remote packets already live in their destination banks.
function msgb_retire_invocation(core : range(0, 1), invocation : int) -> bool = {
  if invocation == 0 | not_bool(msgb_core_quiescent(core)) then false
  else {
    var endpoints = msgb_endpoints;
    foreach (offset from 0 to 127) {
      let index = core * 128 + offset;
      let bank = endpoints[index];
      if bank.invocation == invocation then {
        let empty = msgb_empty_endpoint();
        let receive = msgb_receive_reset(bank.receive.epoch);
        let cleared = {
          empty with domain_bound = bank.domain_bound, domain = bank.domain,
          source_epoch = bank.source_epoch, tx_sequence = bank.tx_sequence,
          receive = { receive with sequence = bank.receive.sequence }
        };
        endpoints = vector_update(endpoints, index, cleared)
      } else ()
    };
    msgb_endpoints = endpoints;
    true
  }
}

function msgb_endpoint_address(index : msgb_endpoint_index) -> bits(32) = {
  if index == msgb_service_index then msgb_service_address else sail_zeros(32) + index
}

function msgb_matches_done(source : msgb_endpoint, control : bits(64)) -> bool = {
  match source.dispatch_id {
    None() => false,
    Some(id) =>
      control == 0x00000003FFFFFFFF &
      source.staging[0] == 0x0000000000000003 &
      source.staging[1] == id
  }
}

function msgb_outstanding_dispatch_count() -> int = {
  var count : int = 0;
  foreach (worker from 0 to 15) {
    if is_some(msgb_endpoints[worker * 16].dispatch_id) then count = count + 1
    else ()
  };
  count
}

function msgb_target_live(index : msgb_endpoint_index, invocation : int) -> bool = {
  if index == msgb_service_index then true
  else {
    let core = msgb_cores[if index < 128 then 0 else 1];
    if core.draining then false
    else match core.active_invocation {
      None() => false,
      Some(active) => active == invocation
    }
  }
}

function msgb_admit_packet(
  source_index : msgb_endpoint_index, control : bits(64), capacity_available : bool
) -> bits(8) = {
  let destination = control[31..0];
  let raw_count = unsigned(control[35..32]);
  if control[63..36] != 0x0000000 | raw_count > 10 |
     (unsigned(destination) >= 256 & destination != msgb_service_address) then msgb_bad_command
  else {
    let count : range(0, 10) = if raw_count <= 10 then raw_count else 0;
    let target_index : msgb_endpoint_index =
      if destination == msgb_service_address then msgb_service_index
      else unsigned(destination[7..0]);
    let source = msgb_endpoints[source_index];
    let target = msgb_endpoints[target_index];
    if not_bool(source.enabled & target.enabled) | source.domain != target.domain |
       not_bool(msgb_target_live(target_index, target.invocation)) then msgb_bad_command
    else if is_some(target.receive.queued) | not_bool(capacity_available) then msgb_busy
    else if target.receive.sequence == 0xFFFFFFFFFFFF then msgb_exhausted
    else {
      let done = msgb_matches_done(source, control);
      let remaining = unsigned(0xFFFFFFFFFFFF) - unsigned(target.receive.sequence);
      if target_index == msgb_service_index & not_bool(done) &
         remaining <= msgb_outstanding_dispatch_count() then msgb_exhausted
      else if source.tx_sequence == 0xFFFFFFFFFFFFFFFF |
              (not_bool(done) & is_some(source.dispatch_id) &
               source.tx_sequence == 0xFFFFFFFFFFFFFFFE) then msgb_exhausted
      else {
        let id_hi = msgb_endpoint_address(source_index) @ source.source_epoch;
        let id_lo = source.tx_sequence + 1;
        var words : vector(10, bits(64)) = vector_init(10, 0x0000000000000000);
        foreach (word from 0 to 9) {
          if word < count then words = vector_update(words, word, source.staging[word])
          else ()
        };
        let packet : msgb_packet = struct {
          source_invocation = source.invocation,
          destination_invocation = target.invocation,
          message_id_hi = id_hi,
          message_id_lo = id_lo,
          control = control,
          word_count = count,
          words = words
        };
        let tx = { source with tx_sequence = id_lo, tx_control = control, tx_id_hi = id_hi, tx_id_lo = id_lo };
        let after_tx = vector_update(msgb_endpoints, source_index, tx);
        // Use the updated endpoint in case the sender addressed its own bank.
        let receiver = after_tx[target_index];
        let receive = { receiver.receive with queued = Some(packet) };
        msgb_endpoints = vector_update(after_tx, target_index, { receiver with receive = receive, waiting = false });
        msgb_ok
      }
    }
  }
}
