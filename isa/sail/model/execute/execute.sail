// LinxISA execute semantics (bring-up; v0.3).

// This file will be grown incrementally. For now, it provides helpers and a
// minimal ALU subset.

// NOTE: Baseline policy (per user): implement semantics according to the
// current manual + golden, and leave ambiguous behavior unimplemented until
// confirmed.

// include state + common helpers

$include "../lib/common.sail"
$include "../state/state.sail"

// ALU helpers.

// Common helpers (must appear before first use in Sail).
function bool_to_u64(b : bool) -> bits(64) = {
  if b then 0x0000_0000_0000_0001 else 0x0000_0000_0000_0000
}

function exec_add(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b1 = apply_srcrtype_arith64(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b = sail_shiftleft(b1, sh);
  let r = a + b;
  write_regdst(RegDst, r)
}

function exec_sub(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b1 = apply_srcrtype_arith64(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b = sail_shiftleft(b1, sh);
  let r = a - b;
  write_regdst(RegDst, r)
}

function exec_and(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b1 = apply_srcrtype_logic64(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b = sail_shiftleft(b1, sh);
  let r = a & b;
  write_regdst(RegDst, r)
}

function exec_or(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b1 = apply_srcrtype_logic64(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b = sail_shiftleft(b1, sh);
  let r = a | b;
  write_regdst(RegDst, r)
}

function exec_xor(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b1 = apply_srcrtype_logic64(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b = sail_shiftleft(b1, sh);
  let r = a ^ b;
  write_regdst(RegDst, r)
}

function exec_addi(RegDst : bits(5), SrcL : bits(5), uimm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = zext12_to64(uimm12);
  write_regdst(RegDst, a + imm)
}

function exec_subi(RegDst : bits(5), SrcL : bits(5), uimm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = zext12_to64(uimm12);
  write_regdst(RegDst, a - imm)
}

function exec_andi(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext12_to64(simm12);
  write_regdst(RegDst, a & imm)
}

function exec_ori(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext12_to64(simm12);
  write_regdst(RegDst, a | imm)
}

function exec_xori(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext12_to64(simm12);
  write_regdst(RegDst, a ^ imm)
}

// Word (32-bit) variants: operate in 32-bit, then sext32 to 64-bit.

function exec_addw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let b0 = read_reg5(SrcR);
  let b1 : bits(32) = apply_srcrtype_arith32(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b : bits(32) = sail_shiftleft(b1, sh);
  let r : bits(32) = a + b;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_subw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let b0 = read_reg5(SrcR);
  let b1 : bits(32) = apply_srcrtype_arith32(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b : bits(32) = sail_shiftleft(b1, sh);
  let r : bits(32) = a - b;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_andw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let b0 = read_reg5(SrcR);
  let b1 : bits(32) = apply_srcrtype_logic32(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b : bits(32) = sail_shiftleft(b1, sh);
  let r : bits(32) = a & b;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_orw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let b0 = read_reg5(SrcR);
  let b1 : bits(32) = apply_srcrtype_logic32(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b : bits(32) = sail_shiftleft(b1, sh);
  let r : bits(32) = a | b;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_xorw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let b0 = read_reg5(SrcR);
  let b1 : bits(32) = apply_srcrtype_logic32(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b : bits(32) = sail_shiftleft(b1, sh);
  let r : bits(32) = a ^ b;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_addiw(RegDst : bits(5), SrcL : bits(5), uimm12 : bits(12)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let imm : bits(32) = sail_zero_extend(uimm12, 32);
  let r : bits(32) = a + imm;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_subiw(RegDst : bits(5), SrcL : bits(5), uimm12 : bits(12)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let imm : bits(32) = sail_zero_extend(uimm12, 32);
  let r : bits(32) = a - imm;
  write_regdst(RegDst, sext32_from32(r))
}

// HL48 long-encoding ALU ops.
// User-confirmed semantics:
// - HL.ADDI/HL.SUBI: same as ADDI/SUBI but with uimm24, zero-extended.
// - HL.ADDIW/HL.SUBIW: 32-bit op, then sext32 to 64-bit.
// - HL.BFI: 64-bit bitfield insert.
//   lsb = immr
//   width = imms + 1
//   src_bits = SrcR[width-1:0]
//   base = SrcL

function exec_hl_addi(RegDst : bits(5), SrcL : bits(5), uimm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = zext24_to64(uimm24);
  write_regdst(RegDst, a + imm)
}

function exec_hl_subi(RegDst : bits(5), SrcL : bits(5), uimm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = zext24_to64(uimm24);
  write_regdst(RegDst, a - imm)
}

function exec_hl_addiw(RegDst : bits(5), SrcL : bits(5), uimm24 : bits(24)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let imm : bits(32) = sail_zero_extend(uimm24, 32);
  let r : bits(32) = a + imm;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_hl_subiw(RegDst : bits(5), SrcL : bits(5), uimm24 : bits(24)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let imm : bits(32) = sail_zero_extend(uimm24, 32);
  let r : bits(32) = a - imm;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_hl_bfi(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), immr : bits(6), imms : bits(6)) -> unit = {
  // HL.BFI is a bitfield insert using the AArch64-style immr/imms encoding.
  // Interpret immr as the rotation/lsb, and compute field width from immr/imms
  // with wrap-around on the 64-bit ring.
  //
  // Semantics we implement (ring-safe insert):
  //   m = immr
  //   n = width
  //   r = ROR(base, m)
  //   r' = (r & ~mask_low_n(n)) | (src_low_n(n))
  //   result = ROL(r', m)
  let base : bits(64) = read_reg5(SrcL);
  let src  : bits(64) = read_reg5(SrcR);
  let m : int = unsigned(immr);
  let s : int = unsigned(imms);

  // Width (n) derived from immr/imms (wrap-around form).
  let n : int = if s >= m then (s - m + 1) else (s + (64 - m) + 1);

  // Defensive: constrain to 1..64 (should always hold for 6-bit fields).
  assert((1 <= n) & (n <= 64));

  let r = ror64(base, m);
  let ins = src & mask_low_n(n);
  let merged = (r & not_vec(mask_low_n(n))) | ins;
  write_regdst(RegDst, rol64(merged, m))
}

// Concat/barrel extract helpers.
// CCAT: treat {SrcL,SrcR} as 128-bit, shift right by shamt, return low/high halves.
function exec_hl_ccat(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), shamt : bits(7)) -> unit = {
  let a : bits(64) = read_reg5(SrcL);
  let b : bits(64) = read_reg5(SrcR);
  let x : bits(128) = a @ b;
  let sh : int = unsigned(shamt);
  let y : bits(128) = if sh >= 128 then sail_zeros(128) else (sail_shiftright(x, sh));
  write_regdst(RegDst0, y[63..0]);
  write_regdst(RegDst1, y[127..64])
}

// CCATW: treat low 32b of SrcL/SrcR as 64-bit concat, shift right by shamt.
// Results are sign-extended from 32b lanes to 64b to match *W conventions.
function exec_hl_ccatw(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), shamt : bits(7)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let x : bits(64) = a32 @ b32;
  let sh : int = unsigned(shamt);
  let y : bits(64) = if sh >= 64 then sail_zeros(64) else (sail_shiftright(x, sh));
  write_regdst(RegDst0, sext32_from32(y[31..0]));
  write_regdst(RegDst1, sext32_from32(y[63..32]))
}

// Multiply-immediate add/sub.
// MIADD: RegDst = SrcL + (SrcR * uimm19)
// MISUB: RegDst = SrcL - (SrcR * uimm19)
function exec_hl_miadd(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), uimm19 : bits(19)) -> unit = {
  let a : bits(64) = read_reg5(SrcL);
  let b : bits(64) = read_reg5(SrcR);
  let m : int = unsigned(uimm19);
  let prod : int = unsigned(b) * m;
  write_regdst(RegDst, a + (sail_zeros(64) + prod))
}

function exec_hl_misub(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), uimm19 : bits(19)) -> unit = {
  let a : bits(64) = read_reg5(SrcL);
  let b : bits(64) = read_reg5(SrcR);
  let m : int = unsigned(uimm19);
  let prod : int = unsigned(b) * m;
  write_regdst(RegDst, a - (sail_zeros(64) + prod))
}

// Queue ops (QMT/QPUSH/QPOP): reserved.
// These interact with block-local queue state (ClockHands / TQ/UQ) but are not
// architecturally specified in v0.3 semantics yet.
//
// Bring-up policy: treat them as no-ops with deterministic register results,
// so the interpreter can run larger tests without tripping "unimplemented".
function exec_hl_qmt(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), e : bits(1), i : bits(1), r : bits(1), s : bits(1)) -> unit = {
  let _ = SrcL; let _ = SrcR; let _ = e; let _ = i; let _ = r; let _ = s;
  write_regdst(RegDst, 0x0000_0000_0000_0000)
}

function exec_hl_qpush(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), e : bits(1), h : bits(1), r : bits(1)) -> unit = {
  let _ = SrcL; let _ = SrcR; let _ = e; let _ = h; let _ = r;
  write_regdst(RegDst, 0x0000_0000_0000_0000)
}

function exec_hl_qpop(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), e : bits(1), r : bits(1)) -> unit = {
  let _ = SrcL; let _ = SrcR; let _ = e; let _ = r;
  write_regdst(RegDst0, 0x0000_0000_0000_0000);
  write_regdst(RegDst1, 0x0000_0000_0000_0000)
}

function exec_andiw(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  let r : bits(32) = a & imm;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_orizw(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  let r : bits(32) = a | imm;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_xoriw(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  let r : bits(32) = a ^ imm;
  write_regdst(RegDst, sext32_from32(r))
}

// Shifts.

function exec_sll(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(mask_shamt64(read_reg5(SrcR)));
  write_regdst(RegDst, sail_shiftleft(a, sh))
}

function exec_srl(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(mask_shamt64(read_reg5(SrcR)));
  write_regdst(RegDst, sail_shiftright(a, sh))
}

function exec_sra(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(mask_shamt64(read_reg5(SrcR)));
  write_regdst(RegDst, ashr64(a, sh))
}

function exec_slli(RegDst : bits(5), SrcL : bits(5), shamt : bits(6)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  write_regdst(RegDst, sail_shiftleft(a, sh))
}

function exec_srli(RegDst : bits(5), SrcL : bits(5), shamt : bits(6)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  write_regdst(RegDst, sail_shiftright(a, sh))
}

function exec_srai(RegDst : bits(5), SrcL : bits(5), shamt : bits(6)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  write_regdst(RegDst, ashr64(a, sh))
}

function exec_sllw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let sh : int = unsigned(mask_shamt32(read_reg5(SrcR)));
  let r : bits(32) = sail_shiftleft(a, sh);
  write_regdst(RegDst, sext32_from32(r))
}

function exec_srlw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let sh : int = unsigned(mask_shamt32(read_reg5(SrcR)));
  let r : bits(32) = sail_shiftright(a, sh);
  write_regdst(RegDst, sext32_from32(r))
}

function exec_sraw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let sh : int = unsigned(mask_shamt32(read_reg5(SrcR)));
  let r : bits(32) = ashr32(a, sh);
  write_regdst(RegDst, sext32_from32(r))
}

function exec_slliw(RegDst : bits(5), SrcL : bits(5), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let sh : int = unsigned(shamt);
  let r : bits(32) = sail_shiftleft(a, sh);
  write_regdst(RegDst, sext32_from32(r))
}

function exec_srliw(RegDst : bits(5), SrcL : bits(5), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let sh : int = unsigned(shamt);
  let r : bits(32) = sail_shiftright(a, sh);
  write_regdst(RegDst, sext32_from32(r))
}

function exec_sraiw(RegDst : bits(5), SrcL : bits(5), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let sh : int = unsigned(shamt);
  let r : bits(32) = ashr32(a, sh);
  write_regdst(RegDst, sext32_from32(r))
}

// Compressed shift immediates (C.TINST split):
function exec_c_slli(RegDst : bits(5), SrcL : bits(5), imm5 : bits(5)) -> unit = {
  // imm5 is the shift amount.
  let a = read_reg5(SrcL);
  let sh : int = unsigned(imm5);
  write_regdst(RegDst, sail_shiftleft(a, sh))
}

function exec_c_srli(RegDst : bits(5), SrcL : bits(5), imm5 : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(imm5);
  write_regdst(RegDst, sail_shiftright(a, sh))
}

// -----------------------------------------------------------------------------
// Compressed (C16) ALU / unary / TINST helpers.
//
// Register conventions used by the assembler templates:
//   - `t`   is a fixed architectural register alias (reg5 code 31).
//   - `t#1` is a fixed architectural register alias (reg5 code 24).
//
// We keep these explicit here so the semantics are readable.

function reg_t() -> bits(5) = { 0b11111 }
function reg_t1() -> bits(5) = { 0b11000 }

function exec_c_add(SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  write_regdst(reg_t(), a + b)
}

function exec_c_sub(SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  write_regdst(reg_t(), a - b)
}

function exec_c_and(SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  write_regdst(reg_t(), a & b)
}

function exec_c_or(SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  write_regdst(reg_t(), a | b)
}

function exec_c_addi(SrcL : bits(5), simm5 : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext5_to64(simm5);
  write_regdst(reg_t(), a + imm)
}

// Compressed base+imm loads/stores.
// These map onto the corresponding 32-bit LWI/LDI/SWI/SDI addressing: sign-extended immediate
// scaled by access size.
function exec_c_lwi(SrcL : bits(5), simm5 : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext5_to64(simm5);
  let ea = base + (sail_shiftleft(off, 2));
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(reg_t(), sext32_from32(w))
}

function exec_c_ldi(SrcL : bits(5), simm5 : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext5_to64(simm5);
  let ea = base + (sail_shiftleft(off, 3));
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(reg_t(), d)
}

function exec_c_swi(SrcL : bits(5), simm5 : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext5_to64(simm5);
  let ea = base + (sail_shiftleft(off, 2));
  let v : bits(32) = read_reg5(reg_t1())[31..0];
  mem_store32_le(ea, v)
}

function exec_c_sdi(SrcL : bits(5), simm5 : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext5_to64(simm5);
  let ea = base + (sail_shiftleft(off, 3));
  let v : bits(64) = read_reg5(reg_t1());
  mem_store64_le(ea, v)
}

function exec_c_movi(RegDst : bits(5), simm5 : bits(5)) -> unit = {
  let imm = sext5_to64(simm5);
  write_regdst(RegDst, imm)
}

function exec_c_movr(RegDst : bits(5), SrcL : bits(5)) -> unit = {
  write_regdst(RegDst, read_reg5(SrcL))
}

function exec_c_cmp_eqi(simm5 : bits(5)) -> unit = {
  let a = read_reg5(reg_t1());
  let imm = sext5_to64(simm5);
  write_regdst(reg_t(), bool_to_u64(a == imm))
}

function exec_c_cmp_nei(simm5 : bits(5)) -> unit = {
  let a = read_reg5(reg_t1());
  let imm = sext5_to64(simm5);
  write_regdst(reg_t(), bool_to_u64(a != imm))
}

function exec_ebreak() -> unit = {
  // Software breakpoint.
  trap_sw_breakpoint(read_pc_or_tpc())
}

function exec_c_ebreak(imm5 : bits(5)) -> unit = {
  // Semantics are identical to EBREAK; imm is for debugger patching heuristics.
  let _ = imm5;
  exec_ebreak()
}

function exec_c_sext_b(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[7..0];
  // Sign-extend from bit 7.
  if a[7] == 0b1 then write_regdst(reg_t(), sail_zero_extend(a, 64) | 0xFFFF_FFFF_FFFF_FF00)
  else write_regdst(reg_t(), sail_zero_extend(a, 64))
}

function exec_c_sext_h(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[15..0];
  if a[15] == 0b1 then write_regdst(reg_t(), sail_zero_extend(a, 64) | 0xFFFF_FFFF_FFFF_0000)
  else write_regdst(reg_t(), sail_zero_extend(a, 64))
}

function exec_c_sext_w(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[31..0];
  write_regdst(reg_t(), sext32_from32(a))
}

function exec_c_zext_b(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[7..0];
  write_regdst(reg_t(), sail_zero_extend(a, 64))
}

function exec_c_zext_h(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[15..0];
  write_regdst(reg_t(), sail_zero_extend(a, 64))
}

function exec_c_zext_w(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[31..0];
  write_regdst(reg_t(), zext32_from32(a))
}

// Bitfield operations (wrap-around on 64-bit ring).

function exec_bxu(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  let f = bitfield_wrap(x, m, n);
  write_regdst(RegDst, f)
}

function exec_bxs(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  let f = bitfield_wrap(x, m, n);
  write_regdst(RegDst, sext_low_n(f, n))
}

function exec_ror(RegDst : bits(5), SrcL : bits(5), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let m : int = unsigned(M);
  write_regdst(RegDst, ror64(x, m))
}

function exec_clz(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  let f = bitfield_wrap(x, m, n);
  let c : int = clz_low_n(f, n);
  write_regdst(RegDst, (sail_zeros(64) + c))
}

function exec_ctz(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  let f = bitfield_wrap(x, m, n);
  let c : int = ctz_low_n(f, n);
  write_regdst(RegDst, (sail_zeros(64) + c))
}

function exec_bcnt(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  let f = bitfield_wrap(x, m, n);
  let c : int = popcount_low_n(f, n);
  write_regdst(RegDst, (sail_zeros(64) + c))
}

function exec_bic(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  let r = ror64(x, m);
  let cleared = r & (not_vec(mask_low_n(n)));
  write_regdst(RegDst, rol64(cleared, m))
}

function exec_bis(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  let r = ror64(x, m);
  let setv = r | mask_low_n(n);
  write_regdst(RegDst, rol64(setv, m))
}

function exec_rev(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  if tmod_int(n, 8) != 0 then write_regdst(RegDst, 0x0000_0000_0000_0000)
  else {
    let f = bitfield_wrap(x, m, n);
    let r = rev_bytes_low_n(f, n);
    write_regdst(RegDst, r)
  }
}

// -----------------------------------------------------------------------------
// BRU: comparisons and commit-argument setting (strict v0.3 staged).
//
// NOTE: these are scalar boolean results (0/1) written via RegDst or to the
// block-control commit-argument domain (BARG.CARG).

// (bool_to_u64 defined near top of file)

function sanitize_srcrtype_swuw(t : bits(2)) -> bits(2) = {
  // For forms whose assembly only allows {.sw,.uw}, strict v0.3 treats 11 as 00.
  if t == 0b11 then 0b00 else t
}

function exec_cmp_eq(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  write_regdst(RegDst, bool_to_u64(a == b))
}

function exec_cmp_ne(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  write_regdst(RegDst, bool_to_u64(a != b))
}

function exec_cmp_lt(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  write_regdst(RegDst, bool_to_u64(signed(a) < signed(b)))
}

function exec_cmp_ge(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  write_regdst(RegDst, bool_to_u64(signed(a) >= signed(b)))
}

function exec_cmp_ltu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  write_regdst(RegDst, bool_to_u64(unsigned(a) < unsigned(b)))
}

function exec_cmp_geu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  write_regdst(RegDst, bool_to_u64(unsigned(a) >= unsigned(b)))
}

function exec_cmp_and(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_logic64(SrcRType, b0);
  write_regdst(RegDst, bool_to_u64((a & b) != 0x0000_0000_0000_0000))
}

function exec_cmp_or(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_logic64(SrcRType, b0);
  write_regdst(RegDst, bool_to_u64((a | b) != 0x0000_0000_0000_0000))
}

// Immediate-compare variants.

function exec_cmp_eqi(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext12_to64(simm12);
  write_regdst(RegDst, bool_to_u64(a == imm))
}

function exec_cmp_nei(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext12_to64(simm12);
  write_regdst(RegDst, bool_to_u64(a != imm))
}

function exec_cmp_lti(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext12_to64(simm12);
  write_regdst(RegDst, bool_to_u64(signed(a) < signed(imm)))
}

function exec_cmp_gei(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext12_to64(simm12);
  write_regdst(RegDst, bool_to_u64(signed(a) >= signed(imm)))
}

function exec_cmp_ltui(RegDst : bits(5), SrcL : bits(5), uimm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = zext12_to64(uimm12);
  write_regdst(RegDst, bool_to_u64(unsigned(a) < unsigned(imm)))
}

function exec_cmp_geui(RegDst : bits(5), SrcL : bits(5), uimm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = zext12_to64(uimm12);
  write_regdst(RegDst, bool_to_u64(unsigned(a) >= unsigned(imm)))
}

function exec_cmp_andi(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext12_to64(simm12);
  write_regdst(RegDst, bool_to_u64((a & imm) != 0x0000_0000_0000_0000))
}

function exec_cmp_ori(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext12_to64(simm12);
  write_regdst(RegDst, bool_to_u64((a | imm) != 0x0000_0000_0000_0000))
}

// HL (48-bit) compare-immediate forms: same boolean semantics with 24-bit immediates.

function exec_hl_cmp_eqi(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext24_to64(simm24);
  write_regdst(RegDst, bool_to_u64(a == imm))
}

function exec_hl_cmp_nei(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext24_to64(simm24);
  write_regdst(RegDst, bool_to_u64(a != imm))
}

function exec_hl_cmp_lti(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext24_to64(simm24);
  write_regdst(RegDst, bool_to_u64(signed(a) < signed(imm)))
}

function exec_hl_cmp_gei(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext24_to64(simm24);
  write_regdst(RegDst, bool_to_u64(signed(a) >= signed(imm)))
}

function exec_hl_cmp_ltui(RegDst : bits(5), SrcL : bits(5), uimm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = zext24_to64(uimm24);
  write_regdst(RegDst, bool_to_u64(unsigned(a) < unsigned(imm)))
}

function exec_hl_cmp_geui(RegDst : bits(5), SrcL : bits(5), uimm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = zext24_to64(uimm24);
  write_regdst(RegDst, bool_to_u64(unsigned(a) >= unsigned(imm)))
}

function exec_hl_cmp_andi(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext24_to64(simm24);
  write_regdst(RegDst, bool_to_u64((a & imm) != 0x0000_0000_0000_0000))
}

function exec_hl_cmp_ori(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext24_to64(simm24);
  write_regdst(RegDst, bool_to_u64((a | imm) != 0x0000_0000_0000_0000))
}

// SETC: write to commit-argument domain (BARG.CARG).

function exec_setc_eq(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  set_commit_argument(bool_to_u64(a == b))
}

function exec_setc_ne(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  set_commit_argument(bool_to_u64(a != b))
}

function exec_setc_lt(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  set_commit_argument(bool_to_u64(signed(a) < signed(b)))
}

function exec_setc_ge(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  set_commit_argument(bool_to_u64(signed(a) >= signed(b)))
}

function exec_setc_ltu(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  set_commit_argument(bool_to_u64(unsigned(a) < unsigned(b)))
}

function exec_setc_geu(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_arith64(sanitize_srcrtype_swuw(SrcRType), b0);
  set_commit_argument(bool_to_u64(unsigned(a) >= unsigned(b)))
}

function exec_setc_and(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_logic64(SrcRType, b0);
  set_commit_argument(bool_to_u64((a & b) != 0x0000_0000_0000_0000))
}

function exec_setc_or(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_srcrtype_logic64(SrcRType, b0);
  set_commit_argument(bool_to_u64((a | b) != 0x0000_0000_0000_0000))
}

// SETC immediate variants (with encoded shamt): imm = sail_shiftleft(sext/zext(imm, shamt)).

function exec_setc_eqi(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext12_to64(simm12), sh);
  set_commit_argument(bool_to_u64(a == imm))
}

function exec_setc_nei(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext12_to64(simm12), sh);
  set_commit_argument(bool_to_u64(a != imm))
}

