// LinxISA Sail common helpers for the canonical v0.56 model.

// IMPORTANT POLICY:
// - Missing semantics MUST be explicit (no guessed behavior).
// - `linx_unimplemented("MNEMONIC")` should be used until behavior is confirmed.

function linx_unimplemented(mnemonic : string) -> unit = {
  // Placeholder: in the final model this should raise a defined exception.
  ()
}

// Basic bit utilities.
function zext32(x : bits(64)) -> bits(64) = {
  sail_zeros(32) @ x[31..0]
}

function sext32(x : bits(64)) -> bits(64) = {
  let w = x[31..0];
  // Sign-extend from bit 31.
  if w[31] == 0b1 then sail_ones(32) @ w else sail_zeros(32) @ w
}

function zext32_from32(w : bits(32)) -> bits(64) = {
  sail_zeros(32) @ w
}

function zext8_from8(b : bits(8)) -> bits(64) = {
  sail_zeros(56) @ b
}

function sext32_from32(w : bits(32)) -> bits(64) = {
  if w[31] == 0b1 then sail_ones(32) @ w else sail_zeros(32) @ w
}

function zext12_to64(imm12 : bits(12)) -> bits(64) = {
  sail_zeros(52) @ imm12
}

function sext12_to64(imm12 : bits(12)) -> bits(64) = {
  if imm12[11] == 0b1 then sail_ones(52) @ imm12 else sail_zeros(52) @ imm12
}

function zext5_to64(imm5 : bits(5)) -> bits(64) = {
  sail_zeros(59) @ imm5
}

function sext5_to64(imm5 : bits(5)) -> bits(64) = {
  if imm5[4] == 0b1 then sail_ones(59) @ imm5 else sail_zeros(59) @ imm5
}

function zext24_to64(imm24 : bits(24)) -> bits(64) = {
  sail_zeros(40) @ imm24
}

function sext24_to64(imm24 : bits(24)) -> bits(64) = {
  if imm24[23] == 0b1 then sail_ones(40) @ imm24 else sail_zeros(40) @ imm24
}

function sext25_to64(imm25 : bits(25)) -> bits(64) = {
  if imm25[24] == 0b1 then sail_ones(39) @ imm25 else sail_zeros(39) @ imm25
}

function sext22_to64(imm22 : bits(22)) -> bits(64) = {
  if imm22[21] == 0b1 then sail_ones(42) @ imm22 else sail_zeros(42) @ imm22
}

function zext20_to64(imm20 : bits(20)) -> bits(64) = {
  sail_zeros(44) @ imm20
}

function sext20_to64(imm20 : bits(20)) -> bits(64) = {
  if imm20[19] == 0b1 then sail_ones(44) @ imm20 else sail_zeros(44) @ imm20
}

function sext17_to64(imm17 : bits(17)) -> bits(64) = {
  if imm17[16] == 0b1 then sail_ones(47) @ imm17 else sail_zeros(47) @ imm17
}

function sext29_to64(imm29 : bits(29)) -> bits(64) = {
  if imm29[28] == 0b1 then sail_ones(35) @ imm29 else sail_zeros(35) @ imm29
}

function sext30_to64(imm30 : bits(30)) -> bits(64) = {
  if imm30[29] == 0b1 then sail_ones(34) @ imm30 else sail_zeros(34) @ imm30
}

function sext32_to64(imm32 : bits(32)) -> bits(64) = {
  if imm32[31] == 0b1 then sail_ones(32) @ imm32 else sail_zeros(32) @ imm32
}

function mask_shamt64(x : bits(64)) -> bits(6) = {
  x[5..0]
}

function mask_shamt32(x : bits(64)) -> bits(5) = {
  x[4..0]
}

// Rotate helpers.
function ror64(x : bits(64), sh : int) -> bits(64) = {
  let s = tmod_int(sh, 64);
  if s == 0 then x
  else sail_shiftright(x, s) | sail_shiftleft(x, 64 - s)
}

function rol64(x : bits(64), sh : int) -> bits(64) = {
  let s = tmod_int(sh, 64);
  if s == 0 then x
  else sail_shiftleft(x, s) | sail_shiftright(x, 64 - s)
}

function ror32(x : bits(32), sh : int) -> bits(32) = {
  let s = tmod_int(sh, 32);
  if s == 0 then x
  else sail_shiftright(x, s) | sail_shiftleft(x, 32 - s)
}

function rol32(x : bits(32), sh : int) -> bits(32) = {
  let s = tmod_int(sh, 32);
  if s == 0 then x
  else sail_shiftleft(x, s) | sail_shiftright(x, 32 - s)
}

function mask_low_n(n : int) -> bits(64) = {
  if n >= 64 then 0xFFFF_FFFF_FFFF_FFFF
  else {
    var m : bits(64) = 0x0000_0000_0000_0000;
    var i : int = 0;
    while i < n do {
      m = m | sail_shiftleft(0x0000_0000_0000_0001, i);
      i = i + 1
    };
    m
  }
}

function mask_low_n32(n : int) -> bits(32) = {
  if n >= 32 then 0xFFFF_FFFF
  else {
    var m : bits(32) = 0x0000_0000;
    var i : int = 0;
    while i < n do {
      m = m | sail_shiftleft(0x0000_0001, i);
      i = i + 1
    };
    m
  }
}

