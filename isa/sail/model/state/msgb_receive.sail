// Receive transitions from PTO-ARCH-MSGB-ACK-001 at PTO v0.59.1.0.
// Transport owns queue admission. Every caller supplies the active invocation.

$include <option.sail>

let msgb_ok : bits(8) = 0x01
let msgb_duplicate : bits(8) = 0x02
let msgb_empty : bits(8) = 0x03
let msgb_busy : bits(8) = 0x04
let msgb_no_claim : bits(8) = 0x05
let msgb_not_owner : bits(8) = 0x06
let msgb_token_mismatch : bits(8) = 0x07
let msgb_stale_epoch : bits(8) = 0x08
let msgb_bad_token : bits(8) = 0x09
let msgb_not_read : bits(8) = 0x0A
let msgb_exhausted : bits(8) = 0x0B
let msgb_bad_command : bits(8) = 0x0C
let msgb_io_error : bits(8) = 0x0D

struct msgb_packet = {
  source_invocation : int,
  destination_invocation : int,
  message_id_hi : bits(64),
  message_id_lo : bits(64),
  control : bits(64),
  word_count : range(0, 10),
  words : vector(10, bits(64))
}

struct msgb_snapshot = {
  packet : msgb_packet,
  owner_invocation : int,
  token : bits(64),
  read_mask : bits(10),
  acked : bool
}

struct msgb_receive_bank = {
  epoch : bits(16),
  sequence : bits(48),
  queued : option(msgb_packet),
  snapshot : option(msgb_snapshot),
  rx_result : bits(8),
  ack_result : bits(8),
  ack_result_valid : bool,
  ack_id : bits(64),
  last_success : option(bits(64))
}

function msgb_receive_reset(epoch : bits(16)) -> msgb_receive_bank = {
  struct {
    epoch = epoch,
    sequence = 0x000000000000,
    queued = None(),
    snapshot = None(),
    rx_result = 0x00,
    ack_result = 0x00,
    ack_result_valid = false,
    ack_id = 0x0000000000000000,
    last_success = None()
  }
}

function msgb_receive_claim(bank : msgb_receive_bank, invocation : int, command : bits(64))
    -> msgb_receive_bank = {
  if command == 0x0000000000000000 then bank
  else if command != 0x0000000000000001 then { bank with rx_result = msgb_bad_command }
  else if is_some(bank.snapshot) then { bank with rx_result = msgb_busy }
  else match bank.queued {
    None() => { bank with rx_result = msgb_empty },
    Some(packet) => {
      if bank.sequence == 0xFFFFFFFFFFFF then { bank with rx_result = msgb_exhausted }
      else {
        let sequence = bank.sequence + 1;
        let claim : msgb_snapshot = struct {
          packet = packet,
          owner_invocation = invocation,
          token = bank.epoch @ sequence,
          read_mask = 0b0000000000,
          acked = false
        };
        { bank with sequence = sequence, snapshot = Some(claim), rx_result = msgb_ok }
      }
    }
  }
}

function msgb_receive_read(bank : msgb_receive_bank, invocation : int, word : range(0, 9))
    -> (msgb_receive_bank, option(bits(64))) = {
  match bank.snapshot {
    None() => (bank, None()),
    Some(claim) => {
      if claim.owner_invocation != invocation | word >= claim.packet.word_count then
        (bank, None())
      else {
        let read_mask = claim.read_mask | sail_shiftleft(0b0000000001, word);
        let updated_claim = { claim with read_mask = read_mask };
        ({ bank with snapshot = Some(updated_claim) }, Some(claim.packet.words[word]))
      }
    }
  }
}

function msgb_receive_token_check(bank : msgb_receive_bank, token : bits(64)) -> bits(8) = {
  if token[63..48] == 0x0000 | token[47..0] == 0x000000000000 then msgb_bad_token
  else if token[63..48] != bank.epoch then msgb_stale_epoch
  else msgb_ok
}

function msgb_receive_claim_check(
  claim : msgb_snapshot, invocation : int, token : bits(64)
) -> bits(8) = {
  if claim.owner_invocation != invocation then msgb_not_owner
  else if claim.token != token then msgb_token_mismatch
  else msgb_ok
}

function msgb_receive_complete(claim : msgb_snapshot) -> bool = {
  var complete : bool = true;
  foreach (word from 0 to 9) {
    if word < claim.packet.word_count & claim.read_mask[word] == 0b0 then
      complete = false
    else ()
  };
  complete
}

function msgb_receive_ack_result(bank : msgb_receive_bank, invocation : int, token : bits(64))
    -> bits(8) = {
  let duplicate : bool = match bank.last_success {
    Some(prior) => prior == token,
    None() => false
  };
  let token_check = msgb_receive_token_check(bank, token);
  if token_check != msgb_ok then token_check
  else if duplicate then msgb_duplicate
  else match bank.snapshot {
    None() => msgb_no_claim,
    Some(claim) => {
      let claim_check = msgb_receive_claim_check(claim, invocation, token);
      if claim_check != msgb_ok then claim_check
      else if not_bool(msgb_receive_complete(claim)) then msgb_not_read
      else match bank.queued {
        Some(packet) if packet.message_id_hi == claim.packet.message_id_hi &
                        packet.message_id_lo == claim.packet.message_id_lo => msgb_ok,
        _ => msgb_io_error
      }
    }
  }
}

function msgb_receive_ack(bank : msgb_receive_bank, invocation : int, token : bits(64))
    -> msgb_receive_bank = {
  let result = msgb_receive_ack_result(bank, invocation, token);
  let diagnostics = { bank with ack_result = result, ack_result_valid = true, ack_id = token };
  match bank.snapshot {
    Some(claim) if result == msgb_ok => {
      let acked = { claim with acked = true };
      { diagnostics with snapshot = Some(acked), queued = None(), last_success = Some(token) }
    },
    _ => diagnostics
  }
}

function msgb_receive_release(bank : msgb_receive_bank, invocation : int, token : bits(64))
    -> msgb_receive_bank = {
  let token_check = msgb_receive_token_check(bank, token);
  if token_check != msgb_ok then { bank with rx_result = token_check }
  else match bank.snapshot {
    None() => { bank with rx_result = msgb_no_claim },
    Some(claim) => {
      let claim_check = msgb_receive_claim_check(claim, invocation, token);
      if claim_check != msgb_ok then { bank with rx_result = claim_check }
      else if not_bool(claim.acked) & bank.sequence == 0xFFFFFFFFFFFF then
        { bank with rx_result = msgb_exhausted }
      else { bank with rx_result = msgb_ok, snapshot = None() }
    }
  }
}