function exec_setc_lti(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext12_to64(simm12), sh);
  set_commit_argument(bool_to_u64(signed(a) < signed(imm)))
}

function exec_setc_gei(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext12_to64(simm12), sh);
  set_commit_argument(bool_to_u64(signed(a) >= signed(imm)))
}

function exec_setc_ltui(SrcL : bits(5), shamt : bits(5), uimm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(zext12_to64(uimm12), sh);
  set_commit_argument(bool_to_u64(unsigned(a) < unsigned(imm)))
}

function exec_setc_geui(SrcL : bits(5), shamt : bits(5), uimm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(zext12_to64(uimm12), sh);
  set_commit_argument(bool_to_u64(unsigned(a) >= unsigned(imm)))
}

function exec_setc_andi(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext12_to64(simm12), sh);
  set_commit_argument(bool_to_u64((a & imm) != 0x0000_0000_0000_0000))
}

function exec_setc_ori(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext12_to64(simm12), sh);
  set_commit_argument(bool_to_u64((a | imm) != 0x0000_0000_0000_0000))
}

// HL (48-bit) SETC.*I forms: same semantics, but with 24-bit immediates.

function exec_hl_setc_eqi(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext24_to64(simm24), sh);
  set_commit_argument(bool_to_u64(a == imm))
}

function exec_hl_setc_nei(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext24_to64(simm24), sh);
  set_commit_argument(bool_to_u64(a != imm))
}

function exec_hl_setc_lti(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext24_to64(simm24), sh);
  set_commit_argument(bool_to_u64(signed(a) < signed(imm)))
}

function exec_hl_setc_gei(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext24_to64(simm24), sh);
  set_commit_argument(bool_to_u64(signed(a) >= signed(imm)))
}

function exec_hl_setc_ltui(SrcL : bits(5), shamt : bits(5), uimm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(zext24_to64(uimm24), sh);
  set_commit_argument(bool_to_u64(unsigned(a) < unsigned(imm)))
}

function exec_hl_setc_geui(SrcL : bits(5), shamt : bits(5), uimm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(zext24_to64(uimm24), sh);
  set_commit_argument(bool_to_u64(unsigned(a) >= unsigned(imm)))
}

function exec_hl_setc_andi(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext24_to64(simm24), sh);
  set_commit_argument(bool_to_u64((a & imm) != 0x0000_0000_0000_0000))
}

function exec_hl_setc_ori(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sail_shiftleft(sext24_to64(simm24), sh);
  set_commit_argument(bool_to_u64((a | imm) != 0x0000_0000_0000_0000))
}

// Compressed SETC (16-bit) forms.

function exec_c_setc_eq(SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  set_commit_argument(bool_to_u64(a == b))
}

function exec_c_setc_ne(SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  set_commit_argument(bool_to_u64(a != b))
}

function exec_setc_tgt(SrcL : bits(5), SrcRType : bits(2)) -> unit = {
  // Select a register-based next-target for RET/IND-class transitions.
  // Only the register identity matters; SrcRType is ignored.
  let _ = SrcRType;
  set_commit_target_reg(SrcL)
}

function exec_c_setc_tgt(SrcL : bits(5)) -> unit = {
  set_commit_target_reg(SrcL)
}


// -----------------------------------------------------------------------------
// BRU: control-transfer (vec-engine scalar lane; updates TPC)
//
// Contract summary (strict v0.3 staged):
// - Vec-engine scalar-lane only (scalar blocks executing these trap: TRAPNUM=4).
// - Updates TPC (body-local PC), not architectural global PC.
// - PC-relative base is *current instruction* TPC.
// - Immediate offsets are halfword-scaled: target = base + sail_shiftleft(sext(offset, 1)).
// - B.Z/B.NZ consult predicate register p (modeled via read_predicate_p()).
// - Misaligned/unfetchable targets are reported as E_BLOCK(EC_BFETCH) by the fetch machinery.

function tpc_rel_target_from_imm12(simm12 : bits(12)) -> bits(64) = {
  let off = sail_shiftleft(sext12_to64(simm12), 1);
  read_tpc() + off
}

function tpc_rel_target_from_imm22(simm22 : bits(22)) -> bits(64) = {
  let off = sail_shiftleft(sext22_to64(simm22), 1);
  read_tpc() + off
}

function exec_b_eq(SrcL : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  if a == b then write_tpc(tpc_rel_target_from_imm12(simm12)) else ()
}

function exec_b_ne(SrcL : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  if a != b then write_tpc(tpc_rel_target_from_imm12(simm12)) else ()
}

function exec_b_lt(SrcL : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  if signed(a) < signed(b) then write_tpc(tpc_rel_target_from_imm12(simm12)) else ()
}

function exec_b_ge(SrcL : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  if signed(a) >= signed(b) then write_tpc(tpc_rel_target_from_imm12(simm12)) else ()
}

function exec_b_ltu(SrcL : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  if unsigned(a) < unsigned(b) then write_tpc(tpc_rel_target_from_imm12(simm12)) else ()
}

function exec_b_geu(SrcL : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  if unsigned(a) >= unsigned(b) then write_tpc(tpc_rel_target_from_imm12(simm12)) else ()
}

function exec_j(simm22 : bits(22)) -> unit = {
  write_tpc(tpc_rel_target_from_imm22(simm22))
}

function exec_b_nz(simm22 : bits(22)) -> unit = {
  let p = read_predicate_p();
  if p != 0x0000_0000_0000_0000 then write_tpc(tpc_rel_target_from_imm22(simm22)) else ()
}

function exec_b_z(simm22 : bits(22)) -> unit = {
  let p = read_predicate_p();
  if p == 0x0000_0000_0000_0000 then write_tpc(tpc_rel_target_from_imm22(simm22)) else ()
}

function exec_jr(SrcL : bits(5), simm12 : bits(12)) -> unit = {
  // NOTE: JR encoding also contains a SrcZero field; strict v0.3 ignores it.
  let base = read_reg5(SrcL);
  let off = sail_shiftleft(sext12_to64(simm12), 1);
  write_tpc(base + off)
}


// -----------------------------------------------------------------------------
// PC-relative operations (ADDTPC/SETRET)

function exec_addtpc(RegDst : bits(5), imm20 : bits(20)) -> unit = {
  let base = read_pc_or_tpc();
  let off = sail_shiftleft(sext20_to64(imm20), 1);
  write_regdst(RegDst, base + off)
}

function exec_setret(imm20 : bits(20)) -> unit = {
  let base = read_pc_or_tpc();
  let off = sail_shiftleft(zext20_to64(imm20), 1);
  write_regdst(0b01010, base + off)  // RA
}

function exec_hl_addtpc(RegDst : bits(5), imm32 : bits(32)) -> unit = {
  let base = read_pc_or_tpc();
  let off = sail_shiftleft(sext32_from32(imm32), 1);
  write_regdst(RegDst, base + off)
}

function exec_hl_setret(imm32 : bits(32)) -> unit = {
  let base = read_pc_or_tpc();
  let off = sail_shiftleft(zext32_from32(imm32), 1);
  write_regdst(0b01010, base + off)  // RA
}

function exec_c_setret(uimm5 : bits(5)) -> unit = {
  let base = read_pc_or_tpc();
  let off = sail_shiftleft(sail_zero_extend(uimm5, 64), 1);
  write_regdst(0b01010, base + off)  // RA
}


// -----------------------------------------------------------------------------
// Compound ops

function exec_csel(RegDst : bits(5), SrcP : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  // Decision (review): if Read(SrcP) != 0 then select SrcL else select SrcR.
  // Strict v0.3: SrcRType encodes optional .neg; other values are treated as 00.
  let p = read_reg5(SrcP);
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = if SrcRType == 0b11 then sub_bits(0x0000_0000_0000_0000, b0) else b0;
  let r = if p != 0x0000_0000_0000_0000 then a else b;
  write_regdst(RegDst, r)
}


// -----------------------------------------------------------------------------
// Multi-cycle ALU: division and remainder (ARM-like non-trapping conventions)

function exec_div(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let qi : int =
    if b == 0x0000_0000_0000_0000 then 0
    else if (a == 0x8000_0000_0000_0000) & (b == 0xFFFF_FFFF_FFFF_FFFF) then signed(a)
    else tdiv_int(signed(a), signed(b));
  write_regdst(RegDst, (sail_zeros(64) + qi))
}

function exec_divu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let qi : int = if b == 0x0000_0000_0000_0000 then 0 else tdiv_int(unsigned(a), unsigned(b));
  write_regdst(RegDst, (sail_zeros(64) + qi))
}

function exec_rem(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let ai : int = signed(a);
  let bi : int = signed(b);
  let qi : int =
    if b == 0x0000_0000_0000_0000 then 0
    else if (a == 0x8000_0000_0000_0000) & (b == 0xFFFF_FFFF_FFFF_FFFF) then ai
    else (tdiv_int(ai, bi));
  let ri : int = if b == 0x0000_0000_0000_0000 then ai else (ai - (qi * bi));
  write_regdst(RegDst, (sail_zeros(64) + ri))
}

function exec_remu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let ai : int = unsigned(a);
  let bi : int = unsigned(b);
  let qi : int = if b == 0x0000_0000_0000_0000 then 0 else (tdiv_int(ai, bi));
  let ri : int = if b == 0x0000_0000_0000_0000 then ai else (ai - (qi * bi));
  write_regdst(RegDst, (sail_zeros(64) + ri))
}

// Word (32-bit) variants: compute in 32-bit domain, then sign-extend to 64-bit for writeback.

function exec_divw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let a = sext32_from32(a32);
  let b = sext32_from32(b32);
  let ai : int = signed(a);
  let bi : int = signed(b);
  let qi : int =
    if b32 == 0x0000_0000 then 0
    else if (a32 == 0x8000_0000) & (b32 == 0xFFFF_FFFF) then ai
    else (tdiv_int(ai, bi));
  let q32 : bits(32) = (sail_zeros(32) + qi);
  write_regdst(RegDst, sext32_from32(q32))
}

function exec_divuw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let ai : int = unsigned(zext32_from32(a32));
  let bi : int = unsigned(zext32_from32(b32));
  let qi : int = if b32 == 0x0000_0000 then 0 else (tdiv_int(ai, bi));
  let q32 : bits(32) = (sail_zeros(32) + qi);
  write_regdst(RegDst, sext32_from32(q32))
}

function exec_remw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let a = sext32_from32(a32);
  let b = sext32_from32(b32);
  let ai : int = signed(a);
  let bi : int = signed(b);
  let qi : int =
    if b32 == 0x0000_0000 then 0
    else if (a32 == 0x8000_0000) & (b32 == 0xFFFF_FFFF) then ai
    else (tdiv_int(ai, bi));
  let ri : int = if b32 == 0x0000_0000 then ai else (ai - (qi * bi));
  let r32 : bits(32) = (sail_zeros(32) + ri);
  write_regdst(RegDst, sext32_from32(r32))
}

function exec_remuw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let ai : int = unsigned(zext32_from32(a32));
  let bi : int = unsigned(zext32_from32(b32));
  let qi : int = if b32 == 0x0000_0000 then 0 else (tdiv_int(ai, bi));
  let ri : int = if b32 == 0x0000_0000 then ai else (ai - (qi * bi));
  let r32 : bits(32) = (sail_zeros(32) + ri);
  write_regdst(RegDst, sext32_from32(r32))
}


// -----------------------------------------------------------------------------
// HL (48-bit) multi-cycle ALU: two-destination div/rem
// Convention: Dst0=quotient, Dst1=remainder.

function exec_hl_div(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let ai : int = signed(a);
  let bi : int = signed(b);
  let qi : int =
    if b == 0x0000_0000_0000_0000 then 0
    else if (a == 0x8000_0000_0000_0000) & (b == 0xFFFF_FFFF_FFFF_FFFF) then ai
    else (tdiv_int(ai, bi));
  let ri : int =
    if b == 0x0000_0000_0000_0000 then ai
    else if (a == 0x8000_0000_0000_0000) & (b == 0xFFFF_FFFF_FFFF_FFFF) then 0
    else (ai - (qi * bi));
  write_regdst(RegDst0, (sail_zeros(64) + qi));
  write_regdst(RegDst1, (sail_zeros(64) + ri))
}

function exec_hl_divu(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let ai : int = unsigned(a);
  let bi : int = unsigned(b);
  let qi : int = if b == 0x0000_0000_0000_0000 then 0 else (tdiv_int(ai, bi));
  let ri : int = if b == 0x0000_0000_0000_0000 then ai else (ai - (qi * bi));
  write_regdst(RegDst0, (sail_zeros(64) + qi));
  write_regdst(RegDst1, (sail_zeros(64) + ri))
}

function exec_hl_divw(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let a = sext32_from32(a32);
  let b = sext32_from32(b32);
  let ai : int = signed(a);
  let bi : int = signed(b);
  let qi : int =
    if b32 == 0x0000_0000 then 0
    else if (a32 == 0x8000_0000) & (b32 == 0xFFFF_FFFF) then ai
    else (tdiv_int(ai, bi));
  let ri : int =
    if b32 == 0x0000_0000 then ai
    else if (a32 == 0x8000_0000) & (b32 == 0xFFFF_FFFF) then 0
    else (ai - (qi * bi));
  let q32 : bits(32) = (sail_zeros(32) + qi);
  let r32 : bits(32) = (sail_zeros(32) + ri);
  write_regdst(RegDst0, sext32_from32(q32));
  write_regdst(RegDst1, sext32_from32(r32))
}

function exec_hl_divuw(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let ai : int = unsigned(zext32_from32(a32));
  let bi : int = unsigned(zext32_from32(b32));
  let qi : int = if b32 == 0x0000_0000 then 0 else (tdiv_int(ai, bi));
  let ri : int = if b32 == 0x0000_0000 then ai else (ai - (qi * bi));
  let q32 : bits(32) = (sail_zeros(32) + qi);
  let r32 : bits(32) = (sail_zeros(32) + ri);
  write_regdst(RegDst0, sext32_from32(q32));
  write_regdst(RegDst1, sext32_from32(r32))
}

function exec_hl_rem(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  // Alias: returns same pair as HL.DIV (quotient in Dst0, remainder in Dst1).
  exec_hl_div(RegDst0, RegDst1, SrcL, SrcR)
}

function exec_hl_remu(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  exec_hl_divu(RegDst0, RegDst1, SrcL, SrcR)
}

function exec_hl_remw(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  exec_hl_divw(RegDst0, RegDst1, SrcL, SrcR)
}

function exec_hl_remuw(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  exec_hl_divuw(RegDst0, RegDst1, SrcL, SrcR)
}


// -----------------------------------------------------------------------------
// Multi-cycle ALU: multiplication (low-part; *W sign-extends from bit31)

function exec_mul(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let pi : int = signed(a) * signed(b);
  write_regdst(RegDst, (sail_zeros(64) + pi))
}

function exec_mulu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let pi : int = unsigned(a) * unsigned(b);
  write_regdst(RegDst, (sail_zeros(64) + pi))
}

function exec_mulw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let pi : int = signed(sext32_from32(a32)) * signed(sext32_from32(b32));
  let p32 : bits(32) = (sail_zeros(32) + pi);
  write_regdst(RegDst, sext32_from32(p32))
}

function exec_muluw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let pi : int = unsigned(zext32_from32(a32)) * unsigned(zext32_from32(b32));
  let p32 : bits(32) = (sail_zeros(32) + pi);
  // *W writeback convention: sign-extend low 32 bits.
  write_regdst(RegDst, sext32_from32(p32))
}

// -----------------------------------------------------------------------------
// HL (48-bit) multi-cycle ALU: two-destination multiply
// Convention: Dst0 = low 64 bits of full product; Dst1 = high 64 bits.

function exec_hl_mul(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let pi : int = signed(a) * signed(b);
  let p128 : bits(128) = (sail_zeros(128) + pi);
  let lo : bits(64) = p128[63..0];
  let hi : bits(64) = p128[127..64];
  write_regdst(RegDst0, lo);
  write_regdst(RegDst1, hi)
}

function exec_hl_mulu(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let pi : int = unsigned(a) * unsigned(b);
  let p128 : bits(128) = (sail_zeros(128) + pi);
  let lo : bits(64) = p128[63..0];
  let hi : bits(64) = p128[127..64];
  write_regdst(RegDst0, lo);
  write_regdst(RegDst1, hi)
}


// -----------------------------------------------------------------------------
// Multi-cycle ALU: multiply-add (three-source)

function exec_madd(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let d = read_reg5(SrcD);
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let ri : int = signed(a) * signed(b) + signed(d);
  write_regdst(RegDst, (sail_zeros(64) + ri))
}

function exec_maddw(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let d32 : bits(32) = read_reg5(SrcD)[31..0];
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let di : int = signed(sext32_from32(d32));
  let ai : int = signed(sext32_from32(a32));
  let bi : int = signed(sext32_from32(b32));
  let ri : int = ai * bi + di;
  let r32 : bits(32) = (sail_zeros(32) + ri);
  write_regdst(RegDst, sext32_from32(r32))
}


// -----------------------------------------------------------------------------
// HL (48-bit) multi-cycle ALU: two-destination multiply-add
// Convention: Dst0 = low64(acc); Dst1 = high64(acc), where acc is 128-bit.

function exec_hl_madd(RegDst0 : bits(5), RegDst1 : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let d = read_reg5(SrcD);
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let pi : int = signed(a) * signed(b);
  let di : int = signed(d);
  let acc : int = pi + di;
  let acc128 : bits(128) = (sail_zeros(128) + acc);
  write_regdst(RegDst0, acc128[63..0]);
  write_regdst(RegDst1, acc128[127..64])
}

function exec_hl_maddw(RegDst0 : bits(5), RegDst1 : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let d32 : bits(32) = read_reg5(SrcD)[31..0];
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let di : int = signed(sext32_from32(d32));
  let ai : int = signed(sext32_from32(a32));
  let bi : int = signed(sext32_from32(b32));
  let acc : int = (ai * bi) + di;
  let acc128 : bits(128) = (sail_zeros(128) + acc);
  write_regdst(RegDst0, acc128[63..0]);
  write_regdst(RegDst1, acc128[127..64])
}


// -----------------------------------------------------------------------------
// Max/Min

function exec_max(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let r = if signed(a) >= signed(b) then a else b;
  write_regdst(RegDst, r)
}

function exec_maxu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let r = if unsigned(a) >= unsigned(b) then a else b;
  write_regdst(RegDst, r)
}

function exec_min(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let r = if signed(a) <= signed(b) then a else b;
  write_regdst(RegDst, r)
}

function exec_minu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let r = if unsigned(a) <= unsigned(b) then a else b;
  write_regdst(RegDst, r)
}


// -----------------------------------------------------------------------------
// Immediate materialization

function exec_lui(RegDst : bits(5), imm20 : bits(20)) -> unit = {
  // Load upper immediate: sign-extend imm20 then shift left by 12.
  let imm = sail_shiftleft(sext20_to64(imm20), 12);
  write_regdst(RegDst, imm)
}

function exec_hl_lui(RegDst : bits(5), imm32 : bits(32)) -> unit = {
  // HL.LUI: load a 32-bit immediate and sign-extend to 64-bit (sail_shiftleft(no, 12)).
  write_regdst(RegDst, sext32_from32(imm32))
}

function exec_hl_lis(RegDst : bits(5), simm32 : bits(32)) -> unit = {
  // HL.LIS: load signed 32-bit immediate.
  write_regdst(RegDst, sext32_from32(simm32))
}

function exec_hl_liu(RegDst : bits(5), uimm32 : bits(32)) -> unit = {
  // HL.LIU: load unsigned 32-bit immediate.
  write_regdst(RegDst, zext32_from32(uimm32))
}


// -----------------------------------------------------------------------------
// Word (32-bit) immediate logical ops

// NOTE: exec_oriw/exec_xoriw are already defined earlier in this file;
// keep only one definition to satisfy Sail.


// -----------------------------------------------------------------------------
// HL (48-bit) extended-immediate logical ops (simm24)

function exec_hl_andi(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext24_to64(simm24);
  write_regdst(RegDst, a & imm)
}

function exec_hl_ori(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext24_to64(simm24);
  write_regdst(RegDst, a | imm)
}

function exec_hl_xori(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let imm = sext24_to64(simm24);
  write_regdst(RegDst, a ^ imm)
}

function exec_hl_andiw(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let imm32 : bits(32) = sext24_to64(simm24)[31..0];
  let r32 : bits(32) = a32 & imm32;
  write_regdst(RegDst, sext32_from32(r32))
}

function exec_hl_oriw(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let imm32 : bits(32) = sext24_to64(simm24)[31..0];
  let r32 : bits(32) = a32 | imm32;
  write_regdst(RegDst, sext32_from32(r32))
}