function bitfield_wrap(x : bits(64), M : int, N : int) -> bits(64) = {
  // Return field bits in low N bits, with wrap-around on the 64-bit ring.
  let r = ror64(x, M);
  r & mask_low_n(N)
}

function bitfield_wrap32(x : bits(32), M : int, N : int) -> bits(32) = {
  let r = ror32(x, M);
  r & mask_low_n32(N)
}

function sext_low_n(field : bits(64), N : int) -> bits(64) = {
  if N <= 0 then field
  else if N >= 64 then field
  else {
    assert((0 < N) & (N < 64));
    let sign = sail_shiftright(field, N - 1)[0];
    let masked = mask_low_n(N);
    if sign == 0b1 then (field | not_vec(masked)) else field
  }
}

function clz_low_n(field : bits(64), N : int) -> int = {
  // Count leading zeros in an N-bit value encoded in low N bits.
  if N <= 0 then 0
  else {
    let n = if N >= 64 then 64 else N;
    var c : int = 0;
    var seen_one : bool = false;
    foreach (j from 0 to 63) {
      let idx : int = 63 - j;
      if (j >= 64 - n) & not_bool(seen_one) then {
        assert((0 <= idx) & (idx < 64));
        if bitvector_access(field, idx) == 0b1 then seen_one = true else c = c + 1
      } else ()
    };
    c
  }
}

function ctz_low_n(field : bits(64), N : int) -> int = {
  if N <= 0 then 0
  else {
    let n = if N >= 64 then 64 else N;
    var c : int = 0;
    var seen_one : bool = false;
    foreach (i from 0 to 63) {
      if (i < n) & not_bool(seen_one) then {
        assert((0 <= i) & (i < 64));
        if bitvector_access(field, i) == 0b1 then seen_one = true else c = c + 1
      } else ()
    };
    c
  }
}

function popcount_low_n(field : bits(64), N : int) -> int = {
  if N <= 0 then 0
  else {
    let n = if N >= 64 then 64 else N;
    var c : int = 0;
    foreach (i from 0 to 63) {
      if i < n then {
        assert((0 <= i) & (i < 64));
        if bitvector_access(field, i) == 0b1 then c = c + 1 else ()
      } else ()
    };
    c
  }
}

function rev_bytes_low_n(field : bits(64), N : int) -> bits(64) = {
  // Reverse byte order of low N bits. Requires N multiple of 8.
  let nb : int = tdiv_int(N, 8);
  var out : bits(64) = 0x0000_0000_0000_0000;
  var i : int = 0;
  while i < nb do {
    let b : bits(8) = sail_shiftright(field, 8 * i)[7..0];
    let shift : int = 8 * (nb - 1 - i);
    out = out | sail_shiftleft(zext8_from8(b), shift);
    i = i + 1
  };
  out
}

// Arithmetic shift right helpers.
function ashr64(x : bits(64), sh : int) -> bits(64) = {
  if sh == 0 then x
  else {
    let fill = if x[63] == 0b1 then 0xFFFF_FFFF_FFFF_FFFF else 0x0000_0000_0000_0000;
    sail_shiftright(x, sh) | sail_shiftleft(fill, 64 - sh)
  }
}

function ashr32(w : bits(32), sh : int) -> bits(32) = {
  if sh == 0 then w
  else {
    let fill32 = if w[31] == 0b1 then 0xFFFF_FFFF else 0x0000_0000;
    sail_shiftright(w, sh) | sail_shiftleft(fill32, 32 - sh)
  }
}

// ClockHands queues: depth-4 shift register (t#1..t#4, u#1..u#4).
// In the current v0.56 bring-up profile, queues are block-local architectural state.

// Architectural state accessors are defined in state.sail.

// SrcRType mapping (2-bit).
// 00: none
// 01: .sw (sext32)
// 10: .uw (zext32)
// 11: .neg (arithmetic) OR .not (logical)

type srcrtype = bits(2)

function apply_srcrtype_arith64(t : srcrtype, x : bits(64)) -> bits(64) = {
  match t {
    0b00 => x,
    0b01 => sext32(x),
    0b10 => zext32(x),
    0b11 => sub_bits(sail_zeros(64), x)
  }
}

function apply_srcrtype_logic64(t : srcrtype, x : bits(64)) -> bits(64) = {
  match t {
    0b00 => x,
    0b01 => sext32(x),
    0b10 => zext32(x),
    0b11 => not_vec(x)
  }
}

function apply_srcrtype_arith32(t : srcrtype, x : bits(64)) -> bits(32) = {
  let w = x[31..0];
  match t {
    0b00 => w,
    0b01 => w, // already 32-bit; "sw" affects 64-bit view only
    0b10 => w,
    0b11 => sub_bits(sail_zeros(32), w)
  }
}

function apply_srcrtype_logic32(t : srcrtype, x : bits(64)) -> bits(32) = {
  let w = x[31..0];
  match t {
    0b00 => w,
    0b01 => w,
    0b10 => w,
    0b11 => not_vec(w)
  }
}

// Load/store extension helpers.
function sext8_from8(b : bits(8)) -> bits(64) = {
  if b[7] == 0b1 then sail_ones(56) @ b else sail_zeros(56) @ b
}

function zext16_from16(h : bits(16)) -> bits(64) = {
  sail_zeros(48) @ h
}

function sext16_from16(h : bits(16)) -> bits(64) = {
  if h[15] == 0b1 then sail_ones(48) @ h else sail_zeros(48) @ h
}
