// LinxISA Sail common helpers (bring-up; v0.3).

// IMPORTANT POLICY:
// - Missing semantics MUST be explicit (no guessed behavior).
// - `unimplemented("MNEMONIC")` should be used until behavior is confirmed.

function unimplemented(mnemonic : string) -> unit = {
  // Placeholder: in the final model this should raise a defined exception.
  ()
}

// Basic bit utilities.
function zext32(x : bits(64)) -> bits(64) = {
  0x00000000_00000000 | (x[31..0])
}

function sext32(x : bits(64)) -> bits(64) = {
  let w = x[31..0];
  // Sign-extend from bit 31.
  if w[31] == 1b1 then (0xFFFF_FFFF_0000_0000 | w) else (0x0000_0000_0000_0000 | w)
}

function zext32_from32(w : bits(32)) -> bits(64) = {
  0x0000_0000_0000_0000 | w
}

function zext8_from8(b : bits(8)) -> bits(64) = {
  0x0000_0000_0000_0000 | b
}

function sext32_from32(w : bits(32)) -> bits(64) = {
  if w[31] == 1b1 then (0xFFFF_FFFF_0000_0000 | w) else (0x0000_0000_0000_0000 | w)
}

function zext12_to64(imm12 : bits(12)) -> bits(64) = {
  0x0000_0000_0000_0000 | imm12
}

function sext12_to64(imm12 : bits(12)) -> bits(64) = {
  if imm12[11] == 1b1 then (0xFFFF_FFFF_FFFF_F000 | imm12) else (0x0000_0000_0000_0000 | imm12)
}

function zext24_to64(imm24 : bits(24)) -> bits(64) = {
  0x0000_0000_0000_0000 | imm24
}

function sext24_to64(imm24 : bits(24)) -> bits(64) = {
  if imm24[23] == 1b1 then (0xFFFF_FFFF_FF00_0000 | imm24) else (0x0000_0000_0000_0000 | imm24)
}

function sext22_to64(imm22 : bits(22)) -> bits(64) = {
  if imm22[21] == 1b1 then (0xFFFF_FFFF_FFF0_0000 | imm22) else (0x0000_0000_0000_0000 | imm22)
}

function zext20_to64(imm20 : bits(20)) -> bits(64) = {
  0x0000_0000_0000_0000 | imm20
}

function sext20_to64(imm20 : bits(20)) -> bits(64) = {
  if imm20[19] == 1b1 then (0xFFFF_FFFF_FFF0_0000 | imm20) else (0x0000_0000_0000_0000 | imm20)
}

function sext17_to64(imm17 : bits(17)) -> bits(64) = {
  if imm17[16] == 1b1 then (0xFFFF_FFFF_FFFF_0000 | imm17) else (0x0000_0000_0000_0000 | imm17)
}

function mask_shamt64(x : bits(64)) -> bits(6) = {
  x[5..0]
}

function mask_shamt32(x : bits(64)) -> bits(5) = {
  x[4..0]
}

// Rotate helpers.
function ror64(x : bits(64), sh : int) -> bits(64) = {
  let s = sh % 64;
  if s == 0 then x
  else (x >> s) | (x << (64 - s))
}

function rol64(x : bits(64), sh : int) -> bits(64) = {
  let s = sh % 64;
  if s == 0 then x
  else (x << s) | (x >> (64 - s))
}

function mask_low_n(n : int) -> bits(64) = {
  if n >= 64 then 0xFFFF_FFFF_FFFF_FFFF
  else {
    var m : bits(64) = 0x0000_0000_0000_0000;
    var i : int = 0;
    while i < n do {
      m = m | (0x0000_0000_0000_0001 << i);
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

function sext_low_n(field : bits(64), N : int) -> bits(64) = {
  if N >= 64 then field
  else {
    let sign = field[N - 1];
    if sign == 1b1 then (field | (~mask_low_n(N))) else field
  }
}

function clz_low_n(field : bits(64), N : int) -> int = {
  // Count leading zeros in an N-bit value encoded in low N bits.
  var c : int = 0;
  var i : int = N - 1;
  while i >= 0 do {
    if field[i] == 1b1 then i = -1
    else {
      c = c + 1;
      i = i - 1
    }
  };
  c
}

function ctz_low_n(field : bits(64), N : int) -> int = {
  var c : int = 0;
  var i : int = 0;
  while i < N do {
    if field[i] == 1b1 then i = N
    else {
      c = c + 1;
      i = i + 1
    }
  };
  c
}

function popcount_low_n(field : bits(64), N : int) -> int = {
  var c : int = 0;
  var i : int = 0;
  while i < N do {
    if field[i] == 1b1 then c = c + 1 else ();
    i = i + 1
  };
  c
}

function rev_bytes_low_n(field : bits(64), N : int) -> bits(64) = {
  // Reverse byte order of low N bits. Requires N multiple of 8.
  let nb : int = N / 8;
  var out : bits(64) = 0x0000_0000_0000_0000;
  var i : int = 0;
  while i < nb do {
    let b : bits(8) = field[(8*i + 7) .. (8*i)];
    let shift : int = 8 * (nb - 1 - i);
    out = out | (zext8_from8(b) << shift);
    i = i + 1
  };
  out
}

// Arithmetic shift right helpers.
function ashr64(x : bits(64), sh : int) -> bits(64) = {
  if sh == 0 then x
  else {
    let fill = if x[63] == 1b1 then 0xFFFF_FFFF_FFFF_FFFF else 0x0000_0000_0000_0000;
    (x >> sh) | (fill << (64 - sh))
  }
}

function ashr32(w : bits(32), sh : int) -> bits(32) = {
  if sh == 0 then w
  else {
    let fill32 = if w[31] == 1b1 then 0xFFFF_FFFF else 0x0000_0000;
    (w >> sh) | (fill32 << (32 - sh))
  }
}

// ClockHands queues: depth-4 shift register (t#1..t#4, u#1..u#4).
// In the v0.3 bring-up profile, queues are block-local architectural state.

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
    0b11 => (0x00000000_00000000 - x)
  }
}

function apply_srcrtype_logic64(t : srcrtype, x : bits(64)) -> bits(64) = {
  match t {
    0b00 => x,
    0b01 => sext32(x),
    0b10 => zext32(x),
    0b11 => ~x
  }
}

function apply_srcrtype_arith32(t : srcrtype, x : bits(64)) -> bits(32) = {
  let w = x[31..0];
  match t {
    0b00 => w,
    0b01 => w, // already 32-bit; "sw" affects 64-bit view only
    0b10 => w,
    0b11 => (0x00000000 - w)
  }
}

function apply_srcrtype_logic32(t : srcrtype, x : bits(64)) -> bits(32) = {
  let w = x[31..0];
  match t {
    0b00 => w,
    0b01 => w,
    0b10 => w,
    0b11 => ~w
  }
}