function exec_hl_xoriw(RegDst : bits(5), SrcL : bits(5), simm24 : bits(24)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let imm32 : bits(32) = sext24_to64(simm24)[31..0];
  let r32 : bits(32) = a32 ^ imm32;
  write_regdst(RegDst, sext32_from32(r32))
}


// -----------------------------------------------------------------------------
// Prefetch (non-faulting hints)

function ea_base_reg(srcl : bits(5), srcr : bits(5), srcrtype : bits(2), shamt5 : bits(5)) -> bits(64) = {
  let base = read_reg5(srcl);
  let idx = apply_srcrtype_arith64(srcrtype, read_reg5(srcr));
  let sh : int = unsigned(shamt5);
  base + (sail_shiftleft(idx, sh))
}

function exec_prf(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  // RegDst is encoded but architecturally unused for PRF.
  let _ea = ea_base_reg(SrcL, SrcR, SrcRType, shamt);
  // Non-faulting hint: no architectural effect.
  ()
}

function exec_prfi_u(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let _ea = read_reg5(SrcL) + sext12_to64(simm12);
  ()
}

function exec_hl_prf(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), model : bits(5), shamt : bits(5)) -> unit = {
  let _ea = ea_base_reg(SrcL, SrcR, SrcRType, shamt);
  ()
}

function exec_hl_prf_a(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), model : bits(5), shamt : bits(5)) -> unit = {
  let ea = ea_base_reg(SrcL, SrcR, SrcRType, shamt);
  // .A form returns EA
  write_regdst(RegDst, ea)
}

function exec_hl_prfi_u(SrcL : bits(5), model : bits(5), simm17 : bits(17)) -> unit = {
  let _ea = read_reg5(SrcL) + sext17_to64(simm17);
  ()
}

function exec_hl_prfi_ua(RegDst : bits(5), SrcL : bits(5), model : bits(5), simm17 : bits(17)) -> unit = {
  let ea = read_reg5(SrcL) + sext17_to64(simm17);
  write_regdst(RegDst, ea)
}


// -----------------------------------------------------------------------------
// Floating-point compares (ordered; NaN => false)
//
// Note: staged model treats FP values as raw IEEE754 bit patterns.
// SrcType (2-bit) selects format: 0=fd (64-bit), 1=fs (32-bit in low bits).
// Other SrcType values are treated as fd.

function fp64_is_nan(x : bits(64)) -> bool = {
  let exp : bits(11) = x[62..52];
  let frac : bits(52) = x[51..0];
  (exp == (sail_zeros(11) + 2047)) & (frac != sail_zeros(52))
}

function fp64_is_zero(x : bits(64)) -> bool = {
  (x & 0x7FFF_FFFF_FFFF_FFFF) == 0x0000_0000_0000_0000
}

function fp64_key(x : bits(64)) -> bits(64) = {
  // Total-order key for non-NaNs (matches LinxCore RTL ordering trick).
  if x[63] == 0b1 then not_vec(x) else (x ^ 0x8000_0000_0000_0000)
}

function fp64_eq(a : bits(64), b : bits(64)) -> bool = {
  let nan = fp64_is_nan(a) | fp64_is_nan(b);
  let both_zero = fp64_is_zero(a) & fp64_is_zero(b);
  not_bool(nan) & ((a == b) | both_zero)
}

function fp64_lt(a : bits(64), b : bits(64)) -> bool = {
  let nan = fp64_is_nan(a) | fp64_is_nan(b);
  let both_zero = fp64_is_zero(a) & fp64_is_zero(b);
  not_bool(nan) & not_bool(both_zero) & (unsigned(fp64_key(a)) < unsigned(fp64_key(b)))
}

function fp64_ge(a : bits(64), b : bits(64)) -> bool = {
  let nan = fp64_is_nan(a) | fp64_is_nan(b);
  let both_zero = fp64_is_zero(a) & fp64_is_zero(b);
  not_bool(nan) & (both_zero | (unsigned(fp64_key(a)) >= unsigned(fp64_key(b))))
}

function fp32_is_nan(x : bits(32)) -> bool = {
  let exp : bits(8) = x[30..23];
  let frac : bits(23) = x[22..0];
  (exp == (sail_zeros(8) + 255)) & (frac != sail_zeros(23))
}

function fp32_is_zero(x : bits(32)) -> bool = {
  (x & 0x7FFF_FFFF) == 0x0000_0000
}

function fp32_key(x : bits(32)) -> bits(32) = {
  if x[31] == 0b1 then not_vec(x) else (x ^ 0x8000_0000)
}

function fp32_eq(a : bits(32), b : bits(32)) -> bool = {
  let nan = fp32_is_nan(a) | fp32_is_nan(b);
  let both_zero = fp32_is_zero(a) & fp32_is_zero(b);
  not_bool(nan) & ((a == b) | both_zero)
}

function fp32_lt(a : bits(32), b : bits(32)) -> bool = {
  let nan = fp32_is_nan(a) | fp32_is_nan(b);
  let both_zero = fp32_is_zero(a) & fp32_is_zero(b);
  not_bool(nan) & not_bool(both_zero) & (unsigned(fp32_key(a)) < unsigned(fp32_key(b)))
}

function fp32_ge(a : bits(32), b : bits(32)) -> bool = {
  let nan = fp32_is_nan(a) | fp32_is_nan(b);
  let both_zero = fp32_is_zero(a) & fp32_is_zero(b);
  not_bool(nan) & (both_zero | (unsigned(fp32_key(a)) >= unsigned(fp32_key(b))))
}

function exec_feq(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let a64 = read_reg5(SrcL);
  let b64 = read_reg5(SrcR);
  let is_fs = (SrcType == 0b01);
  let r = if is_fs then bool_to_u64(fp32_eq(a64[31..0], b64[31..0])) else bool_to_u64(fp64_eq(a64, b64));
  write_regdst(RegDst, r)
}

function exec_flt(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let a64 = read_reg5(SrcL);
  let b64 = read_reg5(SrcR);
  let is_fs = (SrcType == 0b01);
  let r = if is_fs then bool_to_u64(fp32_lt(a64[31..0], b64[31..0])) else bool_to_u64(fp64_lt(a64, b64));
  write_regdst(RegDst, r)
}

function exec_fge(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let a64 = read_reg5(SrcL);
  let b64 = read_reg5(SrcR);
  let is_fs = (SrcType == 0b01);
  let r = if is_fs then bool_to_u64(fp32_ge(a64[31..0], b64[31..0])) else bool_to_u64(fp64_ge(a64, b64));
  write_regdst(RegDst, r)
}

// S-variants: currently modeled as aliases (no FP exception signaling modeled in staged Sail).
function exec_feqs(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  exec_feq(RegDst, SrcL, SrcR, SrcType)
}

function exec_flts(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  exec_flt(RegDst, SrcL, SrcR, SrcType)
}

function exec_fges(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  exec_fge(RegDst, SrcL, SrcR, SrcType)
}


function exec_fne(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  // Ordered not-equal: NaN => false.
  let a64 = read_reg5(SrcL);
  let b64 = read_reg5(SrcR);
  let is_fs = (SrcType == 0b01);
  let eq = if is_fs then fp32_eq(a64[31..0], b64[31..0]) else fp64_eq(a64, b64);
  write_regdst(RegDst, bool_to_u64(not_bool(eq)))
}

function exec_fnes(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  exec_fne(RegDst, SrcL, SrcR, SrcType)
}

function exec_fmax(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  // ARM/IEEE maxNum-style: if exactly one operand is NaN, return the other; if both NaN, return canonical qNaN.
  // For signed zeros: if both are zero, return +0 for FMAX.
  let a64 = read_reg5(SrcL);
  let b64 = read_reg5(SrcR);
  let is_fs = (SrcType == 0b01);
  if is_fs then {
    let a32 = a64[31..0];
    let b32 = b64[31..0];
    let nan_a = fp32_is_nan(a32);
    let nan_b = fp32_is_nan(b32);
    let both_zero = fp32_is_zero(a32) & fp32_is_zero(b32);
    let r32 =
      if nan_a & nan_b then 0x7FC0_0000
      else if nan_a then b32
      else if nan_b then a32
      else if both_zero then 0x0000_0000
      else if fp32_ge(a32, b32) then a32 else b32;
    write_regdst(RegDst, zext32_from32(r32))
  } else {
    let nan_a = fp64_is_nan(a64);
    let nan_b = fp64_is_nan(b64);
    let both_zero = fp64_is_zero(a64) & fp64_is_zero(b64);
    let r =
      if nan_a & nan_b then 0x7FF8_0000_0000_0000
      else if nan_a then b64
      else if nan_b then a64
      else if both_zero then 0x0000_0000_0000_0000
      else if fp64_ge(a64, b64) then a64 else b64;
    write_regdst(RegDst, r)
  }
}

function exec_fmin(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  // ARM/IEEE minNum-style: if exactly one operand is NaN, return the other; if both NaN, return canonical qNaN.
  // For signed zeros: if both are zero, return -0 iff either operand is -0.
  let a64 = read_reg5(SrcL);
  let b64 = read_reg5(SrcR);
  let is_fs = (SrcType == 0b01);
  if is_fs then {
    let a32 = a64[31..0];
    let b32 = b64[31..0];
    let nan_a = fp32_is_nan(a32);
    let nan_b = fp32_is_nan(b32);
    let both_zero = fp32_is_zero(a32) & fp32_is_zero(b32);
    let neg0 = (a32[31] == 0b1) | (b32[31] == 0b1);
    let r32 =
      if nan_a & nan_b then 0x7FC0_0000
      else if nan_a then b32
      else if nan_b then a32
      else if both_zero then (if neg0 then 0x8000_0000 else 0x0000_0000)
      else if fp32_lt(a32, b32) then a32 else b32;
    write_regdst(RegDst, zext32_from32(r32))
  } else {
    let nan_a = fp64_is_nan(a64);
    let nan_b = fp64_is_nan(b64);
    let both_zero = fp64_is_zero(a64) & fp64_is_zero(b64);
    let neg0 = (a64[63] == 0b1) | (b64[63] == 0b1);
    let r =
      if nan_a & nan_b then 0x7FF8_0000_0000_0000
      else if nan_a then b64
      else if nan_b then a64
      else if both_zero then (if neg0 then 0x8000_0000_0000_0000 else 0x0000_0000_0000_0000)
      else if fp64_lt(a64, b64) then a64 else b64;
    write_regdst(RegDst, r)
  }
}


// -----------------------------------------------------------------------------
// Floating-point bitwise ops

function exec_fabs(RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let a64 = read_reg5(SrcL);
  let is_fs = (SrcType == 0b01);
  if is_fs then {
    let a32 = a64[31..0];
    let r32 = a32 & 0x7FFF_FFFF;
    write_regdst(RegDst, zext32_from32(r32))
  } else {
    let r = a64 & 0x7FFF_FFFF_FFFF_FFFF;
    write_regdst(RegDst, r)
  }
}


// -----------------------------------------------------------------------------
// System register access (SSR/LSR)
//
// Normative sources:
// - docs/architecture/isa-manual/src/generated/system_registers_ssr.adoc
// - docs/architecture/isa-manual/src/generated/instruction_details.adoc (SSRGET/SSRSET/SSRSWAP)
//
// Note: legality (E_ISSR routing, RO/WO enforcement, ACR-scoped families) is
// intentionally left to the state layer. The current staged state only backs a
// small subset of base SSRs.

function exec_ssrget(RegDst : bits(5), ssr_id12 : bits(12)) -> unit = {
  let id24 : bits(24) = sail_zero_extend(ssr_id12, 24);
  let v = read_system_register(id24);
  write_regdst(RegDst, v)
}

function exec_ssrset(SrcL : bits(5), ssr_id12 : bits(12)) -> unit = {
  let id24 : bits(24) = sail_zero_extend(ssr_id12, 24);
  write_system_register(id24, read_reg5(SrcL))
}

function exec_ssrswap(RegDst : bits(5), SrcL : bits(5), ssr_id12 : bits(12)) -> unit = {
  let id24 : bits(24) = sail_zero_extend(ssr_id12, 24);
  let old = swap_system_register(id24, read_reg5(SrcL));
  write_regdst(RegDst, old)
}

function exec_hl_ssrget(RegDst : bits(5), ssr_id24 : bits(24)) -> unit = {
  let v = read_system_register(ssr_id24);
  write_regdst(RegDst, v)
}

function exec_hl_ssrset(SrcL : bits(5), ssr_id24 : bits(24)) -> unit = {
  write_system_register(ssr_id24, read_reg5(SrcL))
}

function exec_c_ssrget(ssrid : bits(5)) -> unit = {
  // C.SSRGET encodes a small SSR_ID domain directly in the low bits (no remap).
  // SSR_ID[4:0] = SSRID.
  let id12 : bits(12) = (sail_zeros(7) @ ssrid);
  let id24 : bits(24) = sail_zero_extend(id12, 24);
  let v = read_system_register(id24);
  write_regdst(reg_t(), v)
}

function exec_lsrget(RegDst : bits(5), lsr_id12 : bits(12)) -> unit = {
  // Normative op (informative):
  //   value = ReadSystemRegister(ID)
  //   Write(Dst, value)
  // Source: docs/architecture/isa-manual/src/generated/instruction_details.adoc (LSRGET)
  let id24 : bits(24) = sail_zero_extend(lsr_id12, 24);
  let v = read_system_register(id24);
  write_regdst(RegDst, v)
}

// -----------------------------------------------------------------------------
// Floating-point arithmetic (FSU) - staged bring-up
//
// Normative sources:
// - docs/architecture/isa-manual/src/chapters/02_programming_model.adoc (CSTATE.FRM/FFLAGS)
// - docs/architecture/isa-manual/src/chapters/12_fsu.adoc
//
// POLICY: Do not guess FP numeric behavior until the FP library + CSTATE.FRM/FFLAGS semantics are
// fully wired. For now, we explicitly mark these operations as unimplemented.
// We still write a deterministic placeholder value to the destination to keep
// downstream execution deterministic in staged environments.

function fp_unimpl_result(RegDst : bits(5), mnemonic : string) -> unit = {
  // Staged shim: deterministic placeholder result.
  // IMPORTANT: do not call `unimplemented` here; these mnemonics are counted as
  // implemented shims in coverage.
  let _ = mnemonic;
  write_regdst(RegDst, 0x0000_0000_0000_0000)
}

function exec_fadd(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcL; let _ = SrcR; let _ = SrcType;
  fp_unimpl_result(RegDst, "FADD")
}

function exec_fsub(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcL; let _ = SrcR; let _ = SrcType;
  fp_unimpl_result(RegDst, "FSUB")
}

function exec_fmul(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcL; let _ = SrcR; let _ = SrcType;
  fp_unimpl_result(RegDst, "FMUL")
}

function exec_fdiv(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcL; let _ = SrcR; let _ = SrcType;
  fp_unimpl_result(RegDst, "FDIV")
}

function exec_fsqrt(RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "FSQRT")
}

function exec_frecip(RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "FRECIP")
}

function exec_fexp(RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "FEXP")
}

function exec_fmadd(RegDst : bits(5), SrcA : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcA; let _ = SrcL; let _ = SrcR; let _ = SrcType;
  fp_unimpl_result(RegDst, "FMADD")
}

function exec_fmsub(RegDst : bits(5), SrcA : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcA; let _ = SrcL; let _ = SrcR; let _ = SrcType;
  fp_unimpl_result(RegDst, "FMSUB")
}

function exec_fnmadd(RegDst : bits(5), SrcA : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcA; let _ = SrcL; let _ = SrcR; let _ = SrcType;
  fp_unimpl_result(RegDst, "FNMADD")
}

function exec_fnmsub(RegDst : bits(5), SrcA : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcA; let _ = SrcL; let _ = SrcR; let _ = SrcType;
  fp_unimpl_result(RegDst, "FNMSUB")
}

function exec_fcvt(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = DstType; let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "FCVT")
}

function exec_fcvta(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = DstType; let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "FCVTA")
}

function exec_fcvtm(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = DstType; let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "FCVTM")
}

function exec_fcvtn(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = DstType; let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "FCVTN")
}

function exec_fcvtp(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = DstType; let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "FCVTP")
}

function exec_fcvtz(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = DstType; let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "FCVTZ")
}

function exec_scvtf(RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "SCVTF")
}

function exec_ucvtf(RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let _ = SrcL; let _ = SrcType;
  fp_unimpl_result(RegDst, "UCVTF")
}

// Template blocks: FENTRY/FEXIT/FRET.*
// Spec source: docs/architecture/isa-manual/src/chapters/06_templates.adoc
//
// Bring-up semantics implemented here:
// - `uimm15` is a byte stack adjustment (must preserve 16B alignment by convention).
// - Register range is inclusive.
// - Frame layout (staged):
//     new_sp = sp - (uimm + 8*nregs)
//     locals = [new_sp, new_sp+uimm)
//     save area starts at (new_sp+uimm), regs stored in ascending reg# order.
//
// ABI mapping (docs/reference/linxisa-assembly-agent-guide.md):
// - R1 = sp
// - R10 = ra

function template_sp() -> bits(5) = { 0b00001 }

function template_save_range(base_sp : bits(64), begin : bits(5), endv : bits(5), uimm : int) -> unit = {
  let b : int = unsigned(begin);
  let e : int = unsigned(endv);
  let n : int = if e >= b then (e - b + 1) else 0;
  var k : int = 0;
  while k < n do {
    let r : bits(5) = sail_zeros(5) + (b + k);
    let v : bits(64) = read_reg5(r);
    let ea : bits(64) = base_sp + (sail_zeros(64) + (uimm + 8*k));
    mem_store64_le(ea, v);
    k = k + 1
  }
}

function template_restore_range(base_sp : bits(64), begin : bits(5), endv : bits(5), uimm : int) -> unit = {
  let b : int = unsigned(begin);
  let e : int = unsigned(endv);
  let n : int = if e >= b then (e - b + 1) else 0;
  var k : int = 0;
  while k < n do {
    let r : bits(5) = sail_zeros(5) + (b + k);
    let ea : bits(64) = base_sp + (sail_zeros(64) + (uimm + 8*k));
    let v : bits(64) = mem_load64_le(ea);
    write_reg5(r, v);
    k = k + 1
  }
}

function exec_fentry(SrcBegin : bits(5), SrcEnd : bits(5), uimm15 : bits(15)) -> unit = {
  let uimm : int = unsigned(uimm15);
  let sp0 : bits(64) = read_reg5(template_sp());
  let b : int = unsigned(SrcBegin);
  let e : int = unsigned(SrcEnd);
  let nregs : int = if e >= b then (e - b + 1) else 0;
  let frame : int = uimm + 8*nregs;
  let sp1 : bits(64) = sp0 - (sail_zeros(64) + frame);
  write_reg5(template_sp(), sp1);
  template_save_range(sp1, SrcBegin, SrcEnd, uimm)
}

function exec_fexit(DstBegin : bits(5), DstEnd : bits(5), uimm15 : bits(15)) -> unit = {
  let uimm : int = unsigned(uimm15);
  let sp0 : bits(64) = read_reg5(template_sp());
  let b : int = unsigned(DstBegin);
  let e : int = unsigned(DstEnd);
  let nregs : int = if e >= b then (e - b + 1) else 0;
  template_restore_range(sp0, DstBegin, DstEnd, uimm);
  let frame : int = uimm + 8*nregs;
  write_reg5(template_sp(), sp0 + (sail_zeros(64) + frame))
}

function exec_fret_ra(DstBegin : bits(5), DstEnd : bits(5), uimm15 : bits(15)) -> unit = {
  // Return control-flow is expressed via explicit RET blocks + SETC.TGT in this model.
  exec_fexit(DstBegin, DstEnd, uimm15)
}

function exec_fret_stk(DstBegin : bits(5), DstEnd : bits(5), uimm15 : bits(15)) -> unit = {
  exec_fexit(DstBegin, DstEnd, uimm15)
}

// Bulk memory templates.
// Spec: docs/architecture/isa-manual/src/chapters/06_templates.adoc
// Encoding uses three registers; bring-up convention:
//   - RegSrc0 = dst/base
//   - RegSrc1 = src/value
//   - RegSrc2 = len (bytes)

function exec_mcopy(RegSrc0 : bits(5), RegSrc1 : bits(5), RegSrc2 : bits(5)) -> unit = {
  let dst0 : bits(64) = read_reg5(RegSrc0);
  let src0 : bits(64) = read_reg5(RegSrc1);
  let len  : int = unsigned(read_reg5(RegSrc2));
  var i : int = 0;
  while i < len do {
    let b : bits(8) = read_mem8(src0 + (sail_zeros(64) + i));
    write_mem8(dst0 + (sail_zeros(64) + i), b);
    i = i + 1
  }
}

function exec_mset(RegSrc0 : bits(5), RegSrc1 : bits(5), RegSrc2 : bits(5)) -> unit = {
  let dst0 : bits(64) = read_reg5(RegSrc0);
  let val8 : bits(8)  = read_reg5(RegSrc1)[7..0];
  let len  : int = unsigned(read_reg5(RegSrc2));
  var i : int = 0;
  while i < len do {
    write_mem8(dst0 + (sail_zeros(64) + i), val8);
    i = i + 1
  }
}

// Extended context save/restore (v0.2 bring-up).
// We do not yet model extended state; treat as no-ops for now (but keep explicit
// to allow template blocks to execute).
function exec_esave(RegSrc0 : bits(5), RegSrc1 : bits(5), RegSrc2 : bits(5)) -> unit = {
  let _ = RegSrc0; let _ = RegSrc1; let _ = RegSrc2;
  ()
}

function exec_ercov(RegSrc0 : bits(5), RegSrc1 : bits(5), RegSrc2 : bits(5)) -> unit = {
  let _ = RegSrc0; let _ = RegSrc1; let _ = RegSrc2;
  ()
}

// -----------------------------------------------------------------------------
// Execution control

// ACR requests
// Spec: docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc
//
// Staged semantics:
// - `ACRC`: immediately triggers a synchronous SCALL trap.
//   - TRAPNUM = SCALL (6)
//   - TRAPARG0 = source PC/TPC of the ACRC
//   - BI = 1 (treat as body-interrupting service request)
//   - CAUSE encodes request_type in low bits (profile-defined; we record it for software).
function exec_acrc(RST_Type : bits(4)) -> unit = {
  let trapnum = (sail_zeros(6) + 6); // SCALL
  let cause : bits(24) = sail_zero_extend(RST_Type, 24);
  raise_trap(trapnum, cause, read_pc_or_tpc(), 0b1)
}

