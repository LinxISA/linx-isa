// Directed receive transitions mirroring the PTO v0.59.1.0 MSGB AVS.

function assert_msgb_word(word : option(bits(64)), expected : bits(64)) -> unit = {
  match word {
    Some(value) => assert(value == expected),
    None() => assert(false)
  }
}

function assert_msgb_claim(bank : msgb_receive_bank, token : bits(64), acked : bool) -> unit = {
  match bank.snapshot {
    Some(claim) => {
      assert(claim.token == token);
      assert(claim.acked == acked)
    },
    None() => assert(false)
  }
}

function verify_msgb_receive() -> unit = {
  let claim_command : bits(64) = 0x0000000000000001;
  let token1 : bits(64) = 0x0001000000000001;
  let token2 : bits(64) = 0x0001000000000002;
  let token3 : bits(64) = 0x0001000000000003;
  let final_token : bits(64) = 0x0001FFFFFFFFFFFF;
  let initial = msgb_receive_reset(0x0001);
  let words = vector_update(vector_init(10, 0x0000000000001234), 1, 0xFEDCBA9876543210);
  let packet : msgb_packet = struct {
    source_invocation = 40,
    destination_invocation = 41,
    message_id_hi = 0x0000001000000001,
    message_id_lo = 0x0000000000000001,
    control = 0x0000000200000010,
    word_count = 2,
    words = words
  };

  assert(msgb_receive_claim(initial, 41, claim_command).rx_result == msgb_empty);
  let admitted = { initial with queued = Some(packet) };
  let claimed = msgb_receive_claim(admitted, 41, claim_command);
  assert(claimed.rx_result == msgb_ok);
  assert_msgb_claim(claimed, token1, false);
  assert(msgb_receive_claim(claimed, 41, claim_command).rx_result == msgb_busy);
  assert(msgb_receive_ack(claimed, 40, token1).ack_result == msgb_not_owner);
  assert(msgb_receive_ack(claimed, 41, 0x0002000000000001).ack_result == msgb_stale_epoch);
  let (unread, inaccessible) = msgb_receive_read(claimed, 40, 0);
  assert(is_none(inaccessible));
  let (still_unread, excess) = msgb_receive_read(unread, 41, 2);
  assert(is_none(excess));
  assert(msgb_receive_ack(still_unread, 41, token1).ack_result == msgb_not_read);
  let (partial, first) = msgb_receive_read(still_unread, 41, 0);
  assert_msgb_word(first, 0x0000000000001234);
  let incomplete = msgb_receive_ack(partial, 41, token1);
  assert(incomplete.ack_result == msgb_not_read);
  assert(is_some(incomplete.queued));

  // Cancelling a claim keeps the message. Reclaim allocates a fresh token and
  // starts a fresh read mask, so neither prior acknowledgment nor read applies.
  let cancelled = msgb_receive_release(incomplete, 41, token1);
  assert(is_none(cancelled.snapshot));
  let reclaimed = msgb_receive_claim(cancelled, 41, claim_command);
  assert_msgb_claim(reclaimed, token2, false);
  assert(msgb_receive_ack(reclaimed, 41, token1).ack_result == msgb_token_mismatch);
  let (only_second, second) = msgb_receive_read(reclaimed, 41, 1);
  assert_msgb_word(second, 0xFEDCBA9876543210);
  assert(msgb_receive_ack(only_second, 41, token2).ack_result == msgb_not_read);
  let (complete, _) = msgb_receive_read(only_second, 41, 0);
  let acknowledged = msgb_receive_ack(complete, 41, token2);
  assert(acknowledged.ack_result == msgb_ok);
  assert(is_none(acknowledged.queued));
  assert_msgb_claim(acknowledged, token2, true);
  let (retained, retained_word) = msgb_receive_read(acknowledged, 41, 1);
  assert_msgb_word(retained_word, 0xFEDCBA9876543210);
  let invalid = msgb_receive_ack(retained, 41, 0x0000000000000000);
  assert(invalid.ack_result == msgb_bad_token);
  assert(msgb_receive_ack(invalid, 41, token2).ack_result == msgb_duplicate);
  let released = msgb_receive_release(retained, 41, token2);
  assert(is_none(released.snapshot));
  let next_packet = { packet with message_id_lo = 0x0000000000000002 };
  let next_admitted = { released with queued = Some(next_packet) };
  let next_claimed = msgb_receive_claim(next_admitted, 41, claim_command);
  let duplicate = msgb_receive_ack(next_claimed, 41, token2);
  assert(duplicate.ack_result == msgb_duplicate);
  assert(is_some(duplicate.queued));
  assert_msgb_claim(duplicate, token3, false);

  // Cancelling a final unacknowledged claim would strand its queued packet.
  let near_exhaustion = { admitted with sequence = 0xFFFFFFFFFFFE };
  let final_claim = msgb_receive_claim(near_exhaustion, 41, claim_command);
  assert_msgb_claim(final_claim, final_token, false);
  let blocked_release = msgb_receive_release(final_claim, 41, final_token);
  assert(blocked_release.rx_result == msgb_exhausted);
  assert_msgb_claim(blocked_release, final_token, false);
  assert(is_some(blocked_release.queued));
  let (final_partial, _) = msgb_receive_read(blocked_release, 41, 0);
  let (final_complete, _) = msgb_receive_read(final_partial, 41, 1);
  let final_ack = msgb_receive_ack(final_complete, 41, final_token);
  assert(final_ack.ack_result == msgb_ok);
  assert(is_none(msgb_receive_release(final_ack, 41, final_token).snapshot))
}