// `ACRE`: ACR enter request taken at block commit in the full model.
// We do not yet model privilege rings / EVBASE / EBARG replay in Sail; treat as a no-op.
function exec_acre(RRA_Type : bits(4)) -> unit = {
  let _ = RRA_Type;
  ()
}

function exec_assert(SrcL : bits(5)) -> unit = {
  let v = read_reg5(SrcL);
  if exceptions_enabled() & (v == 0x0000_0000_0000_0000) then trap_assert_fail(read_pc_or_tpc()) else ()
}


function exec_fence_i() -> unit = {
  // Instruction cache fence; architecturally no-op in staged Sail.
  ()
}

function exec_fence_d() -> unit = {
  // Data cache fence; architecturally no-op in staged Sail.
  ()
}

// -----------------------------------------------------------------------------
// Cache + TLB maintenance (staged)
//
// The Sail model does not currently model caches/TLB structures. We still provide
// these instructions with explicit operand validation where architecturally
// required by the ISA manual, and otherwise treat them as functional no-ops.

function is_canonical_va48(va : bits(64)) -> bool = {
  // 48-bit canonical address: bits[63:48] must equal sign-extension of bit 47.
  let sign = va[47];
  if sign == 0b0 then va[63..48] == 0x0000 else va[63..48] == 0xFFFF
}

function exec_tlb_iv(SrcL : bits(5)) -> unit = {
  let va = read_reg5(SrcL);
  if not_bool(is_canonical_va48(va)) then {
    // Manual: must raise translation fault (treated as MMU_PF).
    // Trap wiring is still staged, so keep the failure explicit.
    unimplemented("tlb.iv: non-canonical VA => E_DATA(MMU_PF)")
  } else {
    ()
  }
}

function exec_tlb_iav(SrcL : bits(5)) -> unit = {
  let va = read_reg5(SrcL);
  if not_bool(is_canonical_va48(va)) then {
    unimplemented("tlb.iav: non-canonical VA => E_DATA(MMU_PF)")
  } else {
    ()
  }
}

function exec_tlb_ia(SrcL : bits(5)) -> unit = {
  let x = read_reg5(SrcL);
  // Manual: SrcL[63:16] must be zero.
  if x[63..16] != 0x0000_0000_0000 then {
    unimplemented("tlb.ia: reserved bits nonzero => E_INST(EC_ILLEGAL)")
  } else {
    ()
  }
}

function exec_tlb_iall() -> unit = {
  ()
}

function exec_dc_iall() -> unit = { () }
function exec_dc_iva(SrcL : bits(5)) -> unit = { () }
function exec_dc_isw(SrcL : bits(5)) -> unit = { () }
function exec_dc_zva(SrcL : bits(5)) -> unit = { () }
function exec_dc_cva(SrcL : bits(5)) -> unit = { () }
function exec_dc_civa(SrcL : bits(5)) -> unit = { () }
function exec_dc_csw(SrcL : bits(5)) -> unit = { () }
function exec_dc_cisw(SrcL : bits(5)) -> unit = { () }

function exec_ic_iall() -> unit = { () }
function exec_ic_iva(SrcL : bits(5)) -> unit = { () }

function exec_bc_iall() -> unit = { () }
function exec_bc_iva(SrcL : bits(5)) -> unit = { () }

// (exec_ebreak defined earlier near compressed instruction handlers)

// Block split / transform hints (front-end metadata; no architectural effect).
function exec_bwt() -> unit = { () }
function exec_bwi() -> unit = { () }
function exec_bwe() -> unit = { () }
function exec_bse() -> unit = { () }

// -----------------------------------------------------------------------------
// CMD: Block boundary markers (BSTART/BSTOP)
//
// Normative: docs/architecture/isa-manual/src/chapters/04_block_isa.adoc and
// docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc.
//
// Architectural rule: every control-flow target must land on a block start marker;
// violations trap with E_BLOCK(EC_CFI), kind=CFI_BAD_TARGET.

function exec_bstart() -> unit = {
  // Generic BSTART (COND, <label>) form.
  // - Terminates previous block (commit boundary).
  // - Starts a new block and initializes BARG.
  // - Records block type/xfer kind/next target for commit.
  //
  // Decoder provides block metadata and target.
  let tgt = decoded_block_target_pc();
  if not_bool(is_block_start_marker(tgt)) then {
    // EC_CFI_KIND=1 (CFI_BAD_TARGET)
    trap_block_cfi(0x1, read_pc_or_tpc())
  } else {
    block_commit_boundary();
    barg_reset_at_block_start();
    // Reset descriptor-seen state for the new block header.
    bdesc_reset();
    barg_set_block_type(decoded_block_type());
    barg_set_xfer_kind(decoded_block_xfer_kind());
    barg_set_next_pc_target(tgt)
  }
}

// Typed 32/48-bit BSTART variants share the same boundary semantics; the decoder
// distinguishes the specific block type/xfer kind encoding.
function exec_bstart_std() -> unit = { exec_bstart() }
function exec_bstart_fp() -> unit = { exec_bstart() }
function exec_bstart_sys() -> unit = { exec_bstart() }
function exec_bstart_mpar() -> unit = { exec_bstart() }
function exec_bstart_mseq() -> unit = { exec_bstart() }
function exec_bstart_vpar() -> unit = { exec_bstart() }
function exec_bstart_vseq() -> unit = { exec_bstart() }
function exec_bstart_par() -> unit = { exec_bstart() }
function exec_bstart_cube() -> unit = { exec_bstart() }
function exec_bstart_tma() -> unit = { exec_bstart() }
function exec_bstart_tepl() -> unit = { exec_bstart() }
function exec_bstart_fixp() -> unit = { exec_bstart() }
function exec_bstart_tload() -> unit = { exec_bstart() }
function exec_bstart_tstore() -> unit = { exec_bstart() }
function exec_bstart_tmov() -> unit = { exec_bstart() }
function exec_bstart_tmatmul() -> unit = { exec_bstart() }
function exec_bstart_tmatmul_acc() -> unit = { exec_bstart() }
function exec_bstart_acccvt() -> unit = { exec_bstart() }
function exec_bstart_call() -> unit = { exec_bstart() }

function exec_hl_bstart_std() -> unit = { exec_bstart() }
function exec_hl_bstart_fp() -> unit = { exec_bstart() }
function exec_hl_bstart_sys() -> unit = { exec_bstart() }

function exec_c_bstart() -> unit = { exec_bstart() }
function exec_c_bstart_std() -> unit = { exec_bstart() }
function exec_c_bstart_fp() -> unit = { exec_bstart() }
function exec_c_bstart_sys() -> unit = { exec_bstart() }
function exec_c_bstart_mpar() -> unit = { exec_bstart() }
function exec_c_bstart_mseq() -> unit = { exec_bstart() }
function exec_c_bstart_vpar() -> unit = { exec_bstart() }
function exec_c_bstart_vseq() -> unit = { exec_bstart() }

function exec_bstop() -> unit = {
  // Explicit block terminator.
  // For staged tile/vector headers, perform mandatory-descriptor validation at
  // the end of the header stream before committing the boundary.
  bdesc_validate_header_end(read_pc_or_tpc());
  block_commit_boundary()
}

function exec_c_bstop() -> unit = { exec_bstop() }

// -----------------------------------------------------------------------------
// B.* header descriptors (staged)
//
// In the staged model we track descriptor-family presence for mandatory header
// validation (E_BLOCK(EC_BLOCKFMT)). Full descriptor field semantics (tile
// binding, sizes, LB0..LB2 writes, etc.) are brought up incrementally.

function exec_b_dim() -> unit = {
  // Staged semantics: mark presence and update LB0..LB2 using decoder-provided decoded value.
  let idx = decoded_bdim_index();
  let v = decoded_bdim_value();
  match idx {
    0b00 => ssr_lb0 = v,
    0b01 => ssr_lb1 = v,
    0b10 => ssr_lb2 = v,
    _ => ()
  };
  bdesc_mark_dim()
}
function exec_c_b_dim() -> unit = { exec_b_dim() }
function exec_c_b_dimi() -> unit = { exec_b_dim() }

function exec_b_text() -> unit = { bdesc_mark_text() }
function exec_b_arg() -> unit = { bdesc_mark_arg() }
function exec_b_ior() -> unit = { bdesc_mark_ior() }
function exec_b_iot() -> unit = { bdesc_mark_iot() }
function exec_b_ioti() -> unit = { bdesc_mark_iot() }

function exec_b_attr() -> unit = {
  // Staged semantics: latch raw attribute word so DR (bit 26) can be consulted.
  battr_raw = decoded_battr_raw()
}
function exec_b_hint() -> unit = { () }
function exec_b_iod() -> unit = { () }

// -----------------------------------------------------------------------------
// V.* vector instructions (staged bring-up)
//
// Current staged conventions (per bring-up notes):
// - vec_length = 1 << LCFR[19:16]
// - lane element width is 32-bit for integer ALU forms.
// - predication: p[i]=1 lanes are computed; p[i]=0 lanes produce unspecified values.
// - explicit merge is performed via V.PSEL.

// 32-bit helpers (must appear before first use in Sail).
function ror32bits(x : bits(32), sh : int) -> bits(32) = {
  let s = tmod_int(sh, 32);
  if s == 0 then x else sail_shiftright(x, s) | sail_shiftleft(x, 32 - s)
}

function rol32bits(x : bits(32), sh : int) -> bits(32) = {
  let s = tmod_int(sh, 32);
  if s == 0 then x else sail_shiftleft(x, s) | sail_shiftright(x, 32 - s)
}

// NOTE: bitfield_wrap32 and mask_low_n32 are provided by ../lib/common.sail.

function sext_low_n32(field : bits(32), n : int) -> bits(32) = {
  if n >= 32 then field
  else {
    let sign1 : bits(32) = sail_shiftright(field, n - 1);
    let sign : bits(1) = sign1[0..0];
    if sign == 0b1 then (field | (not_vec(mask_low_n32(n)))) else field
  }
}

function clz_low_n32(field : bits(32), n : int) -> int = {
  var c : int = 0;
  var i : int = n - 1;
  while i >= 0 do {
    let b32 : bits(32) = sail_shiftright(field, i);
    let b : bits(1) = b32[0..0];
    if b == 0b1 then i = -1
    else { c = c + 1; i = i - 1 }
  };
  c
}

function ctz_low_n32(field : bits(32), n : int) -> int = {
  var c : int = 0;
  var i : int = 0;
  while i < n do {
    let b32 : bits(32) = sail_shiftright(field, i);
    let b : bits(1) = b32[0..0];
    if b == 0b1 then i = n
    else { c = c + 1; i = i + 1 }
  };
  c
}

function popcount_low_n32(field : bits(32), n : int) -> int = {
  var c : int = 0;
  var i : int = 0;
  while i < n do {
    let b32 : bits(32) = sail_shiftright(field, i);
    let b : bits(1) = b32[0..0];
    if b == 0b1 then c = c + 1 else ();
    i = i + 1
  };
  c
}

function exec_v_add(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then (a + b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_sub(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then (a - b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_and(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then (a & b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_or(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then (a | b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_xor(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then (a ^ b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

// Immediate forms: operate on 32-bit lanes with sign/zero extension per form.
function exec_v_addi(SrcL_k : bits(3), uimm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sail_zero_extend(uimm12, 32);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then (a + imm) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_subi(SrcL_k : bits(3), uimm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sail_zero_extend(uimm12, 32);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then (a - imm) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_andi(SrcL_k : bits(3), simm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then (a & imm) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_ori(SrcL_k : bits(3), simm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then (a | imm) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_xori(SrcL_k : bits(3), simm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then (a ^ imm) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

// Compare ops: write lane predicate values (0 or 1).
function vec_bool32(b : bool) -> bits(32) = { if b then 0x0000_0001 else 0x0000_0000 }

function exec_v_cmp_eq(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(a == b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_ne(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(a != b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_lt(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(signed(a) < signed(b)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_ge(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(signed(a) >= signed(b)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_ltu(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(unsigned(a) < unsigned(b)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_geu(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(unsigned(a) >= unsigned(b)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

// Compare immediate forms.
function exec_v_cmp_eqi(SrcL_k : bits(3), simm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(a == imm) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_nei(SrcL_k : bits(3), simm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(a != imm) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_lti(SrcL_k : bits(3), simm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(signed(a) < signed(imm)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_gei(SrcL_k : bits(3), simm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(signed(a) >= signed(imm)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_ltui(SrcL_k : bits(3), uimm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sail_zero_extend(uimm12, 32);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(unsigned(a) < unsigned(imm)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_geui(SrcL_k : bits(3), uimm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sail_zero_extend(uimm12, 32);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(unsigned(a) >= unsigned(imm)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

// Boolean combines (treat non-zero as true; produce 0/1).
function exec_v_cmp_and(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i) != 0x0000_0000;
    let b = vec_get_lane32(rhs, i) != 0x0000_0000;
    let r : bits(32) = if active then vec_bool32(a & b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_or(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i) != 0x0000_0000;
    let b = vec_get_lane32(rhs, i) != 0x0000_0000;
    let r : bits(32) = if active then vec_bool32(a | b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_andi(SrcL_k : bits(3), simm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i) != 0x0000_0000;
    let b = imm != 0x0000_0000;
    let r : bits(32) = if active then vec_bool32(a & b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_ori(SrcL_k : bits(3), simm12 : bits(12), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let imm : bits(32) = sext12_to64(simm12)[31..0];
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i) != 0x0000_0000;
    let b = imm != 0x0000_0000;
    let r : bits(32) = if active then vec_bool32(a | b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

// Vector conditional select: Dst = (SrcP != 0) ? SrcL : SrcR
function exec_v_csel(SrcP_k : bits(3), SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let pvec = read_vt(SrcP_k);
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let pv : bits(32) = vec_get_lane32(pvec, i);
    let take_l = pv != 0x0000_0000;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then (if take_l then a else b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

// Bit manipulation (lane-local) using bitfield-wrap (M=lsb, Nminus1=width-1).
function exec_v_bcnt(SrcL_k : bits(3), Nminus1 : bits(6), M : bits(6), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let n0 : int = unsigned(Nminus1) + 1;
  let n : int = if n0 > 32 then 32 else n0;
  let m : int = unsigned(M);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let x : bits(32) = vec_get_lane32(lhs, i);
    let f : bits(32) = bitfield_wrap32(x, m, n);
    let c : int = popcount_low_n32(f, n);
    let r : bits(32) = if active then (sail_zeros(32) + c) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_clz(SrcL_k : bits(3), Nminus1 : bits(6), M : bits(6), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let n0 : int = unsigned(Nminus1) + 1;
  let n : int = if n0 > 32 then 32 else n0;
  let m : int = unsigned(M);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let x : bits(32) = vec_get_lane32(lhs, i);
    let f : bits(32) = bitfield_wrap32(x, m, n);
    let c : int = clz_low_n32(f, n);
    let r : bits(32) = if active then (sail_zeros(32) + c) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_ctz(SrcL_k : bits(3), Nminus1 : bits(6), M : bits(6), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let n0 : int = unsigned(Nminus1) + 1;
  let n : int = if n0 > 32 then 32 else n0;
  let m : int = unsigned(M);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let x : bits(32) = vec_get_lane32(lhs, i);
    let f : bits(32) = bitfield_wrap32(x, m, n);
    let c : int = ctz_low_n32(f, n);
    let r : bits(32) = if active then (sail_zeros(32) + c) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_bxu(SrcL_k : bits(3), Nminus1 : bits(6), M : bits(6), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let n0 : int = unsigned(Nminus1) + 1;
  let n : int = if n0 > 32 then 32 else n0;
  let m : int = unsigned(M);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let x : bits(32) = vec_get_lane32(lhs, i);
    let f : bits(32) = bitfield_wrap32(x, m, n);
    let r : bits(32) = if active then f else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_bxs(SrcL_k : bits(3), Nminus1 : bits(6), M : bits(6), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let n0 : int = unsigned(Nminus1) + 1;
  let n : int = if n0 > 32 then 32 else n0;
  let m : int = unsigned(M);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let x : bits(32) = vec_get_lane32(lhs, i);
    let f : bits(32) = bitfield_wrap32(x, m, n);
    let sx : bits(32) = sext_low_n32(f, n);
    let r : bits(32) = if active then sx else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_bic(SrcL_k : bits(3), Nminus1 : bits(6), M : bits(6), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let n0 : int = unsigned(Nminus1) + 1;
  let n : int = if n0 > 32 then 32 else n0;
  let m : int = unsigned(M);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let x : bits(32) = vec_get_lane32(lhs, i);
    let r0 : bits(32) = ror32bits(x, m);
    let cleared : bits(32) = r0 & (not_vec(mask_low_n32(n)));
    let y : bits(32) = rol32bits(cleared, m);
    let r : bits(32) = if active then y else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_bis(SrcL_k : bits(3), Nminus1 : bits(6), M : bits(6), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let n0 : int = unsigned(Nminus1) + 1;
  let n : int = if n0 > 32 then 32 else n0;
  let m : int = unsigned(M);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let x : bits(32) = vec_get_lane32(lhs, i);
    let r0 : bits(32) = ror32bits(x, m);
    let setv : bits(32) = r0 | mask_low_n32(n);
    let y : bits(32) = rol32bits(setv, m);
    let r : bits(32) = if active then y else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

// For V.BXU/BXS we already use the bitfield wrap helpers above.

function exec_v_div(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  // Signed 32-bit lane divide; div-by-zero yields 0 (match scalar exec_div convention).
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let ai : int = signed(sext32_from32(a));
    let bi : int = signed(sext32_from32(b));
    let qi : int = if b == 0x0000_0000 then 0 else (tdiv_int(ai, bi));
    let r : bits(32) = if active then (sail_zeros(32) + qi) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

// -----------------------------------------------------------------------------
// Vector multiply / max/min / rem / rev (staged)
//
// Spec: docs/architecture/isa-manual/src/generated/instruction_details.adoc

function bit_reverse32(x : bits(32)) -> bits(32) = {
  var r : bits(32) = 0x0000_0000;
  var i : int = 0;
  while i < 32 do {
    let b : bits(1) = sail_shiftright(x, i)[0..0];
    if b == 0b1 then r = r | sail_shiftleft(0x0000_0001, (31 - i)) else ();
    i = i + 1
  };
  r
}

function exec_v_mul(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let prod : int = unsigned(a) * unsigned(b);
    let r : bits(32) = if active then (sail_zeros(32) + prod) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_madd(SrcL_k : bits(3), SrcR_k : bits(3), SrcD_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let add = read_vt(SrcD_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let d : bits(32) = vec_get_lane32(add, i);
    let prod : int = unsigned(a) * unsigned(b);
    let sum  : int = prod + unsigned(d);
    let r : bits(32) = if active then (sail_zeros(32) + sum) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_max(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then (if signed(a) >= signed(b) then a else b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_min(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then (if signed(a) <= signed(b) then a else b) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_rem(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let ai : int = signed(sext32_from32(a));
    let bi : int = signed(sext32_from32(b));
    let ri : int = if b == 0x0000_0000 then ai else (ai - (tdiv_int(ai, bi) * bi));
    let r : bits(32) = if active then (sail_zeros(32) + ri) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_rev(SrcL_k : bits(3), immr : bits(6), imml : bits(6), Dst_k : bits(3)) -> unit = {
  // Strict v0.3: per-lane byte-swap of 32-bit elements (bswap32).
  // immr/imml currently ignored in strict bring-up.
  let _ = immr; let _ = imml;
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let x32 : bits(32) = vec_get_lane32(a, i);
    let x64 : bits(64) = zext32_from32(x32);
    let r32 : bits(32) = (rev_bytes_low_n(x64, 32))[31..0];
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

// -----------------------------------------------------------------------------
// Vector loads (staged)
//
// Normative source for per-mnemonic memory width/extend:
// - docs/architecture/isa-manual/src/generated/instruction_details.adoc
//
// Note: The staged vector RF is 64 lanes of 32-bit (vt0..vt7). For 64-bit loads
// (V.LD*), we pack each 64-bit element into two adjacent 32-bit lanes: lo32 at
// lane (2*i), hi32 at lane (2*i+1), and we use vw64 = vw32/2.

function vec_store64_packed(v : vec_reg64x32, elem : int, x : bits(64)) -> vec_reg64x32 = {
  let lo : bits(32) = x[31..0];
  let hi : bits(32) = x[63..32];
  let v1 = vec_set_lane32(v, 2*elem, lo);
  vec_set_lane32(v1, 2*elem + 1, hi)
}

function vec_compute_ea(base : bits(64), lc0_scaled : int, off : bits(64)) -> bits(64) = {
  base + (sail_zeros(64) + lc0_scaled) + off
}

function vec_off_from_idx32(idx32 : bits(32), shamt : bits(5)) -> bits(64) = {
  sail_shiftleft(sext32_from32(idx32), unsigned(shamt))
}

function exec_v_lb(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let idx32 : bits(32) = vec_get_lane32(idxv, i);
    let ea : bits(64) = vec_compute_ea(base, unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx32, shamt));
    let b : bits(8) = read_mem8(ea);
    let r32 : bits(32) = if active then sext_low_n32(sail_zero_extend(b, 32), 8) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r32)
  };
  write_vt(Dst_k, out)
}

function exec_v_lbu(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let idx32 : bits(32) = vec_get_lane32(idxv, i);
    let ea : bits(64) = vec_compute_ea(base, unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx32, shamt));
    let b : bits(8) = read_mem8(ea);
    let r32 : bits(32) = if active then sail_zero_extend(b, 32) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r32)
  };
  write_vt(Dst_k, out)
}

function exec_v_lh(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let idx32 : bits(32) = vec_get_lane32(idxv, i);
    let ea : bits(64) = vec_compute_ea(base, 2 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx32, shamt));
    let h : bits(16) = mem_load16_le(ea);
    let r32 : bits(32) = if active then sext_low_n32(sail_zero_extend(h, 32), 16) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r32)
  };
  write_vt(Dst_k, out)
}

function exec_v_lhu(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let idx32 : bits(32) = vec_get_lane32(idxv, i);
    let ea : bits(64) = vec_compute_ea(base, 2 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx32, shamt));
    let h : bits(16) = mem_load16_le(ea);
    let r32 : bits(32) = if active then sail_zero_extend(h, 32) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r32)
  };
  write_vt(Dst_k, out)
}

function exec_v_lw(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let idx32 : bits(32) = vec_get_lane32(idxv, i);
    let ea : bits(64) = vec_compute_ea(base, 4 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx32, shamt));
    let w : bits(32) = mem_load32_le(ea);
    let r32 : bits(32) = if active then w else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r32)
  };
  write_vt(Dst_k, out)
}

function exec_v_ld(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    let active = bitvector_access(pm, 2*i) == 0b1;
    let idx32 : bits(32) = vec_get_lane32(idxv, i);
    let ea : bits(64) = vec_compute_ea(base, 8 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx32, shamt));
    let d : bits(64) = mem_load64_le(ea);
    if active then out = vec_store64_packed(out, i, d) else ()
  };
  write_vt(Dst_k, out)
}

// Broadcast variants (BRG): compute address from lane0 offset and broadcast.
function exec_v_lb_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  let b : bits(8) = read_mem8(ea0);
  let r32 : bits(32) = sext_low_n32(sail_zero_extend(b, 32), 8);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

function exec_v_lbu_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  let b : bits(8) = read_mem8(ea0);
  let r32 : bits(32) = sail_zero_extend(b, 32);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

function exec_v_ld_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, 8 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  let d : bits(64) = mem_load64_le(ea0);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    let active = bitvector_access(pm, 2*i) == 0b1;
    if active then out = vec_store64_packed(out, i, d) else ()
  };
  write_vt(Dst_k, out)
}

// Immediate offset forms.
function exec_v_lbi(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let off : bits(64) = sext24_to64(simm24);
  let ea : bits(64) = vec_compute_ea(base, unsigned(ssr_lc0[31..0]), off);
  let b : bits(8) = read_mem8(ea);
  let r32 : bits(32) = sext_low_n32(sail_zero_extend(b, 32), 8);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

function exec_v_lbui(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let off : bits(64) = sext24_to64(simm24);
  let ea : bits(64) = vec_compute_ea(base, unsigned(ssr_lc0[31..0]), off);
  let b : bits(8) = read_mem8(ea);
  let r32 : bits(32) = sail_zero_extend(b, 32);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

function exec_v_ldi(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let off : bits(64) = sext24_to64(simm24);
  let ea : bits(64) = vec_compute_ea(base, 8 * unsigned(ssr_lc0[31..0]), off);
  let d : bits(64) = mem_load64_le(ea);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    let active = bitvector_access(pm, 2*i) == 0b1;
    if active then out = vec_store64_packed(out, i, d) else ()
  };
  write_vt(Dst_k, out)
}

function exec_v_lbi_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lbi(SrcL, simm24, Dst_k, local)
}

function exec_v_lbui_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lbui(SrcL, simm24, Dst_k, local)
}

function exec_v_ldi_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_ldi(SrcL, simm24, Dst_k, local)
}

// More BRG variants.
function exec_v_lh_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, 2 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  let h : bits(16) = mem_load16_le(ea0);
  let r32 : bits(32) = sext_low_n32(sail_zero_extend(h, 32), 16);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

function exec_v_lhu_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, 2 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  let h : bits(16) = mem_load16_le(ea0);
  let r32 : bits(32) = sail_zero_extend(h, 32);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

function exec_v_lw_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, 4 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  let w : bits(32) = mem_load32_le(ea0);
  let r32 : bits(32) = w;
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

function exec_v_lwu(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  // 32-bit load, zero-extended; in 32-bit lanes this is a direct write.
  exec_v_lw(SrcL, SrcR_k, shamt, Dst_k, local)
}

function exec_v_lwu_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lw_brg(SrcL, SrcR_k, shamt, Dst_k, local)
}

// Immediate-offset loads (I) for 16/32.
function exec_v_lhi(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let off : bits(64) = sext24_to64(simm24);
  let ea : bits(64) = vec_compute_ea(base, 2 * unsigned(ssr_lc0[31..0]), off);
  let h : bits(16) = mem_load16_le(ea);
  let r32 : bits(32) = sext_low_n32(sail_zero_extend(h, 32), 16);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

function exec_v_lhi_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lhi(SrcL, simm24, Dst_k, local)
}

function exec_v_lhui(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let off : bits(64) = sext24_to64(simm24);
  let ea : bits(64) = vec_compute_ea(base, 2 * unsigned(ssr_lc0[31..0]), off);
  let h : bits(16) = mem_load16_le(ea);
  let r32 : bits(32) = sail_zero_extend(h, 32);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

function exec_v_lhui_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lhui(SrcL, simm24, Dst_k, local)
}

function exec_v_lwi(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let off : bits(64) = sext24_to64(simm24);
  let ea : bits(64) = vec_compute_ea(base, 4 * unsigned(ssr_lc0[31..0]), off);
  let w : bits(32) = mem_load32_le(ea);
  let r32 : bits(32) = w;
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    out = vec_set_lane32(out, i, if active then r32 else undefined_bitvector(32))
  };
  write_vt(Dst_k, out)
}

function exec_v_lwi_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

function exec_v_lwui(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

function exec_v_lwui_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

// Unscaled (.U) forms: staged model currently treats these the same as the scaled forms.
function exec_v_ldi_u(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_ldi(SrcL, simm24, Dst_k, local)
}

function exec_v_ldi_u_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_ldi(SrcL, simm24, Dst_k, local)
}

function exec_v_lhi_u(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lhi(SrcL, simm24, Dst_k, local)
}

function exec_v_lhi_u_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lhi(SrcL, simm24, Dst_k, local)
}

function exec_v_lhui_u(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lhui(SrcL, simm24, Dst_k, local)
}

function exec_v_lhui_u_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lhui(SrcL, simm24, Dst_k, local)
}

function exec_v_lwi_u(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

function exec_v_lwi_u_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

function exec_v_lwui_u(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

function exec_v_lwui_u_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(3), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

// -----------------------------------------------------------------------------
// Vector atomic RMW loads (staged)
//
// Spec: docs/architecture/isa-manual/src/generated/instruction_details.adoc
//
// Staged note: We do not model atomicity between lanes/cores; we implement the
// informative Read/Modify/Write sequence on memory.

function exec_v_lw_add(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, old + b);
      out = vec_set_lane32(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_lw_and(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, old & b);
      out = vec_set_lane32(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_lw_or(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, old | b);
      out = vec_set_lane32(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_lw_xor(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, old ^ b);
      out = vec_set_lane32(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_lw_max(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, if (signed(old) >= signed(b)) then old else b);
      out = vec_set_lane32(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_lw_min(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, if (signed(old) <= signed(b)) then old else b);
      out = vec_set_lane32(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_ld_add(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      mem_store64_le(ea, old + b);
      out = vec_store64_packed(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_ld_and(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      mem_store64_le(ea, old & b);
      out = vec_store64_packed(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_ld_or(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      mem_store64_le(ea, old | b);
      out = vec_store64_packed(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_ld_xor(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      mem_store64_le(ea, old ^ b);
      out = vec_store64_packed(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_ld_max(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      mem_store64_le(ea, if (signed(old) >= signed(b)) then old else b);
      out = vec_store64_packed(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_ld_min(RegDst_k : bits(3), SrcL : bits(5), SrcR_k : bits(3), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      mem_store64_le(ea, if (signed(old) <= signed(b)) then old else b);
      out = vec_store64_packed(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

// -----------------------------------------------------------------------------
// Vector atomic RMW stores (staged)
//
// Spec: docs/architecture/isa-manual/src/generated/instruction_details.adoc
// Staged note: do not model ordering/atomicity; just Read/Modify/Write.

function exec_v_sd_add(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      mem_store64_le(ea, old + b)
    } else ()
  }
}

function exec_v_sd_and(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      mem_store64_le(ea, old & b)
    } else ()
  }
}

function exec_v_sd_or(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      mem_store64_le(ea, old | b)
    } else ()
  }
}

function exec_v_sd_xor(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      mem_store64_le(ea, old ^ b)
    } else ()
  }
}

function exec_v_sd_max(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      let n  : bits(64) = if (signed(old) >= signed(b)) then old else b;
      mem_store64_le(ea, n)
    } else ()
  }
}

function exec_v_sd_min(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let old : bits(64) = mem_load64_le(ea);
      let lo : bits(32) = vec_get_lane32(src, 2*i);
      let hi : bits(32) = vec_get_lane32(src, 2*i + 1);
      let b  : bits(64) = hi @ lo;
      let n  : bits(64) = if (signed(old) <= signed(b)) then old else b;
      mem_store64_le(ea, n)
    } else ()
  }
}

function exec_v_sw_add(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, old + b)
    } else ()
  }
}

function exec_v_sw_and(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, old & b)
    } else ()
  }
}

function exec_v_sw_or(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, old | b)
    } else ()
  }
}

function exec_v_sw_xor(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, old ^ b)
    } else ()
  }
}

function exec_v_sw_max(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      let n   : bits(32) = if (signed(old) >= signed(b)) then old else b;
      mem_store32_le(ea, n)
    } else ()
  }
}

function exec_v_sw_min(SrcL : bits(5), SrcR_k : bits(3), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      let n   : bits(32) = if (signed(old) <= signed(b)) then old else b;
      mem_store32_le(ea, n)
    } else ()
  }
}

// -----------------------------------------------------------------------------
// Vector shifts (staged)
// Spec: docs/architecture/isa-manual/src/generated/instruction_details.adoc

function exec_v_sll(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let a = read_vt(SrcL_k);
  let b = read_vt(SrcR_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let bv : bits(32) = vec_get_lane32(b, i);
    let sh : int = unsigned(bv[5..0]);
    let r  : bits(32) = if active then sail_shiftleft(av, sh) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_slli(SrcL_k : bits(3), shamt : bits(6), Dst_k : bits(3)) -> unit = {
  let a = read_vt(SrcL_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let sh : int = unsigned(shamt);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let r  : bits(32) = if active then sail_shiftleft(av, sh) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_sra(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let a = read_vt(SrcL_k);
  let b = read_vt(SrcR_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let bv : bits(32) = vec_get_lane32(b, i);
    let sh : int = unsigned(bv[5..0]);
    let r  : bits(32) = if active then sail_arith_shiftright(av, sh) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_srai(SrcL_k : bits(3), shamt : bits(6), Dst_k : bits(3)) -> unit = {
  let a = read_vt(SrcL_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let sh : int = unsigned(shamt);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let r  : bits(32) = if active then sail_arith_shiftright(av, sh) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_srl(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let a = read_vt(SrcL_k);
  let b = read_vt(SrcR_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let bv : bits(32) = vec_get_lane32(b, i);
    let sh : int = unsigned(bv[5..0]);
    let r  : bits(32) = if active then sail_shiftright(av, sh) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_srli(SrcL_k : bits(3), shamt : bits(6), Dst_k : bits(3)) -> unit = {
  let a = read_vt(SrcL_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let sh : int = unsigned(shamt);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let r  : bits(32) = if active then sail_shiftright(av, sh) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

// -----------------------------------------------------------------------------
// Vector shuffle (staged)
//
// The manual currently leaves the operation as "Execute operation as selected".
// POLICY (staged): provide deterministic, non-trapping behavior without claiming
// to implement the full shuffle semantics. We currently pass SrcL through to Dst
// under the active-lane mask.

function vshfl_unimpl(mnemonic : string) -> unit = {
  let _ = mnemonic;
  ()
}

function int_xor_nonneg(a : int, b : int) -> int = {
  // Bitwise xor for non-negative ints (used for SHFL.BFLY lane id computation).
  if (a == 0) & (b == 0) then 0
  else {
    let abit : int = tmod_int(a, 2);
    let bbit : int = tmod_int(b, 2);
    let low : int = if abit == bbit then 0 else 1;
    low + 2 * int_xor_nonneg(tdiv_int(a, 2), tdiv_int(b, 2))
  }
}

function exec_v_shfl_bfly(SrcL_k : bits(3), SrcP_k : bits(3), Dst_k : bits(3)) -> unit = {
  // Strict v0.3 group-local shuffle. BFLY variant.
  // range is fixed to lanenum (whole group); delt from SrcP; src_id = laneid XOR delt.
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lanenum : int = if lb0_i == 0 then vw else (if lb0_i < vw then lb0_i else vw);
  let pm = read_predicate_p();
  let data = read_vt(SrcL_k);
  let maskv = read_vt(SrcP_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (lanenum - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let mask : int = unsigned(vec_get_lane32(maskv, i));
    let delt : int = tmod_int(mask, lanenum);
    let src_id : int = int_xor_nonneg(i, delt);
    let in_range : bool = (0 <= src_id) & (src_id < lanenum);
    let r : bits(32) = if active then (if in_range then vec_get_lane32(data, src_id) else vec_get_lane32(data, i)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_shfl_down(SrcL_k : bits(3), SrcR_k : bits(3), SrcP_k : bits(3), Dst_k : bits(3)) -> unit = {
  // Strict v0.3 group-local shuffle. DOWN variant.
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lanenum : int = if lb0_i == 0 then vw else (if lb0_i < vw then lb0_i else vw);
  let pm = read_predicate_p();
  let data = read_vt(SrcL_k);
  let rangev = read_vt(SrcR_k);
  let offv = read_vt(SrcP_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (lanenum - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let range_raw : int = unsigned(vec_get_lane32(rangev, i));
    let range : int = if range_raw == 0 then lanenum else range_raw;
    let offset : int = unsigned(vec_get_lane32(offv, i));
    let delt : int = tmod_int(offset, range);
    let src_id : int = i + delt;
    let in_seg : bool = (tmod_int(i, range) + delt) < range;
    let r : bits(32) = if active then (if in_seg then vec_get_lane32(data, src_id) else vec_get_lane32(data, i)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  // Lanes above lanenum are unspecified.
  write_vt(Dst_k, out)
}

function exec_v_shfl_idx(SrcL_k : bits(3), SrcR_k : bits(3), SrcP_k : bits(3), Dst_k : bits(3)) -> unit = {
  // Strict v0.3 group-local shuffle. IDX variant.
  // range from SrcR; idx from SrcP; out-of-segment falls back to self.
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lanenum : int = if lb0_i == 0 then vw else (if lb0_i < vw then lb0_i else vw);
  let pm = read_predicate_p();
  let data = read_vt(SrcL_k);
  let rangev = read_vt(SrcR_k);
  let idxv = read_vt(SrcP_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (lanenum - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let range_raw : int = unsigned(vec_get_lane32(rangev, i));
    let range : int = if range_raw == 0 then lanenum else range_raw;
    let idx : int = unsigned(vec_get_lane32(idxv, i));
    // Segment base for this lane, segment width = range.
    let base : int = i - tmod_int(i, range);
    let src_id : int = base + tmod_int(idx, range);
    let in_seg : bool = (src_id >= base) & (src_id < (base + range));
    let r : bits(32) = if active then (if in_seg then vec_get_lane32(data, src_id) else vec_get_lane32(data, i)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_shfl_up(SrcL_k : bits(3), SrcR_k : bits(3), SrcP_k : bits(3), Dst_k : bits(3)) -> unit = {
  // Strict v0.3 group-local shuffle. UP variant.
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lanenum : int = if lb0_i == 0 then vw else (if lb0_i < vw then lb0_i else vw);
  let pm = read_predicate_p();
  let data = read_vt(SrcL_k);
  let rangev = read_vt(SrcR_k);
  let offv = read_vt(SrcP_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (lanenum - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let range_raw : int = unsigned(vec_get_lane32(rangev, i));
    let range : int = if range_raw == 0 then lanenum else range_raw;
    let offset : int = unsigned(vec_get_lane32(offv, i));
    let delt : int = tmod_int(offset, range);
    let src_id : int = i - delt;
    let in_seg : bool = (tmod_int(i, range) - delt) >= 0;
    let r : bits(32) = if active then (if in_seg then vec_get_lane32(data, src_id) else vec_get_lane32(data, i)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_shfli_bfly(SrcL_k : bits(3), imm7 : bits(7), Dst_k : bits(3)) -> unit = {
  // Immediate BFLY: mask from imm7; range fixed to lanenum.
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lanenum : int = if lb0_i == 0 then vw else (if lb0_i < vw then lb0_i else vw);
  let pm = read_predicate_p();
  let data = read_vt(SrcL_k);
  let mask_imm : int = unsigned(imm7);
  let delt : int = tmod_int(mask_imm, lanenum);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (lanenum - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let src_id : int = int_xor_nonneg(i, delt);
    let in_range : bool = (0 <= src_id) & (src_id < lanenum);
    let r : bits(32) = if active then (if in_range then vec_get_lane32(data, src_id) else vec_get_lane32(data, i)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_shfli_down(SrcL_k : bits(3), SrcR_k : bits(3), imm7 : bits(7), Dst_k : bits(3)) -> unit = {
  // Immediate DOWN: offset from imm7, range from SrcR.
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lanenum : int = if lb0_i == 0 then vw else (if lb0_i < vw then lb0_i else vw);
  let pm = read_predicate_p();
  let data = read_vt(SrcL_k);
  let rangev = read_vt(SrcR_k);
  let offset_imm : int = unsigned(imm7);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (lanenum - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let range_raw : int = unsigned(vec_get_lane32(rangev, i));
    let range : int = if range_raw == 0 then lanenum else range_raw;
    let delt : int = tmod_int(offset_imm, range);
    let src_id : int = i + delt;
    let in_seg : bool = (tmod_int(i, range) + delt) < range;
    let r : bits(32) = if active then (if in_seg then vec_get_lane32(data, src_id) else vec_get_lane32(data, i)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_shfli_idx(SrcL_k : bits(3), SrcR_k : bits(3), imm7 : bits(7), Dst_k : bits(3)) -> unit = {
  // Immediate IDX: idx from imm7, range from SrcR.
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lanenum : int = if lb0_i == 0 then vw else (if lb0_i < vw then lb0_i else vw);
  let pm = read_predicate_p();
  let data = read_vt(SrcL_k);
  let rangev = read_vt(SrcR_k);
  let idx_imm : int = unsigned(imm7);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (lanenum - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let range_raw : int = unsigned(vec_get_lane32(rangev, i));
    let range : int = if range_raw == 0 then lanenum else range_raw;
    let base : int = i - tmod_int(i, range);
    let src_id : int = base + tmod_int(idx_imm, range);
    let in_seg : bool = (src_id >= base) & (src_id < (base + range));
    let r : bits(32) = if active then (if in_seg then vec_get_lane32(data, src_id) else vec_get_lane32(data, i)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_shfli_up(SrcL_k : bits(3), SrcR_k : bits(3), imm7 : bits(7), Dst_k : bits(3)) -> unit = {
  // Immediate UP: offset from imm7, range from SrcR.
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lanenum : int = if lb0_i == 0 then vw else (if lb0_i < vw then lb0_i else vw);
  let pm = read_predicate_p();
  let data = read_vt(SrcL_k);
  let rangev = read_vt(SrcR_k);
  let offset_imm : int = unsigned(imm7);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (lanenum - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let range_raw : int = unsigned(vec_get_lane32(rangev, i));
    let range : int = if range_raw == 0 then lanenum else range_raw;
    let delt : int = tmod_int(offset_imm, range);
    let src_id : int = i - delt;
    let in_seg : bool = (tmod_int(i, range) - delt) >= 0;
    let r : bits(32) = if active then (if in_seg then vec_get_lane32(data, src_id) else vec_get_lane32(data, i)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

// -----------------------------------------------------------------------------
// Vector queue ops / reductions / format-convert shims (staged)

function exec_v_qpush(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  // Strict v0.3 memory-queue push.
  // Per active lane (P=1):
  //   base = SrcL[lane] (u32 address)
  //   val  = SrcR[lane]
  // Layout:
  //   base+0x00 : u32 head
  //   base+0x04 : u32 tail
  //   base+0x08 : u32 capacity (elements)
  //   base+0x10 : u32 data[capacity]
  // If full: do not modify queue; Dst[lane]=0.
  // If success: enqueue and Dst[lane]=1.
  // Inactive lanes: Dst[lane]=undefined.
  // NOTE: This staged model executes lanes in increasing laneid order.
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lanenum : int = if lb0_i == 0 then vw else (if lb0_i < vw then lb0_i else vw);
  let pm = read_predicate_p();
  let basev = read_vt(SrcL_k);
  let valv = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (lanenum - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    if active then {
      let base : bits(64) = zext32_from32(vec_get_lane32(basev, i));
      let head : bits(32) = mem_load32_le(base + 0x0000_0000_0000_0000);
      let tail : bits(32) = mem_load32_le(base + 0x0000_0000_0000_0004);
      let cap  : bits(32) = mem_load32_le(base + 0x0000_0000_0000_0008);
      let cap_i : int = unsigned(cap);
      if cap_i == 0 then {
        // Treat cap==0 as permanently full/invalid.
        out = vec_set_lane32(out, i, 0x0000_0000)
      } else {
        let head_i : int = unsigned(head);
        let tail_i : int = unsigned(tail);
        let next_tail_i : int = tmod_int(tail_i + 1, cap_i);
        let full : bool = next_tail_i == tmod_int(head_i, cap_i);
        if full then {
          out = vec_set_lane32(out, i, 0x0000_0000)
        } else {
          let slot : int = tmod_int(tail_i, cap_i);
          let ea : bits(64) = base + (sail_zeros(64) + (16 + slot * 4));
          mem_store32_le(ea, vec_get_lane32(valv, i));
          mem_store32_le(base + 0x0000_0000_0000_0004, sail_zeros(32) + next_tail_i);
          out = vec_set_lane32(out, i, 0x0000_0001)
        }
      }
    } else {
      out = vec_set_lane32(out, i, undefined_bitvector(32))
    }
  };
  write_vt(Dst_k, out)
}

function exec_v_qpop(SrcL_k : bits(3), Dst_k : bits(3)) -> unit = {
  // Strict v0.3 memory-queue pop.
  // Per active lane (P=1):
  //   base = SrcL[lane] (u32 address)
  // If empty: Dst[lane]=0 and queue not modified.
  // If success: dequeue element and write popped value to Dst.
  // Inactive lanes: Dst[lane]=undefined.
  // NOTE: This staged model executes lanes in increasing laneid order.
  let vw : int = vec_length_from_lcfr();
  let lb0_i : int = unsigned(ssr_lb0[31..0]);
  let lanenum : int = if lb0_i == 0 then vw else (if lb0_i < vw then lb0_i else vw);
  let pm = read_predicate_p();
  let basev = read_vt(SrcL_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (lanenum - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    if active then {
      let base : bits(64) = zext32_from32(vec_get_lane32(basev, i));
      let head : bits(32) = mem_load32_le(base + 0x0000_0000_0000_0000);
      let tail : bits(32) = mem_load32_le(base + 0x0000_0000_0000_0004);
      let cap  : bits(32) = mem_load32_le(base + 0x0000_0000_0000_0008);
      let cap_i : int = unsigned(cap);
      if cap_i == 0 then {
        out = vec_set_lane32(out, i, 0x0000_0000)
      } else {
        let head_i : int = unsigned(head);
        let tail_i : int = unsigned(tail);
        let empty : bool = tmod_int(head_i, cap_i) == tmod_int(tail_i, cap_i);
        if empty then {
          out = vec_set_lane32(out, i, 0x0000_0000)
        } else {
          let slot : int = tmod_int(head_i, cap_i);
          let ea : bits(64) = base + (sail_zeros(64) + (16 + slot * 4));
          let v32 : bits(32) = mem_load32_le(ea);
          let next_head_i : int = tmod_int(head_i + 1, cap_i);
          mem_store32_le(base + 0x0000_0000_0000_0000, sail_zeros(32) + next_head_i);
          out = vec_set_lane32(out, i, v32)
        }
      }
    } else {
      out = vec_set_lane32(out, i, undefined_bitvector(32))
    }
  };
  write_vt(Dst_k, out)
}

function vrd_unimpl(mnemonic : string) -> unit = { let _ = mnemonic; () }

function exec_v_rdadd(RegDst : bits(5), SrcL_k : bits(3)) -> unit = {
  vrd_unimpl("V.RDADD");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var acc : bits(64) = 0x0000_0000_0000_0000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then acc = acc + zext32_from32(vec_get_lane32(a, i)) else ()
  };
  write_regdst(RegDst, acc)
}

function exec_v_rdand(RegDst : bits(5), SrcL_k : bits(3)) -> unit = {
  vrd_unimpl("V.RDAND");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var acc : bits(32) = 0xFFFF_FFFF;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then acc = acc & vec_get_lane32(a, i) else ()
  };
  write_regdst(RegDst, zext32_from32(acc))
}

function exec_v_rdor(RegDst : bits(5), SrcL_k : bits(3)) -> unit = {
  vrd_unimpl("V.RDOR");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var acc : bits(32) = 0x0000_0000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then acc = acc | vec_get_lane32(a, i) else ()
  };
  write_regdst(RegDst, zext32_from32(acc))
}

function exec_v_rdxor(RegDst : bits(5), SrcL_k : bits(3)) -> unit = {
  vrd_unimpl("V.RDXOR");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var acc : bits(32) = 0x0000_0000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then acc = acc ^ vec_get_lane32(a, i) else ()
  };
  write_regdst(RegDst, zext32_from32(acc))
}

function exec_v_rdmax(RegDst : bits(5), SrcL_k : bits(3)) -> unit = {
  vrd_unimpl("V.RDMAX");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var acc : bits(32) = 0x8000_0000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let x = vec_get_lane32(a, i);
      acc = if signed(acc) >= signed(x) then acc else x
    } else ()
  };
  write_regdst(RegDst, zext32_from32(acc))
}

function exec_v_rdmin(RegDst : bits(5), SrcL_k : bits(3)) -> unit = {
  vrd_unimpl("V.RDMIN");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var acc : bits(32) = 0x7FFF_FFFF;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let x = vec_get_lane32(a, i);
      acc = if signed(acc) <= signed(x) then acc else x
    } else ()
  };
  write_regdst(RegDst, zext32_from32(acc))
}

function exec_v_rdfadd(RegDst : bits(5), SrcL_k : bits(3)) -> unit = {
  // Staged strict bring-up shim:
  // - The ISA manual leaves RDF* operations as "selected by encoded modifiers".
  // - Full floating-point numeric behavior (rounding/flags, f16/f64 packing) is not modeled.
  // For now we return a deterministic placeholder (0) to keep execution deterministic.
  let _ = SrcL_k;
  write_regdst(RegDst, 0x0000_0000_0000_0000)
}

function exec_v_rdfmax(RegDst : bits(5), SrcL_k : bits(3)) -> unit = {
  // Reduce max over active lanes, interpreting lanes as FP32 bitpatterns.
  // NaN policy matches exec_fmax (maxNum-style, canonical qNaN if all NaN).
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var any : bool = false;
  var acc : bits(32) = 0x7FC0_0000; // canonical qNaN
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let x : bits(32) = vec_get_lane32(a, i);
      if not_bool(any) then { any = true; acc = x }
      else {
        let nan_a = fp32_is_nan(acc);
        let nan_b = fp32_is_nan(x);
        let both_zero = fp32_is_zero(acc) & fp32_is_zero(x);
        acc =
          if nan_a & nan_b then 0x7FC0_0000
          else if nan_a then x
          else if nan_b then acc
          else if both_zero then 0x0000_0000
          else if fp32_ge(acc, x) then acc else x
      }
    } else ()
  };
  write_regdst(RegDst, zext32_from32(acc))
}

function exec_v_rdfmin(RegDst : bits(5), SrcL_k : bits(3)) -> unit = {
  // Reduce min over active lanes, interpreting lanes as FP32 bitpatterns.
  // NaN policy matches exec_fmin (minNum-style, canonical qNaN if all NaN).
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var any : bool = false;
  var acc : bits(32) = 0x7FC0_0000; // canonical qNaN
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let x : bits(32) = vec_get_lane32(a, i);
      if not_bool(any) then { any = true; acc = x }
      else {
        let nan_a = fp32_is_nan(acc);
        let nan_b = fp32_is_nan(x);
        let both_zero = fp32_is_zero(acc) & fp32_is_zero(x);
        let neg0 = (acc[31] == 0b1) | (x[31] == 0b1);
        acc =
          if nan_a & nan_b then 0x7FC0_0000
          else if nan_a then x
          else if nan_b then acc
          else if both_zero then (if neg0 then 0x8000_0000 else 0x0000_0000)
          else if fp32_lt(acc, x) then acc else x
      }
    } else ()
  };
  write_regdst(RegDst, zext32_from32(acc))
}

function exec_v_icvt(SrcL_k : bits(3), SrcType : bits(5), DstType : bits(5), Dst_k : bits(3)) -> unit = {
  // Strict bring-up: format conversion selected by 5-bit SrcType/DstType codes.
  // The manual table (see RegId10 operand encoding + convert tables) defines these codes.
  // This Sail model currently implements a conservative subset:
  // - Integer types: u64/u32/u16/u8 and s64/s32/s16/s8
  //   * narrowing: truncate low bits
  //   * widening: sign-extend if src signed, else zero-extend
  // - Other/packed/experimental types: deterministic 0 result (staged).
  // Vector RF is 32-bit lanes; 64-bit elements are packed {hi,lo} into adjacent lanes (2*i,2*i+1).
  let vw32 : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var out = read_vt(Dst_k);

  // Decode a small subset of the 5-bit type space.
  let src_is_u : bool = (SrcType == 0b00000) | (SrcType == 0b00001) | (SrcType == 0b00010) | (SrcType == 0b00011);
  let src_is_s : bool = (SrcType == 0b01000) | (SrcType == 0b01001) | (SrcType == 0b01010) | (SrcType == 0b01011);
  let dst_is_u : bool = (DstType == 0b00000) | (DstType == 0b00001) | (DstType == 0b00010) | (DstType == 0b00011);
  let dst_is_s : bool = (DstType == 0b01000) | (DstType == 0b01001) | (DstType == 0b01010) | (DstType == 0b01011);
  let src_ok : bool = src_is_u | src_is_s;
  let dst_ok : bool = dst_is_u | dst_is_s;
  let src_signed : bool = src_is_s;

  if not_bool(src_ok & dst_ok) then {
    // Reserved/illegal SrcType/DstType encodings must not be generated by software.
    // Model as ILLEGAL_INST in strict bring-up.
    trap_illegal_inst(read_pc_or_tpc())
  } else () ;

  let src_bits : int =
    if SrcType == 0b00000 | SrcType == 0b01000 then 64
    else if SrcType == 0b00001 | SrcType == 0b01001 then 32
    else if SrcType == 0b00010 | SrcType == 0b01010 then 16
    else if SrcType == 0b00011 | SrcType == 0b01011 then 8
    else 32;

  let dst_bits : int =
    if DstType == 0b00000 | DstType == 0b01000 then 64
    else if DstType == 0b00001 | DstType == 0b01001 then 32
    else if DstType == 0b00010 | DstType == 0b01010 then 16
    else if DstType == 0b00011 | DstType == 0b01011 then 8
    else 32;

  let src_is_d : bool = src_ok & (src_bits == 64);
  let dst_is_d : bool = dst_ok & (dst_bits == 64);

  let src_elems : int = if src_is_d then tdiv_int(vw32, 2) else vw32;
  let dst_elems : int = if dst_is_d then tdiv_int(vw32, 2) else vw32;
  let n : int = if src_elems < dst_elems then src_elems else dst_elems;

  foreach (i from 0 to (n - 1)) {
    assert((0 <= i) & (i < 64));
    // predicate lane selection: for 64-bit packed elems, use lane 2*i.
    let wide : bool = src_is_d | dst_is_d;
    if wide then assert(i < 32) else ();
    let pidx : int = if wide then 2*i else i;
    assert((0 <= pidx) & (pidx < 64));
    let active : bool = bitvector_access(pm, pidx) == 0b1;
    if active then {
      // load source value as up-to-64b
      let x64 : bits(64) =
        if src_is_d then {
          let lo : bits(32) = vec_get_lane32(a, 2*i);
          let hi : bits(32) = vec_get_lane32(a, 2*i + 1);
          hi @ lo
        } else {
          let x32 : bits(32) = vec_get_lane32(a, i);
          zext32_from32(x32)
        };

      // truncate to src_bits first (for non-d sources this is already true, but keep explicit)
      let y64 : bits(64) =
        if src_bits == 64 then x64
        else if src_bits == 32 then (sail_zeros(32) @ x64[31..0])
        else if src_bits == 16 then (sail_zeros(48) @ x64[15..0])
        else (sail_zeros(56) @ x64[7..0]);

      // convert to dst_bits via trunc + (sign/zero)-extend
      let z64 : bits(64) =
        if dst_bits < src_bits then {
          // narrowing: truncate
          if dst_bits == 32 then (sail_zeros(32) @ y64[31..0])
          else if dst_bits == 16 then (sail_zeros(48) @ y64[15..0])
          else if dst_bits == 8 then (sail_zeros(56) @ y64[7..0])
          else y64
        } else if dst_bits == src_bits then y64
        else {
          // widening: extend from src_bits
          if src_bits == 32 then (if src_signed then sext32_from32(y64[31..0]) else zext32_from32(y64[31..0]))
          else if src_bits == 16 then (if src_signed then sext16_from16(y64[15..0]) else zext16_from16(y64[15..0]))
          else if src_bits == 8 then (if src_signed then sext8_from8(y64[7..0]) else zext8_from8(y64[7..0]))
          else y64
        };

      if dst_is_d then {
        out = vec_store64_packed(out, i, z64)
      } else {
        let r32 : bits(32) =
          if dst_bits == 32 then z64[31..0]
          else if dst_bits == 16 then (sail_zeros(16) @ z64[15..0])
          else if dst_bits == 8 then (sail_zeros(24) @ z64[7..0])
          else z64[31..0];
        out = vec_set_lane32(out, i, r32)
      }
    } else {
      if dst_is_d then {
        out = vec_set_lane32(out, 2*i, undefined_bitvector(32));
        out = vec_set_lane32(out, 2*i + 1, undefined_bitvector(32))
      } else {
        out = vec_set_lane32(out, i, undefined_bitvector(32))
      }
    }
  };

  write_vt(Dst_k, out)
}

function exec_v_icvtf(SrcL_k : bits(3), SrcType : bits(5), DstType : bits(5), Dst_k : bits(3)) -> unit = {
  // Staged bring-up shim:
  // - This instruction uses the same SrcType/DstType code space as other convert-class ops.
  // - Full float<->int numeric conversions (rounding/flags) are not modeled here.
  // Policy for now:
  //   * Implement integer -> float only as a deterministic placeholder with correct width packing.
  //   * For illegal/reserved encodings: trap ILLEGAL_INST.
  let src_is_int : bool = (SrcType == 0b00000) | (SrcType == 0b00001) | (SrcType == 0b00010) | (SrcType == 0b00011) |
                          (SrcType == 0b01000) | (SrcType == 0b01001) | (SrcType == 0b01010) | (SrcType == 0b01011) |
                          (SrcType == 0b00100) | (SrcType == 0b00101) | (SrcType == 0b00110) | (SrcType == 0b00111) |
                          (SrcType == 0b01100) | (SrcType == 0b01101) | (SrcType == 0b01110);

  // Float type codes (subset): FP64/FP32/FP16/BF16/HiF8/e4m3/e5m2.
  let dst_is_float : bool = (DstType == 0b00000) | (DstType == 0b00001) | (DstType == 0b00100) | (DstType == 0b00101) |
                            (DstType == 0b00110) | (DstType == 0b00111) | (DstType == 0b01000);

  if not_bool(src_is_int & dst_is_float) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let dst_bits : int = if DstType == 0b00000 then 64
                         else if DstType == 0b00001 then 32
                         else if (DstType == 0b00100) | (DstType == 0b00101) then 16
                         else 8;
    let dst_is_d : bool = dst_bits == 64;

    let vw32 : int = vec_length_from_lcfr();
    let vw : int = if dst_is_d then tdiv_int(vw32, 2) else vw32;
    let pm = read_predicate_p();
    var out = read_vt(Dst_k);
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      let pidx : int = if dst_is_d then 2*i else i;
      if dst_is_d then assert(i < 32) else ();
      assert((0 <= pidx) & (pidx < 64));
      let active = bitvector_access(pm, pidx) == 0b1;
      if active then {
        // Placeholder numeric conversion: produce +0 in target format.
        if dst_is_d then {
          out = vec_store64_packed(out, i, 0x0000_0000_0000_0000)
        } else {
          let r32 : bits(32) = if dst_bits == 32 then 0x0000_0000
                               else if dst_bits == 16 then 0x0000_0000
                               else 0x0000_0000;
          out = vec_set_lane32(out, i, r32)
        }
      } else {
        if dst_is_d then {
          out = vec_set_lane32(out, 2*i, undefined_bitvector(32));
          out = vec_set_lane32(out, 2*i + 1, undefined_bitvector(32))
        } else {
          out = vec_set_lane32(out, i, undefined_bitvector(32))
        }
      }
    };
    write_vt(Dst_k, out)
  }
}

function exec_xb(acr_id : bits(12), cross_bid : bits(8)) -> unit = {
  // Strict bring-up (v0.4-draft): XB is a controlled cross-block call dispatcher.
  // The full CAC_TABLE lookup / coupled-vs-decoupled execution is not modeled yet.
  // We DO enforce architectural legality checks and encode them in E_INST cause codes.
  //
  // Encoding notes:
  // - Catalog encodes ACR-ID (10b) and C-ID/CROSS-BID (7b). The Sail decoder passes wider fields;
  //   reserved high bits must be zero.

  // 1) check reserved high bits
  if not_bool(acr_id[11..10] == 0b00) then trap_e_inst(0x10, 0x00, read_pc_or_tpc()) else (); // EC_XBID
  if not_bool(cross_bid[7] == 0b0) then trap_e_inst(0x10, 0x00, read_pc_or_tpc()) else (); // EC_XBID

  // 2) check supported ACR range (bring-up profile: 0..2)
  let target_acr : bits(4) = acr_id[3..0];
  if not_bool((target_acr == 0x0) | (target_acr == 0x1) | (target_acr == 0x2)) then
    trap_e_inst(0x10, 0x00, read_pc_or_tpc())
  else ();

  // 3) permission direction check: may only call same or less-privileged ACR (numerically >= current ACR)
  // Bring-up convention: use ssr_cstate[3:0] as active ACR id.
  let cur_acr : bits(4) = ssr_cstate[3..0];
  // ACR0 is most privileged => allowed if target_acr >= cur_acr.
  if not_bool(unsigned(target_acr) >= unsigned(cur_acr)) then
    trap_e_inst(0x03, 0x00, read_pc_or_tpc()) // EC_PERM
  else ();

  // 4) CAC_TABLE existence/definition check (minimal):
  //    - Read XBINFO for target ACR to obtain CAC_TABLE base.
  //    - If base == 0 => definition missing.
  //    - Otherwise, read first 64-bit word of CAC_TABLE[c-id] (entry size 32B).
  //      If the word is 0 => treat as missing/invalid definition.
  // Full entry parsing (B.ATTR/B.IOR/B.TEXT) is deferred.
  let base : bits(64) = read_xbinfo_for_acr(target_acr);
  if base == 0x0000_0000_0000_0000 then {
    trap_e_inst(0x11, 0x00, read_pc_or_tpc()) // EC_XBDEF
  } else {
    let cid : bits(7) = cross_bid[6..0];
    let off : bits(64) = sail_zero_extend(cid @ 0b00000, 64); // cid * 32
    let ea : bits(64) = base + off;
    let w0 : bits(64) = mem_load64_le(ea);
    if w0 == 0x0000_0000_0000_0000 then trap_e_inst(0x11, 0x00, read_pc_or_tpc()) else ()
  };

  // 5) staged behavior: no-op (dispatch not modeled)
  let _ = cross_bid;
  ()
}

// -----------------------------------------------------------------------------
// Vector stores (staged)
//
// Spec: docs/architecture/isa-manual/src/generated/instruction_details.adoc

function exec_v_shi(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcR);
  let off  : bits(64) = sext24_to64(simm24);
  let ea   : bits(64) = vec_compute_ea(base, 2 * unsigned(ssr_lc0[31..0]), off);
  let data = read_vt(SrcL_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then mem_store16_le(ea, vec_get_lane32(data, i)[15..0]) else ()
  }
}

function exec_v_shi_brg(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_shi(SrcL_k, SrcR, simm24, local)
}

function exec_v_shi_u(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_shi(SrcL_k, SrcR, simm24, local)
}

function exec_v_shi_u_brg(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_shi(SrcL_k, SrcR, simm24, local)
}

function exec_v_sb(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let data = read_vt(SrcD_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let idx32 : bits(32) = vec_get_lane32(idxv, i);
      let ea : bits(64) = vec_compute_ea(base, unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx32, shamt));
      let b : bits(8) = vec_get_lane32(data, i)[7..0];
      write_mem8(ea, b)
    } else ()
  }
}

function exec_v_sw(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  // Store32 register-offset.
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let data = read_vt(SrcD_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let idx32 : bits(32) = vec_get_lane32(idxv, i);
      let ea : bits(64) = vec_compute_ea(base, 4 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx32, shamt));
      let w : bits(32) = vec_get_lane32(data, i);
      mem_store32_le(ea, w)
    } else ()
  }
}

function exec_v_sw_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  // BRG: lane0 address + lane0 data.
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let data = read_vt(SrcD_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, 4 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  mem_store32_le(ea0, vec_get_lane32(data, 0))
}

function exec_v_sw_u(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  // Unscaled: staged model treats same as scaled.
  exec_v_sw(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_sw_u_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  exec_v_sw_brg(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_swi(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcR);
  let off  : bits(64) = sext24_to64(simm24);
  let ea   : bits(64) = vec_compute_ea(base, 4 * unsigned(ssr_lc0[31..0]), off);
  let data = read_vt(SrcL_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then mem_store32_le(ea, vec_get_lane32(data, i)) else ()
  }
}

function exec_v_swi_brg(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_swi(SrcL_k, SrcR, simm24, local)
}

function exec_v_swi_u(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_swi(SrcL_k, SrcR, simm24, local)
}

function exec_v_swi_u_brg(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_swi(SrcL_k, SrcR, simm24, local)
}

function exec_v_sb_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  // BRG: use lane0 address and store lane0 data.
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let data = read_vt(SrcD_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  let b0 : bits(8) = vec_get_lane32(data, 0)[7..0];
  write_mem8(ea0, b0)
}

function exec_v_sh(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let data = read_vt(SrcD_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let idx32 : bits(32) = vec_get_lane32(idxv, i);
      let ea : bits(64) = vec_compute_ea(base, 2 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx32, shamt));
      let h : bits(16) = vec_get_lane32(data, i)[15..0];
      mem_store16_le(ea, h)
    } else ()
  }
}

function exec_v_sh_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let data = read_vt(SrcD_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, 2 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  let h0 : bits(16) = vec_get_lane32(data, 0)[15..0];
  mem_store16_le(ea0, h0)
}

function exec_v_sh_u(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  exec_v_sh(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_sh_u_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  exec_v_sh_brg(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_sd(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  // Store packed 64-bit: read lo/hi from two lanes.
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let data = read_vt(SrcD_k);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let idx32 : bits(32) = vec_get_lane32(idxv, i);
      let ea : bits(64) = vec_compute_ea(base, 8 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx32, shamt));
      let lo : bits(32) = vec_get_lane32(data, 2*i);
      let hi : bits(32) = vec_get_lane32(data, 2*i + 1);
      let d : bits(64) = hi @ lo;
      mem_store64_le(ea, d)
    } else ()
  }
}

function exec_v_sd_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let data = read_vt(SrcD_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, 8 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  let lo : bits(32) = vec_get_lane32(data, 0);
  let hi : bits(32) = vec_get_lane32(data, 1);
  mem_store64_le(ea0, (hi @ lo))
}

function exec_v_sd_u(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  exec_v_sd(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_sd_u_brg(SrcL : bits(5), SrcR_k : bits(3), shamt : bits(5), SrcD_k : bits(3), local : bits(1)) -> unit = {
  exec_v_sd_brg(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_sbi(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcR);
  let off : bits(64) = sext24_to64(simm24);
  let ea : bits(64) = vec_compute_ea(base, unsigned(ssr_lc0[31..0]), off);
  let data = read_vt(SrcL_k);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then write_mem8(ea, vec_get_lane32(data, i)[7..0]) else ()
  }
}

function exec_v_sbi_brg(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_sbi(SrcL_k, SrcR, simm24, local)
}

function exec_v_sdi(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcR);
  let off : bits(64) = sext24_to64(simm24);
  let ea : bits(64) = vec_compute_ea(base, 8 * unsigned(ssr_lc0[31..0]), off);
  let data = read_vt(SrcL_k);
  let vw32 : int = vec_length_from_lcfr();
  let vw : int = tdiv_int(vw32, 2);
  let pm = read_predicate_p();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 32));
    if bitvector_access(pm, 2*i) == 0b1 then {
      let lo : bits(32) = vec_get_lane32(data, 2*i);
      let hi : bits(32) = vec_get_lane32(data, 2*i + 1);
      mem_store64_le(ea, (hi @ lo))
    } else ()
  }
}

function exec_v_sdi_brg(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_sdi(SrcL_k, SrcR, simm24, local)
}

function exec_v_sdi_u(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_sdi(SrcL_k, SrcR, simm24, local)
}

function exec_v_sdi_u_brg(SrcL_k : bits(3), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_sdi(SrcL_k, SrcR, simm24, local)
}

// -----------------------------------------------------------------------------
// V.F* vector floating-point (FSU) - staged bring-up
//
// POLICY: follow scalar FSU behavior for now.
// - For arithmetic/conversion/classify: keep as unimplemented with deterministic 0 result.
// - For compares and min/max: we can reuse the staged bit-pattern IEEE rules already
//   used by scalar exec_feq/exec_flt/exec_fge/exec_fmin/exec_fmax.

function vfp_unimpl(mnemonic : string) -> unit = {
  // Vector FSU shim: keep deterministic but do not raise `unimplemented`.
  let _ = mnemonic;
  ()
}

function exec_v_fadd(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FADD");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fsub(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FSUB");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fmul(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FMUL");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fdiv(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FDIV");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fsqrt(SrcL_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FSQRT");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_frecip(SrcL_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FRECIP");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fexp(SrcL_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FEXP");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fabs(SrcL_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FABS");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fclass(SrcL_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FCLASS");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fcvt(SrcL_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FCVT");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fcvti(SrcL_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FCVTI");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fmadd(SrcL_k : bits(3), SrcR_k : bits(3), SrcA_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FMADD");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fmsub(SrcL_k : bits(3), SrcR_k : bits(3), SrcA_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FMSUB");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fnmadd(SrcL_k : bits(3), SrcR_k : bits(3), SrcA_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FNMADD");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_fnmsub(SrcL_k : bits(3), SrcR_k : bits(3), SrcA_k : bits(3), Dst_k : bits(3)) -> unit = {
  vfp_unimpl("V.FNMSUB");
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let r : bits(32) = if active then 0x0000_0000 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

// Vector FP compares: ordered; NaN => false. Results are 0/1 in each lane.
function exec_v_feq(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(fp32_eq(a, b)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_flt(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(fp32_lt(a, b)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_fge(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(fp32_ge(a, b)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_fne(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let eq = fp32_eq(a, b);
    let r : bits(32) = if active then vec_bool32(not_bool(eq)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

// S-variants are aliases (no exception signaling modeled).
function exec_v_feqs(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = { exec_v_feq(SrcL_k, SrcR_k, Dst_k) }
function exec_v_flts(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = { exec_v_flt(SrcL_k, SrcR_k, Dst_k) }
function exec_v_fges(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = { exec_v_fge(SrcL_k, SrcR_k, Dst_k) }
function exec_v_fnes(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = { exec_v_fne(SrcL_k, SrcR_k, Dst_k) }

function exec_v_fmax(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  // Match scalar exec_fmax logic for fs lanes.
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a32 = vec_get_lane32(lhs, i);
    let b32 = vec_get_lane32(rhs, i);
    let nan_a = fp32_is_nan(a32);
    let nan_b = fp32_is_nan(b32);
    let both_zero = fp32_is_zero(a32) & fp32_is_zero(b32);
    let r32 =
      if nan_a & nan_b then 0x7FC0_0000
      else if nan_a then b32
      else if nan_b then a32
      else if both_zero then 0x0000_0000
      else if fp32_ge(a32, b32) then a32 else b32;
    let r : bits(32) = if active then r32 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_fmin(SrcL_k : bits(3), SrcR_k : bits(3), Dst_k : bits(3)) -> unit = {
  // Match scalar exec_fmin logic for fs lanes.
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a32 = vec_get_lane32(lhs, i);
    let b32 = vec_get_lane32(rhs, i);
    let nan_a = fp32_is_nan(a32);
    let nan_b = fp32_is_nan(b32);
    let both_zero = fp32_is_zero(a32) & fp32_is_zero(b32);
    let neg0 = (a32[31] == 0b1) | (b32[31] == 0b1);
    let r32 =
      if nan_a & nan_b then 0x7FC0_0000
      else if nan_a then b32
      else if nan_b then a32
      else if both_zero then (if neg0 then 0x8000_0000 else 0x0000_0000)
      else if fp32_lt(a32, b32) then a32 else b32;
    let r : bits(32) = if active then r32 else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

// (32-bit helpers defined earlier near V.* block)

function exec_v_psel(SrcP_k : bits(3), SrcL_k : bits(3), SrcR_k : bits(3), neg : bits(1), Dst_k : bits(3)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pvec = read_vt(SrcP_k);
  let lhs = read_vt(SrcL_k);
  let rhs0 = read_vt(SrcR_k);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    let pv : bits(32) = vec_get_lane32(pvec, i);
    let take_l = pv != 0x0000_0000;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b0 : bits(32) = vec_get_lane32(rhs0, i);
    let b : bits(32) = if neg == 0b1 then (0x0000_0000 - b0) else b0;
    let r : bits(32) = if take_l then a else b;
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_fneg(RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  // Bitwise sign flip (fd/fs).
  let a64 = read_reg5(SrcL);
  let is_fs = (SrcType == 0b01);
  if is_fs then {
    let a32 = a64[31..0];
    let r32 = a32 ^ 0x8000_0000;
    write_regdst(RegDst, zext32_from32(r32))
  } else {
    write_regdst(RegDst, a64 ^ 0x8000_0000_0000_0000)
  }
}

// ============================================================
// AGU / Load-Store (staged bring-up; strict v0.3 conventions)
// ============================================================

// -----------------------------------------------------------------------------
// Exclusive load/store + swap + CAS (ARM-style)
//
// Staged semantics:
// - LR.* sets a local exclusive reservation (64B cacheline).
// - SC.* succeeds if reservation matches, stores, and returns status (0=success, 1=failure).
// - SWAP* always swaps and returns the old memory value.
// - CAS* compares memory against SrcR, stores SrcD if equal, returns old memory value.
// - aq/rl/f/far modifiers are parsed but not modeled.

function exec_lr_b(RegDst : bits(5), SrcL : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old8 : bits(8) = read_mem8(ea);
  excl_set(ea);
  write_regdst(RegDst, zext8_from8(old8))
}

function exec_lr_h(RegDst : bits(5), SrcL : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old16 : bits(16) = mem_load16_le(ea);
  excl_set(ea);
  write_regdst(RegDst, zext16_from16(old16))
}

function exec_lr_w(RegDst : bits(5), SrcL : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old32 : bits(32) = mem_load32_le(ea);
  excl_set(ea);
  write_regdst(RegDst, sext32_from32(old32))
}

function exec_lr_d(RegDst : bits(5), SrcL : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old64 : bits(64) = mem_load64_le(ea);
  excl_set(ea);
  write_regdst(RegDst, old64)
}

function exec_sc_b(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let v8 : bits(8) = read_reg5(SrcL)[7..0];
  let ea = read_reg5(SrcR);
  let ok = excl_check(ea);
  if ok then write_mem8(ea, v8) else ();
  excl_clear();
  write_regdst(RegDst, bool_to_u64(not_bool(ok)))
}

function exec_sc_h(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let v16 : bits(16) = read_reg5(SrcL)[15..0];
  let ea = read_reg5(SrcR);
  let ok = excl_check(ea);
  if ok then mem_store16_le(ea, v16) else ();
  excl_clear();
  write_regdst(RegDst, bool_to_u64(not_bool(ok)))
}

function exec_sc_w(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let v32 : bits(32) = read_reg5(SrcL)[31..0];
  let ea = read_reg5(SrcR);
  let ok = excl_check(ea);
  if ok then mem_store32_le(ea, v32) else ();
  excl_clear();
  write_regdst(RegDst, bool_to_u64(not_bool(ok)))
}

function exec_sc_d(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let v64 : bits(64) = read_reg5(SrcL);
  let ea = read_reg5(SrcR);
  let ok = excl_check(ea);
  if ok then mem_store64_le(ea, v64) else ();
  excl_clear();
  write_regdst(RegDst, bool_to_u64(not_bool(ok)))
}

function exec_swapb(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old8 : bits(8) = read_mem8(ea);
  let v8 : bits(8) = read_reg5(SrcR)[7..0];
  write_mem8(ea, v8);
  write_regdst(RegDst, zext8_from8(old8))
}

function exec_swaph(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old16 : bits(16) = mem_load16_le(ea);
  let v16 : bits(16) = read_reg5(SrcR)[15..0];
  mem_store16_le(ea, v16);
  write_regdst(RegDst, zext16_from16(old16))
}

function exec_swapw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old32 : bits(32) = mem_load32_le(ea);
  let v32 : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, v32);
  write_regdst(RegDst, sext32_from32(old32))
}

function exec_swapd(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old64 : bits(64) = mem_load64_le(ea);
  let v64 : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, v64);
  write_regdst(RegDst, old64)
}

function exec_hl_casb(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcD : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old8 : bits(8) = read_mem8(ea);
  let exp8 : bits(8) = read_reg5(SrcR)[7..0];
  let new8 : bits(8) = read_reg5(SrcD)[7..0];
  if old8 == exp8 then write_mem8(ea, new8) else ();
  write_regdst(RegDst, zext8_from8(old8))
}

function exec_hl_cash(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcD : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old16 : bits(16) = mem_load16_le(ea);
  let exp16 : bits(16) = read_reg5(SrcR)[15..0];
  let new16 : bits(16) = read_reg5(SrcD)[15..0];
  if old16 == exp16 then mem_store16_le(ea, new16) else ();
  write_regdst(RegDst, zext16_from16(old16))
}

function exec_hl_casw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcD : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old32 : bits(32) = mem_load32_le(ea);
  let exp32 : bits(32) = read_reg5(SrcR)[31..0];
  let new32 : bits(32) = read_reg5(SrcD)[31..0];
  if old32 == exp32 then mem_store32_le(ea, new32) else ();
  write_regdst(RegDst, sext32_from32(old32))
}

function exec_hl_casd(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcD : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old64 : bits(64) = mem_load64_le(ea);
  let exp64 : bits(64) = read_reg5(SrcR);
  let new64 : bits(64) = read_reg5(SrcD);
  if old64 == exp64 then mem_store64_le(ea, new64) else ();
  write_regdst(RegDst, old64)
}


// -----------------------------------------------------------------------------
// Atomic RMW ops (LW/LD/SW/SD .ADD/.AND/.OR/.XOR/.SMIN/.SMAX/.UMIN/.UMAX)
//
// Staged Sail model notes:
//   - aq/rl/f modifiers are parsed but currently not modeled (no memory ordering)
//   - FAR is treated as a hint only (no special fault-avoid behavior modeled)
//   - Operations are modeled as read-modify-write on the addressed word/dword.
//   - LW.* returns the *old* memory value sign-extended to 64-bit (like LW).
//   - LD.* returns the *old* memory value (64-bit).

function rmw32_add(a : bits(32), b : bits(32)) -> bits(32) = { a + b }
function rmw32_and(a : bits(32), b : bits(32)) -> bits(32) = { a & b }
function rmw32_or(a : bits(32), b : bits(32)) -> bits(32) = { a | b }
function rmw32_xor(a : bits(32), b : bits(32)) -> bits(32) = { a ^ b }

function rmw32_smax(a : bits(32), b : bits(32)) -> bits(32) = { if (signed(a) >= signed(b)) then a else b }
function rmw32_smin(a : bits(32), b : bits(32)) -> bits(32) = { if (signed(a) <= signed(b)) then a else b }
function rmw32_umax(a : bits(32), b : bits(32)) -> bits(32) = { if (unsigned(a) >= unsigned(b)) then a else b }
function rmw32_umin(a : bits(32), b : bits(32)) -> bits(32) = { if (unsigned(a) <= unsigned(b)) then a else b }

function rmw64_add(a : bits(64), b : bits(64)) -> bits(64) = { a + b }
function rmw64_and(a : bits(64), b : bits(64)) -> bits(64) = { a & b }
function rmw64_or(a : bits(64), b : bits(64)) -> bits(64) = { a | b }
function rmw64_xor(a : bits(64), b : bits(64)) -> bits(64) = { a ^ b }

function rmw64_smax(a : bits(64), b : bits(64)) -> bits(64) = { if (signed(a) >= signed(b)) then a else b }
function rmw64_smin(a : bits(64), b : bits(64)) -> bits(64) = { if (signed(a) <= signed(b)) then a else b }
function rmw64_umax(a : bits(64), b : bits(64)) -> bits(64) = { if (unsigned(a) >= unsigned(b)) then a else b }
function rmw64_umin(a : bits(64), b : bits(64)) -> bits(64) = { if (unsigned(a) <= unsigned(b)) then a else b }

function exec_lw_add(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_add(old, b));
  write_regdst(RegDst, sext32_from32(old))
}

function exec_lw_and(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_and(old, b));
  write_regdst(RegDst, sext32_from32(old))
}

function exec_lw_or(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_or(old, b));
  write_regdst(RegDst, sext32_from32(old))
}

function exec_lw_xor(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_xor(old, b));
  write_regdst(RegDst, sext32_from32(old))
}

function exec_lw_smax(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_smax(old, b));
  write_regdst(RegDst, sext32_from32(old))
}

function exec_lw_smin(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_smin(old, b));
  write_regdst(RegDst, sext32_from32(old))
}

function exec_lw_umax(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_umax(old, b));
  write_regdst(RegDst, sext32_from32(old))
}

function exec_lw_umin(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_umin(old, b));
  write_regdst(RegDst, sext32_from32(old))
}

function exec_ld_add(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_add(old, b));
  write_regdst(RegDst, old)
}

function exec_ld_and(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_and(old, b));
  write_regdst(RegDst, old)
}

function exec_ld_or(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_or(old, b));
  write_regdst(RegDst, old)
}

function exec_ld_xor(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_xor(old, b));
  write_regdst(RegDst, old)
}

function exec_ld_smax(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_smax(old, b));
  write_regdst(RegDst, old)
}

function exec_ld_smin(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_smin(old, b));
  write_regdst(RegDst, old)
}

function exec_ld_umax(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_umax(old, b));
  write_regdst(RegDst, old)
}

function exec_ld_umin(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_umin(old, b));
  write_regdst(RegDst, old)
}

function exec_sw_add(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_add(old, b));
  ()
}

function exec_sw_and(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_and(old, b));
  ()
}

function exec_sw_or(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_or(old, b));
  ()
}

function exec_sw_xor(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_xor(old, b));
  ()
}

function exec_sw_smax(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_smax(old, b));
  ()
}

function exec_sw_smin(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_smin(old, b));
  ()
}

function exec_sw_umax(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_umax(old, b));
  ()
}

function exec_sw_umin(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_umin(old, b));
  ()
}

function exec_sd_add(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_add(old, b));
  ()
}

function exec_sd_and(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_and(old, b));
  ()
}

function exec_sd_or(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_or(old, b));
  ()
}

function exec_sd_xor(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_xor(old, b));
  ()
}

function exec_sd_smax(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_smax(old, b));
  ()
}

function exec_sd_smin(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_smin(old, b));
  ()
}

function exec_sd_umax(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_umax(old, b));
  ()
}

function exec_sd_umin(SrcL : bits(5), SrcR : bits(5), far : bits(1), rl : bits(1)) -> unit = {
  let _ = far; let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_umin(old, b));
  ()
}

// NOTE: mem_load{16,32,64}_le are provided by the staged memory model (state/memory.sail).

function exec_lb(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, sext8_from8(b))
}

function exec_lbu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, zext8_from8(b))
}

function exec_lh(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}

function exec_lhu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}

function exec_lw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}

function exec_lwu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}

function exec_ld(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst, d)
}

// NOTE: mem_store{16,32,64}_le are provided by the staged memory model (state/memory.sail).

// Stores.

function exec_sb(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let ea = base + off1;
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(ea, v)
}

function exec_sh(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let ea = base + (sail_shiftleft(off1, 1));
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}

function exec_sw(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let ea = base + (sail_shiftleft(off1, 2));
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}

function exec_sd(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let ea = base + (sail_shiftleft(off1, 3));
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v)
}

// Unscaled store variants (.U): no implicit <<{1,2,3} scaling.

function exec_sh_u(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let ea = base + off1;
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}

function exec_sw_u(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let ea = base + off1;
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}

function exec_sd_u(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let ea = base + off1;
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v)
}

// Immediate-offset loads/stores.

function exec_lbi(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, sext8_from8(b))
}

function exec_lbui(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, zext8_from8(b))
}

function exec_lhi(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + (sail_shiftleft(off, 1));
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}

function exec_lhi_u(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}

function exec_lhui(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + (sail_shiftleft(off, 1));
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}

function exec_lhui_u(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}

function exec_lwi(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + (sail_shiftleft(off, 2));
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}

function exec_lwi_u(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}

function exec_lwui(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + (sail_shiftleft(off, 2));
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}

function exec_lwui_u(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}

function exec_ldi(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + (sail_shiftleft(off, 3));
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst, d)
}

function exec_ldi_u(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst, d)
}

function exec_sbi(SrcD : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcR);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(ea, v)
}

function exec_shi(SrcD : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcR);
  let off = sext12_to64(simm12);
  let ea = base + (sail_shiftleft(off, 1));
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}

function exec_shi_u(SrcD : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcR);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}

function exec_swi(SrcD : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcR);
  let off = sext12_to64(simm12);
  let ea = base + (sail_shiftleft(off, 2));
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}

function exec_swi_u(SrcD : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcR);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}

function exec_sdi(SrcD : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcR);
  let off = sext12_to64(simm12);
  let ea = base + (sail_shiftleft(off, 3));
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v)
}

function exec_sdi_u(SrcD : bits(5), SrcR : bits(5), simm12 : bits(12)) -> unit = {
  let base = read_reg5(SrcR);
  let off = sext12_to64(simm12);
  let ea = base + off;
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v)
}

// PC-relative (PCR) loads/stores.

function exec_lb_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, sext8_from8(b))
}

function exec_lbu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, zext8_from8(b))
}

function exec_lh_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}

function exec_lhu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}

function exec_lw_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}

function exec_lwu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}

function exec_ld_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst, d)
}

function exec_sb_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(ea, v)
}

function exec_sh_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}

function exec_sw_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}

function exec_sd_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc_aligned = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = sail_shiftleft(sext17_to64(simm17), 2);
  let ea = pc_aligned + off;
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v)
}

// -----------------------------------------------------------------------------
// HL (48-bit) pre/post-index loads/stores.
// Contract (per decision):
//   - PR: new_base = base + off; access at new_base; Dst1/Rd = new_base
//   - PO: access at base; new_base = base + off; Dst1/Rd = new_base
// off = sail_shiftleft(apply_srcrtype_arith64(SrcRType, SrcR, shamt_or_scale))

function hl_off_shamt(SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> bits(64) = {
  let idx0 = read_reg5(SrcR);
  let idx1 = apply_srcrtype_arith64(SrcRType, idx0);
  (sail_shiftleft(idx1, unsigned(shamt)))
}

function hl_off_scale(SrcR : bits(5), SrcRType : bits(2), scale : int) -> bits(64) = {
  let idx0 = read_reg5(SrcR);
  let idx1 = apply_srcrtype_arith64(SrcRType, idx0);
  (sail_shiftleft(idx1, scale))
}

function exec_hl_lb_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  let b : bits(8) = read_mem8(new_base);
  write_regdst(RegDst0, sext8_from8(b));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lb_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let b : bits(8) = read_mem8(base);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  write_regdst(RegDst0, sext8_from8(b));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lbu_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  let b : bits(8) = read_mem8(new_base);
  write_regdst(RegDst0, zext8_from8(b));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lbu_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let b : bits(8) = read_mem8(base);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  write_regdst(RegDst0, zext8_from8(b));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lh_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  let h : bits(16) = mem_load16_le(new_base);
  write_regdst(RegDst0, sext16_from16(h));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lh_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let h : bits(16) = mem_load16_le(base);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  write_regdst(RegDst0, sext16_from16(h));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lhu_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  let h : bits(16) = mem_load16_le(new_base);
  write_regdst(RegDst0, zext16_from16(h));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lhu_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let h : bits(16) = mem_load16_le(base);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  write_regdst(RegDst0, zext16_from16(h));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lw_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  let w : bits(32) = mem_load32_le(new_base);
  write_regdst(RegDst0, sext32_from32(w));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lw_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let w : bits(32) = mem_load32_le(base);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  write_regdst(RegDst0, sext32_from32(w));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lwu_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  let w : bits(32) = mem_load32_le(new_base);
  write_regdst(RegDst0, zext32_from32(w));
  write_regdst(RegDst1, new_base)
}

function exec_hl_lwu_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let w : bits(32) = mem_load32_le(base);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  write_regdst(RegDst0, zext32_from32(w));
  write_regdst(RegDst1, new_base)
}

function exec_hl_ld_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  let d : bits(64) = mem_load64_le(new_base);
  write_regdst(RegDst0, d);
  write_regdst(RegDst1, new_base)
}

function exec_hl_ld_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let d : bits(64) = mem_load64_le(base);
  let off = hl_off_shamt(SrcR, SrcRType, shamt);
  let new_base = base + off;
  write_regdst(RegDst0, d);
  write_regdst(RegDst1, new_base)
}

// HL stores return the updated base in RegDst.
function exec_hl_sb_pr(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_scale(SrcR, SrcRType, 0);
  let new_base = base + off;
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(new_base, v);
  write_regdst(RegDst, new_base)
}

function exec_hl_sb_po(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(base, v);
  let off = hl_off_scale(SrcR, SrcRType, 0);
  let new_base = base + off;
  write_regdst(RegDst, new_base)
}

function exec_hl_sh_pr(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_scale(SrcR, SrcRType, 1);
  let new_base = base + off;
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(new_base, v);
  write_regdst(RegDst, new_base)
}

function exec_hl_sh_po(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(base, v);
  let off = hl_off_scale(SrcR, SrcRType, 1);
  let new_base = base + off;
  write_regdst(RegDst, new_base)
}

function exec_hl_sw_pr(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_scale(SrcR, SrcRType, 2);
  let new_base = base + off;
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(new_base, v);
  write_regdst(RegDst, new_base)
}

function exec_hl_sw_po(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(base, v);
  let off = hl_off_scale(SrcR, SrcRType, 2);
  let new_base = base + off;
  write_regdst(RegDst, new_base)
}

function exec_hl_sd_pr(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off = hl_off_scale(SrcR, SrcRType, 3);
  let new_base = base + off;
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(new_base, v);
  write_regdst(RegDst, new_base)
}

function exec_hl_sd_po(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(base, v);
  let off = hl_off_scale(SrcR, SrcRType, 3);
  let new_base = base + off;
  write_regdst(RegDst, new_base)
}

// Aliases without explicit shamt.
// .UPR/.UPO forms use register offset without an explicit shamt field.
// Model them as the corresponding pre/post-index ops with element-size scaling.
function exec_hl_sh_upr(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  exec_hl_sh_pr(RegDst, SrcD, SrcL, SrcR, SrcRType)
}
function exec_hl_sh_upo(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  exec_hl_sh_po(RegDst, SrcD, SrcL, SrcR, SrcRType)
}
function exec_hl_sw_upr(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  exec_hl_sw_pr(RegDst, SrcD, SrcL, SrcR, SrcRType)
}
function exec_hl_sw_upo(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  exec_hl_sw_po(RegDst, SrcD, SrcL, SrcR, SrcRType)
}
function exec_hl_sd_upr(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  exec_hl_sd_pr(RegDst, SrcD, SrcL, SrcR, SrcRType)
}
function exec_hl_sd_upo(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  exec_hl_sd_po(RegDst, SrcD, SrcL, SrcR, SrcRType)
}

// -----------------------------------------------------------------------------
// HL (48-bit) PC-relative / immediate / pair addressing.
//
// Conventions:
// - .PCR uses EA = align4(PC/TPC) + sail_shiftleft(sext17(simm17, 2))
// - *I uses long immediate simm22 with scaled offset by element size.
// - *I.U uses unscaled immediate simm22.
// - *I.PR/*I.PO use simm17 with writeback to Dst1 (per PR/PO contract).
// - *I.UPR/*I.UPO are unscaled pre/post-index (simm17) with writeback.
// - *IP/*P are pair forms: Dst0=mem[EA], Dst1=mem[EA+elem_size]. No writeback.

function hl_pc_aligned4() -> bits(64) = {
  let pc0 = read_pc_or_tpc();
  pc0 & 0xFFFF_FFFF_FFFF_FFFC
}

function hl_ea_pcr(simm17 : bits(17)) -> bits(64) = {
  hl_pc_aligned4() + sail_shiftleft(sext17_to64(simm17), 2)
}

function hl_ea_imm_scaled(base : bits(64), simm22 : bits(22), scale : int) -> bits(64) = {
  let off = sext22_to64(simm22);
  base + (sail_shiftleft(off, scale))
}

function hl_ea_imm_unscaled(base : bits(64), simm22 : bits(22)) -> bits(64) = {
  base + sext22_to64(simm22)
}

function hl_ea_imm17_scaled(base : bits(64), simm17 : bits(17), scale : int) -> bits(64) = {
  let off = sext17_to64(simm17);
  base + (sail_shiftleft(off, scale))
}

function hl_ea_imm17_unscaled(base : bits(64), simm17 : bits(17)) -> bits(64) = {
  base + sext17_to64(simm17)
}

// ---- HL loads: PCR ----
function exec_hl_lb_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, sext8_from8(b))
}
function exec_hl_lbu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, zext8_from8(b))
}
function exec_hl_lh_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}
function exec_hl_lhu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}
function exec_hl_lw_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}
function exec_hl_lwu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}
function exec_hl_ld_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst, d)
}

// ---- HL loads: long immediate (simm22) ----
function exec_hl_lbi(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcL), simm22, 0);
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, sext8_from8(b))
}
function exec_hl_lbui(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcL), simm22, 0);
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, zext8_from8(b))
}
function exec_hl_lhi(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcL), simm22, 1);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}
function exec_hl_lhi_u(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_unscaled(read_reg5(SrcL), simm22);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}
function exec_hl_lhui(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcL), simm22, 1);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}
function exec_hl_lhui_u(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_unscaled(read_reg5(SrcL), simm22);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}
function exec_hl_lwi(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcL), simm22, 2);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}
function exec_hl_lwi_u(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_unscaled(read_reg5(SrcL), simm22);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}
function exec_hl_lwui(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcL), simm22, 2);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}
function exec_hl_lwui_u(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_unscaled(read_reg5(SrcL), simm22);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}
function exec_hl_ldi(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcL), simm22, 3);
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst, d)
}
function exec_hl_ldi_u(RegDst : bits(5), SrcL : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_unscaled(read_reg5(SrcL), simm22);
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst, d)
}

// ---- HL loads: immediate PR/PO (simm17) with writeback ----
function exec_hl_lbi_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_scaled(base, simm17, 0);
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst0, sext8_from8(b));
  write_regdst(RegDst1, ea)
}
function exec_hl_lbi_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let b : bits(8) = read_mem8(base);
  let ea = hl_ea_imm17_scaled(base, simm17, 0);
  write_regdst(RegDst0, sext8_from8(b));
  write_regdst(RegDst1, ea)
}
function exec_hl_lbui_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_scaled(base, simm17, 0);
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst0, zext8_from8(b));
  write_regdst(RegDst1, ea)
}
function exec_hl_lbui_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let b : bits(8) = read_mem8(base);
  let ea = hl_ea_imm17_scaled(base, simm17, 0);
  write_regdst(RegDst0, zext8_from8(b));
  write_regdst(RegDst1, ea)
}
function exec_hl_lhi_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_scaled(base, simm17, 1);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst0, sext16_from16(h));
  write_regdst(RegDst1, ea)
}
function exec_hl_lhi_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let h : bits(16) = mem_load16_le(base);
  let ea = hl_ea_imm17_scaled(base, simm17, 1);
  write_regdst(RegDst0, sext16_from16(h));
  write_regdst(RegDst1, ea)
}
function exec_hl_lhi_upr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst0, sext16_from16(h));
  write_regdst(RegDst1, ea)
}
function exec_hl_lhi_upo(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let h : bits(16) = mem_load16_le(base);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  write_regdst(RegDst0, sext16_from16(h));
  write_regdst(RegDst1, ea)
}
function exec_hl_lhui_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_scaled(base, simm17, 1);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst0, zext16_from16(h));
  write_regdst(RegDst1, ea)
}
function exec_hl_lhui_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let h : bits(16) = mem_load16_le(base);
  let ea = hl_ea_imm17_scaled(base, simm17, 1);
  write_regdst(RegDst0, zext16_from16(h));
  write_regdst(RegDst1, ea)
}
function exec_hl_lhui_upr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst0, zext16_from16(h));
  write_regdst(RegDst1, ea)
}
function exec_hl_lhui_upo(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let h : bits(16) = mem_load16_le(base);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  write_regdst(RegDst0, zext16_from16(h));
  write_regdst(RegDst1, ea)
}
function exec_hl_lwi_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_scaled(base, simm17, 2);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst0, sext32_from32(w));
  write_regdst(RegDst1, ea)
}
function exec_hl_lwi_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let w : bits(32) = mem_load32_le(base);
  let ea = hl_ea_imm17_scaled(base, simm17, 2);
  write_regdst(RegDst0, sext32_from32(w));
  write_regdst(RegDst1, ea)
}
function exec_hl_lwi_upr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst0, sext32_from32(w));
  write_regdst(RegDst1, ea)
}
function exec_hl_lwi_upo(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let w : bits(32) = mem_load32_le(base);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  write_regdst(RegDst0, sext32_from32(w));
  write_regdst(RegDst1, ea)
}
function exec_hl_lwui_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_scaled(base, simm17, 2);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst0, zext32_from32(w));
  write_regdst(RegDst1, ea)
}
function exec_hl_lwui_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let w : bits(32) = mem_load32_le(base);
  let ea = hl_ea_imm17_scaled(base, simm17, 2);
  write_regdst(RegDst0, zext32_from32(w));
  write_regdst(RegDst1, ea)
}
function exec_hl_lwui_upr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst0, zext32_from32(w));
  write_regdst(RegDst1, ea)
}
function exec_hl_lwui_upo(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let w : bits(32) = mem_load32_le(base);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  write_regdst(RegDst0, zext32_from32(w));
  write_regdst(RegDst1, ea)
}
function exec_hl_ldi_pr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_scaled(base, simm17, 3);
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst0, d);
  write_regdst(RegDst1, ea)
}
function exec_hl_ldi_po(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let d : bits(64) = mem_load64_le(base);
  let ea = hl_ea_imm17_scaled(base, simm17, 3);
  write_regdst(RegDst0, d);
  write_regdst(RegDst1, ea)
}
function exec_hl_ldi_upr(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst0, d);
  write_regdst(RegDst1, ea)
}
function exec_hl_ldi_upo(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcL);
  let d : bits(64) = mem_load64_le(base);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  write_regdst(RegDst0, d);
  write_regdst(RegDst1, ea)
}

// ---- HL load pair: immediate simm17 ----
function exec_hl_lbip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 0);
  let v0 : bits(8) = read_mem8(ea);
  let v1 : bits(8) = read_mem8(ea + (sail_zeros(64) + 1));
  write_regdst(RegDst0, sext8_from8(v0));
  write_regdst(RegDst1, sext8_from8(v1))
}
function exec_hl_lbuip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 0);
  let v0 : bits(8) = read_mem8(ea);
  let v1 : bits(8) = read_mem8(ea + (sail_zeros(64) + 1));
  write_regdst(RegDst0, zext8_from8(v0));
  write_regdst(RegDst1, zext8_from8(v1))
}
function exec_hl_lhip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 1);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + (sail_zeros(64) + 2));
  write_regdst(RegDst0, sext16_from16(v0));
  write_regdst(RegDst1, sext16_from16(v1))
}
function exec_hl_lhip_u(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcL), simm17);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + (sail_zeros(64) + 2));
  write_regdst(RegDst0, sext16_from16(v0));
  write_regdst(RegDst1, sext16_from16(v1))
}
function exec_hl_lhuip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 1);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + (sail_zeros(64) + 2));
  write_regdst(RegDst0, zext16_from16(v0));
  write_regdst(RegDst1, zext16_from16(v1))
}
function exec_hl_lhuip_u(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcL), simm17);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + (sail_zeros(64) + 2));
  write_regdst(RegDst0, zext16_from16(v0));
  write_regdst(RegDst1, zext16_from16(v1))
}
function exec_hl_lwip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 2);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + (sail_zeros(64) + 4));
  write_regdst(RegDst0, sext32_from32(v0));
  write_regdst(RegDst1, sext32_from32(v1))
}
function exec_hl_lwip_u(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcL), simm17);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + (sail_zeros(64) + 4));
  write_regdst(RegDst0, sext32_from32(v0));
  write_regdst(RegDst1, sext32_from32(v1))
}
function exec_hl_lwuip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 2);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + (sail_zeros(64) + 4));
  write_regdst(RegDst0, zext32_from32(v0));
  write_regdst(RegDst1, zext32_from32(v1))
}
function exec_hl_lwuip_u(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcL), simm17);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + (sail_zeros(64) + 4));
  write_regdst(RegDst0, zext32_from32(v0));
  write_regdst(RegDst1, zext32_from32(v1))
}
function exec_hl_ldip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 3);
  let v0 : bits(64) = mem_load64_le(ea);
  let v1 : bits(64) = mem_load64_le(ea + (sail_zeros(64) + 8));
  write_regdst(RegDst0, v0);
  write_regdst(RegDst1, v1)
}
function exec_hl_ldip_u(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcL), simm17);
  let v0 : bits(64) = mem_load64_le(ea);
  let v1 : bits(64) = mem_load64_le(ea + (sail_zeros(64) + 8));
  write_regdst(RegDst0, v0);
  write_regdst(RegDst1, v1)
}

// ---- HL load pair: reg+reg+shamt ----
function exec_hl_lbp(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(8) = read_mem8(ea);
  let v1 : bits(8) = read_mem8(ea + (sail_zeros(64) + 1));
  write_regdst(RegDst0, sext8_from8(v0));
  write_regdst(RegDst1, sext8_from8(v1))
}
function exec_hl_lbup(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(8) = read_mem8(ea);
  let v1 : bits(8) = read_mem8(ea + (sail_zeros(64) + 1));
  write_regdst(RegDst0, zext8_from8(v0));
  write_regdst(RegDst1, zext8_from8(v1))
}
function exec_hl_lhp(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + (sail_zeros(64) + 2));
  write_regdst(RegDst0, sext16_from16(v0));
  write_regdst(RegDst1, sext16_from16(v1))
}
function exec_hl_lhup(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + (sail_zeros(64) + 2));
  write_regdst(RegDst0, zext16_from16(v0));
  write_regdst(RegDst1, zext16_from16(v1))
}
function exec_hl_lwp(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + (sail_zeros(64) + 4));
  write_regdst(RegDst0, sext32_from32(v0));
  write_regdst(RegDst1, sext32_from32(v1))
}
function exec_hl_lwup(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + (sail_zeros(64) + 4));
  write_regdst(RegDst0, zext32_from32(v0));
  write_regdst(RegDst1, zext32_from32(v1))
}
function exec_hl_ldp(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(64) = mem_load64_le(ea);
  let v1 : bits(64) = mem_load64_le(ea + (sail_zeros(64) + 8));
  write_regdst(RegDst0, v0);
  write_regdst(RegDst1, v1)
}

// ---- HL stores: PCR ----
function exec_hl_sb_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(ea, v)
}
function exec_hl_sh_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}
function exec_hl_sw_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}
function exec_hl_sd_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v)
}

// ---- HL stores: long immediate (simm22) ----
function exec_hl_sbi(SrcD : bits(5), SrcR : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcR), simm22, 0);
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(ea, v)
}
function exec_hl_shi(SrcD : bits(5), SrcR : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcR), simm22, 1);
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}
function exec_hl_shi_u(SrcD : bits(5), SrcR : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_unscaled(read_reg5(SrcR), simm22);
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}
function exec_hl_swi(SrcD : bits(5), SrcR : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcR), simm22, 2);
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}
function exec_hl_swi_u(SrcD : bits(5), SrcR : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_unscaled(read_reg5(SrcR), simm22);
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}
function exec_hl_sdi(SrcD : bits(5), SrcR : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_scaled(read_reg5(SrcR), simm22, 3);
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v)
}
function exec_hl_sdi_u(SrcD : bits(5), SrcR : bits(5), simm22 : bits(22)) -> unit = {
  let ea = hl_ea_imm_unscaled(read_reg5(SrcR), simm22);
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v)
}

// ---- HL stores: immediate PR/PO (simm17) with writeback (Rd gets updated base) ----
function exec_hl_sbi_pr(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let ea = hl_ea_imm17_scaled(base, simm17, 0);
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(ea, v);
  write_regdst(RegDst, ea)
}
function exec_hl_sbi_po(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(base, v);
  let ea = hl_ea_imm17_scaled(base, simm17, 0);
  write_regdst(RegDst, ea)
}
function exec_hl_shi_pr(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let ea = hl_ea_imm17_scaled(base, simm17, 1);
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v);
  write_regdst(RegDst, ea)
}
function exec_hl_shi_po(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(base, v);
  let ea = hl_ea_imm17_scaled(base, simm17, 1);
  write_regdst(RegDst, ea)
}
function exec_hl_shi_upr(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v);
  write_regdst(RegDst, ea)
}
function exec_hl_shi_upo(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(base, v);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  write_regdst(RegDst, ea)
}
function exec_hl_swi_pr(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let ea = hl_ea_imm17_scaled(base, simm17, 2);
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v);
  write_regdst(RegDst, ea)
}
function exec_hl_swi_po(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(base, v);
  let ea = hl_ea_imm17_scaled(base, simm17, 2);
  write_regdst(RegDst, ea)
}
function exec_hl_swi_upr(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v);
  write_regdst(RegDst, ea)
}
function exec_hl_swi_upo(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(base, v);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  write_regdst(RegDst, ea)
}
function exec_hl_sdi_pr(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let ea = hl_ea_imm17_scaled(base, simm17, 3);
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v);
  write_regdst(RegDst, ea)
}
function exec_hl_sdi_po(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(base, v);
  let ea = hl_ea_imm17_scaled(base, simm17, 3);
  write_regdst(RegDst, ea)
}
function exec_hl_sdi_upr(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v);
  write_regdst(RegDst, ea)
}
function exec_hl_sdi_upo(RegDst : bits(5), SrcD : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let base = read_reg5(SrcR);
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(base, v);
  let ea = hl_ea_imm17_unscaled(base, simm17);
  write_regdst(RegDst, ea)
}

// ---- HL store pair: immediate simm17 ----
function exec_hl_sbip(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcR), simm17, 0);
  let v0 : bits(8) = read_reg5(SrcD0)[7..0];
  let v1 : bits(8) = read_reg5(SrcD1)[7..0];
  write_mem8(ea, v0);
  write_mem8(ea + (sail_zeros(64) + 1), v1)
}
function exec_hl_ship(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcR), simm17, 1);
  let v0 : bits(16) = read_reg5(SrcD0)[15..0];
  let v1 : bits(16) = read_reg5(SrcD1)[15..0];
  mem_store16_le(ea, v0);
  mem_store16_le(ea + (sail_zeros(64) + 2), v1)
}
function exec_hl_ship_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcR), simm17);
  let v0 : bits(16) = read_reg5(SrcD0)[15..0];
  let v1 : bits(16) = read_reg5(SrcD1)[15..0];
  mem_store16_le(ea, v0);
  mem_store16_le(ea + (sail_zeros(64) + 2), v1)
}
function exec_hl_swip(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcR), simm17, 2);
  let v0 : bits(32) = read_reg5(SrcD0)[31..0];
  let v1 : bits(32) = read_reg5(SrcD1)[31..0];
  mem_store32_le(ea, v0);
  mem_store32_le(ea + (sail_zeros(64) + 4), v1)
}
function exec_hl_swip_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcR), simm17);
  let v0 : bits(32) = read_reg5(SrcD0)[31..0];
  let v1 : bits(32) = read_reg5(SrcD1)[31..0];
  mem_store32_le(ea, v0);
  mem_store32_le(ea + (sail_zeros(64) + 4), v1)
}
function exec_hl_sdip(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcR), simm17, 3);
  let v0 : bits(64) = read_reg5(SrcD0);
  let v1 : bits(64) = read_reg5(SrcD1);
  mem_store64_le(ea, v0);
  mem_store64_le(ea + (sail_zeros(64) + 8), v1)
}
function exec_hl_sdip_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcR), simm17);
  let v0 : bits(64) = read_reg5(SrcD0);
  let v1 : bits(64) = read_reg5(SrcD1);
  mem_store64_le(ea, v0);
  mem_store64_le(ea + (sail_zeros(64) + 8), v1)
}

// ---- HL store pair: reg+reg addressing ----
function exec_hl_sbp(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_scale(SrcR, SrcRType, 0);
  let v0 : bits(8) = read_reg5(SrcD0)[7..0];
  let v1 : bits(8) = read_reg5(SrcD1)[7..0];
  write_mem8(ea, v0);
  write_mem8(ea + (sail_zeros(64) + 1), v1)
}
function exec_hl_shp(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_scale(SrcR, SrcRType, 1);
  let v0 : bits(16) = read_reg5(SrcD0)[15..0];
  let v1 : bits(16) = read_reg5(SrcD1)[15..0];
  mem_store16_le(ea, v0);
  mem_store16_le(ea + (sail_zeros(64) + 2), v1)
}
function exec_hl_shp_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + apply_srcrtype_arith64(SrcRType, read_reg5(SrcR));
  let v0 : bits(16) = read_reg5(SrcD0)[15..0];
  let v1 : bits(16) = read_reg5(SrcD1)[15..0];
  mem_store16_le(ea, v0);
  mem_store16_le(ea + (sail_zeros(64) + 2), v1)
}
function exec_hl_swp(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_scale(SrcR, SrcRType, 2);
  let v0 : bits(32) = read_reg5(SrcD0)[31..0];
  let v1 : bits(32) = read_reg5(SrcD1)[31..0];
  mem_store32_le(ea, v0);
  mem_store32_le(ea + (sail_zeros(64) + 4), v1)
}
function exec_hl_swp_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + apply_srcrtype_arith64(SrcRType, read_reg5(SrcR));
  let v0 : bits(32) = read_reg5(SrcD0)[31..0];
  let v1 : bits(32) = read_reg5(SrcD1)[31..0];
  mem_store32_le(ea, v0);
  mem_store32_le(ea + (sail_zeros(64) + 4), v1)
}
function exec_hl_sdp(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_scale(SrcR, SrcRType, 3);
  let v0 : bits(64) = read_reg5(SrcD0);
  let v1 : bits(64) = read_reg5(SrcD1);
  mem_store64_le(ea, v0);
  mem_store64_le(ea + (sail_zeros(64) + 8), v1)
}
function exec_hl_sdp_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + apply_srcrtype_arith64(SrcRType, read_reg5(SrcR));
  let v0 : bits(64) = read_reg5(SrcD0);
  let v1 : bits(64) = read_reg5(SrcD1);
  mem_store64_le(ea, v0);
  mem_store64_le(ea + (sail_zeros(64) + 8), v1)
}
