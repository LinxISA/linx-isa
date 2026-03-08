// LinxISA execute semantics for the canonical v0.4 model.

// This file holds the live execute semantics used by the strict v0.4 Sail gate.
// Coverage is incomplete in some units, but active mnemonics are tracked in
// semantics_status.json rather than via staged placeholder wording here.

// NOTE: Baseline policy (per user): implement semantics according to the
// current manual + golden, and leave ambiguous behavior unimplemented until
// confirmed.

// State and common helpers are provided by the top-level model entry.

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
  let r = sub_bits(a, b);
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
  let r = xor_vec(a, b);
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
  write_regdst(RegDst, sub_bits(a, imm))
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
  write_regdst(RegDst, xor_vec(a, imm))
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
  let r : bits(32) = sub_bits(a, b);
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
  let r : bits(32) = xor_vec(a, b);
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
  let r : bits(32) = sub_bits(a, imm);
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
  write_regdst(RegDst, sub_bits(a, imm))
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
  let r : bits(32) = sub_bits(a, imm);
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
  write_regdst(RegDst, sub_bits(a, sail_zeros(64) + prod))
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
  let r : bits(32) = xor_vec(a, imm);
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
  write_regdst(reg_t(), sub_bits(a, b))
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
  write_regdst(RegDst, xor_vec(a, imm))
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
  let r32 : bits(32) = xor_vec(a32, imm32);
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
  if x[63] == 0b1 then not_vec(x) else xor_vec(x, 0x8000_0000_0000_0000)
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
  if x[31] == 0b1 then not_vec(x) else xor_vec(x, 0x8000_0000)
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

function fp32_is_snan(x : bits(32)) -> bool = {
  let exp : bits(8) = x[30..23];
  let frac : bits(23) = x[22..0];
  (exp == (sail_zeros(8) + 255)) & (frac != sail_zeros(23)) & (frac[22] == 0b0)
}

function fp64_is_snan(x : bits(64)) -> bool = {
  let exp : bits(11) = x[62..52];
  let frac : bits(52) = x[51..0];
  (exp == (sail_zeros(11) + 2047)) & (frac != sail_zeros(52)) & (frac[51] == 0b0)
}

function fp32_class_mask(x : bits(32)) -> bits(32) = {
  let exp : bits(8) = x[30..23];
  let frac : bits(23) = x[22..0];
  let sign : bits(1) = x[31];
  if (exp == sail_zeros(8)) & (frac == sail_zeros(23)) then {
    if sign == 0b1 then 0x0000_0008 else 0x0000_0010
  } else if exp == sail_zeros(8) then {
    if sign == 0b1 then 0x0000_0004 else 0x0000_0020
  } else if (exp == (sail_zeros(8) + 255)) & (frac == sail_zeros(23)) then {
    if sign == 0b1 then 0x0000_0001 else 0x0000_0080
  } else if exp == (sail_zeros(8) + 255) then {
    if fp32_is_snan(x) then 0x0000_0100 else 0x0000_0200
  } else {
    if sign == 0b1 then 0x0000_0002 else 0x0000_0040
  }
}

function fp64_class_mask(x : bits(64)) -> bits(32) = {
  let exp : bits(11) = x[62..52];
  let frac : bits(52) = x[51..0];
  let sign : bits(1) = x[63];
  if (exp == sail_zeros(11)) & (frac == sail_zeros(52)) then {
    if sign == 0b1 then 0x0000_0008 else 0x0000_0010
  } else if exp == sail_zeros(11) then {
    if sign == 0b1 then 0x0000_0004 else 0x0000_0020
  } else if (exp == (sail_zeros(11) + 2047)) & (frac == sail_zeros(52)) then {
    if sign == 0b1 then 0x0000_0001 else 0x0000_0080
  } else if exp == (sail_zeros(11) + 2047) then {
    if fp64_is_snan(x) then 0x0000_0100 else 0x0000_0200
  } else {
    if sign == 0b1 then 0x0000_0002 else 0x0000_0040
  }
}

val linx_fp_add = pure "linx_fp_add" : (bits(3), bits(5), bits(64), bits(64)) -> (bits(64), bits(5))
val linx_fp_sub = pure "linx_fp_sub" : (bits(3), bits(5), bits(64), bits(64)) -> (bits(64), bits(5))
val linx_fp_mul = pure "linx_fp_mul" : (bits(3), bits(5), bits(64), bits(64)) -> (bits(64), bits(5))
val linx_fp_div = pure "linx_fp_div" : (bits(3), bits(5), bits(64), bits(64)) -> (bits(64), bits(5))
val linx_fp_sqrt = pure "linx_fp_sqrt" : (bits(3), bits(5), bits(64)) -> (bits(64), bits(5))
val linx_fp_recip = pure "linx_fp_recip" : (bits(3), bits(5), bits(64)) -> (bits(64), bits(5))
val linx_fp_exp = pure "linx_fp_exp" : (bits(3), bits(5), bits(64)) -> (bits(64), bits(5))
val linx_fp_fmadd = pure "linx_fp_fmadd" : (bits(3), bits(5), bits(64), bits(64), bits(64)) -> (bits(64), bits(5))
val linx_fp_fmsub = pure "linx_fp_fmsub" : (bits(3), bits(5), bits(64), bits(64), bits(64)) -> (bits(64), bits(5))
val linx_fp_fnmadd = pure "linx_fp_fnmadd" : (bits(3), bits(5), bits(64), bits(64), bits(64)) -> (bits(64), bits(5))
val linx_fp_fnmsub = pure "linx_fp_fnmsub" : (bits(3), bits(5), bits(64), bits(64), bits(64)) -> (bits(64), bits(5))
val linx_fp_to_fp = pure "linx_fp_to_fp" : (bits(3), bits(5), bits(5), bits(64)) -> (bits(64), bits(5))
val linx_fp_to_int = pure "linx_fp_to_int" : (bits(3), bits(5), bits(5), bits(64)) -> (bits(64), bits(5))
val linx_int_to_fp = pure "linx_int_to_fp" : (bits(3), bits(5), bits(5), bits(64)) -> (bits(64), bits(5))

function fp_active_rm() -> bits(3) = {
  let frm = cstate_get_frm();
  if unsigned(frm) <= 4 then frm else 0b000
}

function vec_fp_from_carrier32(carrier : bits(32), src_t : bits(5)) -> (bits(64), bits(5)) = {
  if src_t == 0b00001 then {
    (zext32_from32(carrier), 0b00000)
  } else {
    linx_fp_to_fp(fp_active_rm(), src_t, 0b00001, zext32_from32(carrier))
  }
}

function vec_fp_to_carrier32(raw : bits(64), src_t : bits(5)) -> (bits(32), bits(5)) = {
  if src_t == 0b00001 then {
    (raw[31..0], 0b00000)
  } else {
    let (carrier, flags) = linx_fp_to_fp(fp_active_rm(), 0b00001, src_t, raw);
    (carrier[31..0], flags)
  }
}

function vec_fp_result_to_carrier32(raw : bits(64), src_t : bits(5), dst_t : bits(5)) -> (bits(32), bits(5)) = {
  if dst_t == src_t then {
    vec_fp_to_carrier32(raw, dst_t)
  } else {
    let (dst_raw, flags0) = linx_fp_to_fp(fp_active_rm(), dst_t, src_t, raw);
    let (carrier, flags1) = vec_fp_to_carrier32(dst_raw, dst_t);
    (carrier, flags0 | flags1)
  }
}

function vec_fp_to_fp64_norm(carrier : bits(32), src_t : bits(5)) -> (bits(64), bits(5)) = {
  let (typed, flags0) = vec_fp_from_carrier32(carrier, src_t);
  if src_t == 0b00000 then {
    (typed, flags0)
  } else {
    let (norm, flags1) = linx_fp_to_fp(fp_active_rm(), 0b00000, src_t, typed);
    (norm, flags0 | flags1)
  }
}

function vec_fp_qnan_in_type(src_t : bits(5)) -> (bits(64), bits(5)) = {
  if src_t == 0b00000 then {
    (0x7FF8_0000_0000_0000, 0b00000)
  } else if src_t == 0b00001 then {
    (0x0000_0000_7FC0_0000, 0b00000)
  } else {
    linx_fp_to_fp(fp_active_rm(), src_t, 0b00000, 0x7FF8_0000_0000_0000)
  }
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
// Floating-point arithmetic (FSU)
//
// Architectural contract:
// - `SrcType` selects scalar FP source width: `0=FP64`, `1=FP32`; all other
//   encodings are illegal for the scalar FSU forms.
// - `DstType` for convert-class ops uses the canonical floating/integer type
//   tables from chapter 05c.
// - `CSTATE.FRM` selects the active rounding mode and `CSTATE.FFLAGS` is the
//   sticky IEEE-754 flag mirror used by the current bring-up profile.
// - Narrow FP results are written into the low bits of the destination GPR and
//   zero-extended to 64 bits.
//
// Numeric behavior is delegated to typed helper hooks so the Sail model can
// carry architecturally precise inputs/outputs/flag effects without hard-coding
// one host FP implementation into the source.

function fp_record_flags(flags : bits(5)) -> unit = {
  cstate_or_fflags(flags)
}

function scalar_fp_type_code(SrcType : bits(2)) -> bits(5) = {
  if SrcType == 0b00 then 0b00000
  else if SrcType == 0b01 then 0b00001
  else 0b11111
}

function scalar_signed_int_type_code(SrcType : bits(2)) -> bits(5) = {
  if SrcType == 0b00 then 0b01000
  else if SrcType == 0b01 then 0b01001
  else 0b11111
}

function scalar_unsigned_int_type_code(SrcType : bits(2)) -> bits(5) = {
  if SrcType == 0b00 then 0b00000
  else if SrcType == 0b01 then 0b00001
  else 0b11111
}

function fp_type_code_supported(t : bits(5)) -> bool = {
  unsigned(t) <= 14
}

function int_type_code_supported(t : bits(5)) -> bool = {
  unsigned(t) <= 14
}

function int_type_width(t : bits(5)) -> int = {
  if t == 0b00000 | t == 0b01000 then 64
  else if t == 0b00001 | t == 0b01001 then 32
  else if t == 0b00010 | t == 0b01010 then 16
  else if t == 0b00011 | t == 0b01011 then 8
  else if t == 0b00100 | t == 0b01100 then 4
  else if t == 0b00101 | t == 0b01101 then 2
  else if t == 0b00110 | t == 0b00111 | t == 0b01110 then 1
  else 0
}

function float_type_width(t : bits(5)) -> int = {
  if t == 0b00000 then 64
  else if t == 0b00001 | t == 0b00011 then 32
  else if t == 0b00010 then 19
  else if t == 0b00100 | t == 0b00101 then 16
  else if t == 0b00110 | t == 0b00111 | t == 0b01000 | t == 0b01101 then 8
  else if t == 0b01001 | t == 0b01010 then 6
  else if t == 0b01011 | t == 0b01100 then 4
  else if t == 0b01110 then 9
  else 0
}

function fp_scalar_value(raw : bits(64), fp_type : bits(5)) -> bits(64) = {
  if fp_type == 0b00001 then zext32_from32(raw[31..0]) else raw
}

function scalar_int_value(raw : bits(64), int_type : bits(5)) -> bits(64) = {
  if int_type == 0b00001 then zext32_from32(raw[31..0])
  else if int_type == 0b01001 then sext32_from32(raw[31..0])
  else raw
}

function fp_write_result(RegDst : bits(5), result : bits(64), flags : bits(5)) -> unit = {
  fp_record_flags(flags);
  write_regdst(RegDst, result)
}

function pack_low_bits_into_lane32(value : bits(64), width : int) -> bits(32) = {
  if width == 32 then value[31..0]
  else if width == 19 then sail_zeros(13) @ value[18..0]
  else if width == 16 then sail_zeros(16) @ value[15..0]
  else if width == 9 then sail_zeros(23) @ value[8..0]
  else if width == 8 then sail_zeros(24) @ value[7..0]
  else if width == 6 then sail_zeros(26) @ value[5..0]
  else if width == 4 then sail_zeros(28) @ value[3..0]
  else 0x0000_0000
}

function pack_low_int_bits_into_lane32(value : bits(64), width : int) -> bits(32) = {
  if width >= 32 then value[31..0]
  else if width == 16 then sail_zeros(16) @ value[15..0]
  else if width == 8 then sail_zeros(24) @ value[7..0]
  else if width == 4 then sail_zeros(28) @ value[3..0]
  else if width == 2 then sail_zeros(30) @ value[1..0]
  else if width == 1 then sail_zeros(31) @ value[0..0]
  else 0x0000_0000
}

function int_type_is_signed(t : bits(5)) -> bool = {
  unsigned(t) >= 8
}

function mask_low_n64(n : int) -> bits(64) = {
  let ones : bits(64) = 0xFFFF_FFFF_FFFF_FFFF;
  if n >= 64 then ones
  else sail_shiftright(ones, 64 - n)
}

function low_n64(x : bits(64), n : int) -> bits(64) = {
  if n >= 64 then x else x & mask_low_n64(n)
}

function sext_low_n64(field : bits(64), n : int) -> bits(64) = {
  if n >= 64 then field
  else {
    let sign1 : bits(64) = sail_shiftright(field, n - 1);
    let sign : bits(1) = sign1[0..0];
    let low : bits(64) = low_n64(field, n);
    if sign == 0b1 then (low | (not_vec(mask_low_n64(n)))) else low
  }
}

function vec_int_effective_width(t : bits(5)) -> int = {
  let w : int = int_type_width(t);
  if w == 0 then 32 else w
}

function vec_int_bits_from_carrier32(carrier : bits(32), t : bits(5)) -> bits(64) = {
  let w : int = vec_int_effective_width(t);
  let base : bits(64) = zext32_from32(carrier);
  if w > 32 then base else low_n64(base, w)
}

function vec_int_numeric_from_carrier32(carrier : bits(32), t : bits(5)) -> bits(64) = {
  let w : int = vec_int_effective_width(t);
  let base : bits(64) = zext32_from32(carrier);
  if int_type_is_signed(t) then {
    if w > 32 then sext_low_n64(base, 32) else sext_low_n64(base, w)
  } else {
    if w > 32 then base else low_n64(base, w)
  }
}

function vec_int_bits_from_value64(value : bits(64), t : bits(5)) -> bits(64) = {
  let w : int = vec_int_effective_width(t);
  if w >= 64 then value else low_n64(value, w)
}

function vec_int_numeric_from_value64(value : bits(64), t : bits(5)) -> bits(64) = {
  let w : int = vec_int_effective_width(t);
  if int_type_is_signed(t) then {
    if w >= 64 then value else sext_low_n64(value, w)
  } else {
    if w >= 64 then value else low_n64(value, w)
  }
}

function vec_int_pack_carrier32(value : bits(64), t : bits(5)) -> bits(32) = {
  pack_low_int_bits_into_lane32(value, vec_int_effective_width(t))
}

function vec_int_shift_amount(carrier : bits(32), t : bits(5)) -> int = {
  let width : int = vec_int_effective_width(t);
  if width <= 1 then 0
  else tmod_int(unsigned(carrier[5..0]), if width > 64 then 64 else width)
}

function exec_fadd(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_add(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t), fp_scalar_value(read_reg5(SrcR), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fsub(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_sub(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t), fp_scalar_value(read_reg5(SrcR), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fmul(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_mul(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t), fp_scalar_value(read_reg5(SrcR), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fdiv(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_div(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t), fp_scalar_value(read_reg5(SrcR), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fsqrt(RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_sqrt(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_frecip(RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_recip(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fexp(RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_exp(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fmadd(RegDst : bits(5), SrcA : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_fmadd(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t), fp_scalar_value(read_reg5(SrcR), fp_t), fp_scalar_value(read_reg5(SrcA), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fmsub(RegDst : bits(5), SrcA : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_fmsub(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t), fp_scalar_value(read_reg5(SrcR), fp_t), fp_scalar_value(read_reg5(SrcA), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fnmadd(RegDst : bits(5), SrcA : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_fnmadd(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t), fp_scalar_value(read_reg5(SrcR), fp_t), fp_scalar_value(read_reg5(SrcA), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fnmsub(RegDst : bits(5), SrcA : bits(5), SrcL : bits(5), SrcR : bits(5), SrcType : bits(2)) -> unit = {
  let fp_t = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(fp_t)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_fnmsub(fp_active_rm(), fp_t, fp_scalar_value(read_reg5(SrcL), fp_t), fp_scalar_value(read_reg5(SrcR), fp_t), fp_scalar_value(read_reg5(SrcA), fp_t));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fcvt(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let src_fp_type = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(src_fp_type) & fp_type_code_supported(DstType)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_to_fp(fp_active_rm(), DstType, src_fp_type, fp_scalar_value(read_reg5(SrcL), src_fp_type));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fcvta(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let src_fp_type = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(src_fp_type) & int_type_code_supported(DstType)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_to_int(0b100, DstType, src_fp_type, fp_scalar_value(read_reg5(SrcL), src_fp_type));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fcvtm(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let src_fp_type = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(src_fp_type) & int_type_code_supported(DstType)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_to_int(0b001, DstType, src_fp_type, fp_scalar_value(read_reg5(SrcL), src_fp_type));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fcvtn(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let src_fp_type = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(src_fp_type) & int_type_code_supported(DstType)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_to_int(0b000, DstType, src_fp_type, fp_scalar_value(read_reg5(SrcL), src_fp_type));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fcvtp(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let src_fp_type = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(src_fp_type) & int_type_code_supported(DstType)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_to_int(0b010, DstType, src_fp_type, fp_scalar_value(read_reg5(SrcL), src_fp_type));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_fcvtz(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let src_fp_type = scalar_fp_type_code(SrcType);
  if not_bool(fp_type_code_supported(src_fp_type) & int_type_code_supported(DstType)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_fp_to_int(0b011, DstType, src_fp_type, fp_scalar_value(read_reg5(SrcL), src_fp_type));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_scvtf(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let src_int_type = scalar_signed_int_type_code(SrcType);
  if not_bool(int_type_code_supported(src_int_type) & fp_type_code_supported(DstType)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_int_to_fp(fp_active_rm(), src_int_type, DstType, scalar_int_value(read_reg5(SrcL), src_int_type));
    fp_write_result(RegDst, result, flags)
  }
}

function exec_ucvtf(DstType : bits(5), RegDst : bits(5), SrcL : bits(5), SrcType : bits(2)) -> unit = {
  let src_int_type = scalar_unsigned_int_type_code(SrcType);
  if not_bool(int_type_code_supported(src_int_type) & fp_type_code_supported(DstType)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let (result, flags) = linx_int_to_fp(fp_active_rm(), src_int_type, DstType, scalar_int_value(read_reg5(SrcL), src_int_type));
    fp_write_result(RegDst, result, flags)
  }
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
  let sp1 : bits(64) = sub_bits(sp0, sail_zeros(64) + frame);
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
// The precise external format is profile-defined. The Sail model writes and restores
// a minimal architectural snapshot through the canonical EBARG_EXTCTX pointer/meta
// registers so ESAVE/ERCOV are executable and testable.
function exec_esave(RegSrc0 : bits(5), RegSrc1 : bits(5), RegSrc2 : bits(5)) -> unit = {
  let cur_acr : bits(4) = current_acr_id();
  let base : bits(64) = read_reg5(RegSrc0);
  let kind : bits(64) = read_reg5(RegSrc1);
  let len  : bits(64) = read_reg5(RegSrc2);
  write_ebarg_extctx_ptr_for_acr(cur_acr, base);
  write_ebarg_extctx_meta_for_acr(cur_acr, sail_shiftleft((kind & 0x0000_0000_FFFF_FFFF), 32) | (len & 0x0000_0000_FFFF_FFFF));
  if unsigned(len) >= 8 then mem_store64_le(base + 0x0000_0000_0000_0000, ssr_cstate) else ();
  if unsigned(len) >= 16 then mem_store64_le(base + 0x0000_0000_0000_0008, pc) else ();
  if unsigned(len) >= 24 then mem_store64_le(base + 0x0000_0000_0000_0010, tpc) else ();
  if unsigned(len) >= 32 then mem_store64_le(base + 0x0000_0000_0000_0018, barg_bpc_cur) else ();
  if unsigned(len) >= 40 then mem_store64_le(base + 0x0000_0000_0000_0020, barg_bpc_tgt) else ();
  if unsigned(len) >= 48 then mem_store64_le(base + 0x0000_0000_0000_0028, barg_carg) else ()
}

function exec_ercov(RegSrc0 : bits(5), RegSrc1 : bits(5), RegSrc2 : bits(5)) -> unit = {
  let _ = RegSrc1;
  let cur_acr : bits(4) = current_acr_id();
  let base0 : bits(64) = read_reg5(RegSrc0);
  let base : bits(64) = if base0 == 0x0000_0000_0000_0000 then read_ebarg_extctx_ptr_for_acr(cur_acr) else base0;
  let len0 : bits(64) = read_reg5(RegSrc2);
  let meta : bits(64) = read_ebarg_extctx_meta_for_acr(cur_acr);
  let len  : bits(64) = if len0 == 0x0000_0000_0000_0000 then (sail_zeros(32) @ meta[31..0]) else len0;
  if unsigned(len) >= 8 then ssr_cstate = mem_load64_le(base + 0x0000_0000_0000_0000) else ();
  if unsigned(len) >= 16 then pc = mem_load64_le(base + 0x0000_0000_0000_0008) else ();
  if unsigned(len) >= 24 then tpc = mem_load64_le(base + 0x0000_0000_0000_0010) else ();
  if unsigned(len) >= 32 then barg_bpc_cur = mem_load64_le(base + 0x0000_0000_0000_0018) else ();
  if unsigned(len) >= 40 then barg_bpc_tgt = mem_load64_le(base + 0x0000_0000_0000_0020) else ();
  if unsigned(len) >= 48 then barg_carg = mem_load64_le(base + 0x0000_0000_0000_0028) else ();
  barg_valid = true
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
  let cur_acr : bits(4) = current_acr_id();
  let ecstate : bits(64) = (ssr_cstate & 0xFFFF_FFFF_FFFF_FFE0) | sail_zero_extend(cur_acr, 64) | 0x0000_0000_0000_0010;
  write_ecstate_for_acr(cur_acr, ecstate);
  write_ebarg_bpc_cur_for_acr(cur_acr, barg_bpc_cur);
  write_ebarg_bpc_tgt_for_acr(cur_acr, barg_bpc_tgt);
  write_ebarg_tpc_for_acr(cur_acr, tpc);
  let trapnum = (sail_zeros(6) + 6); // SCALL
  let cause : bits(24) = sail_zero_extend(RST_Type, 24);
  raise_trap(trapnum, cause, read_pc_or_tpc(), 0b1)
}

// `ACRE`: ACR enter request taken at block commit in the full model.
// The Sail bring-up model restores the architecturally visible CSTATE/BPC/TPC/EXTCTX
// subset from the active manager-bank shadows.
function exec_acre(RRA_Type : bits(4)) -> unit = {
  let cur_acr : bits(4) = current_acr_id();
  let ecstate : bits(64) = read_ecstate_for_acr(cur_acr);
  let target_acr : bits(4) = ecstate_target_acr(ecstate);
  if not_bool((RRA_Type == 0x0) | (RRA_Type == 0x1)) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else if not_bool(unsigned(target_acr) >= unsigned(cur_acr)) then {
    trap_e_inst(0x02, 0x00, read_pc_or_tpc())
  } else {
    ssr_cstate = ecstate;
    barg_valid = true;
    barg_bpc_cur = read_ebarg_bpc_cur_for_acr(cur_acr);
    barg_bpc_tgt = read_ebarg_bpc_tgt_for_acr(cur_acr);
    if ecstate_bi(ecstate) then {
      pc = barg_bpc_cur;
      tpc = read_ebarg_tpc_for_acr(cur_acr)
    } else {
      pc = barg_bpc_cur;
      tpc = barg_bpc_cur
    };
    if RRA_Type == 0x1 then {
      let ext_base : bits(64) = read_ebarg_extctx_ptr_for_acr(cur_acr);
      let ext_meta : bits(64) = read_ebarg_extctx_meta_for_acr(cur_acr);
      let ext_len : bits(64) = sail_zeros(32) @ ext_meta[31..0];
      if ext_base != 0x0000_0000_0000_0000 then {
        if unsigned(ext_len) >= 8 then ssr_cstate = mem_load64_le(ext_base + 0x0000_0000_0000_0000) else ();
        if unsigned(ext_len) >= 16 then pc = mem_load64_le(ext_base + 0x0000_0000_0000_0008) else ();
        if unsigned(ext_len) >= 24 then tpc = mem_load64_le(ext_base + 0x0000_0000_0000_0010) else ();
        if unsigned(ext_len) >= 32 then barg_bpc_cur = mem_load64_le(ext_base + 0x0000_0000_0000_0018) else ();
        if unsigned(ext_len) >= 40 then barg_bpc_tgt = mem_load64_le(ext_base + 0x0000_0000_0000_0020) else ();
        if unsigned(ext_len) >= 48 then barg_carg = mem_load64_le(ext_base + 0x0000_0000_0000_0028) else ()
      } else ()
    } else ()
  }
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

function tlb_is_unprivileged_manager() -> bool = {
  ssr_cstate[3..0] == 0x2
}

function exec_tlb_iv(SrcL : bits(5)) -> unit = {
  let va = read_reg5(SrcL);
  if tlb_is_unprivileged_manager() then {
    trap_e_inst(0x03, 0x01, read_pc_or_tpc())
  } else if not_bool(is_canonical_va48(va)) then {
    trap_data_page_fault(va)
  } else {
    ()
  }
}

function exec_tlb_iav(SrcL : bits(5)) -> unit = {
  let va = read_reg5(SrcL);
  if tlb_is_unprivileged_manager() then {
    trap_e_inst(0x03, 0x01, read_pc_or_tpc())
  } else if not_bool(is_canonical_va48(va)) then {
    trap_data_page_fault(va)
  } else {
    ()
  }
}

function exec_tlb_ia(SrcL : bits(5)) -> unit = {
  let x = read_reg5(SrcL);
  if tlb_is_unprivileged_manager() then {
    trap_e_inst(0x03, 0x01, read_pc_or_tpc())
  } else if x[63..16] != 0x0000_0000_0000 then {
    // Manual: SrcL[63:16] must be zero.
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    ()
  }
}

function exec_tlb_iall() -> unit = {
  if tlb_is_unprivileged_manager() then trap_e_inst(0x03, 0x01, read_pc_or_tpc()) else ()
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
function exec_b_ior() -> unit = {
  let src0 : bits(5) = decoded_bior_regsrc0();
  let src1 : bits(5) = decoded_bior_regsrc1();
  let src2 : bits(5) = decoded_bior_regsrc2();
  let _dst : bits(5) = decoded_bior_regdst();
  // Live v0.4 bring-up follows the shipped LLVM/QEMU ordering for ri* capture:
  // RegSrc1, then RegSrc0, then RegSrc2; zero-valued GPR slots are skipped.
  if src1 != 0b00000 then allocate_ri_binding(src1) else ();
  if src0 != 0b00000 then allocate_ri_binding(src0) else ();
  if src2 != 0b00000 then allocate_ri_binding(src2) else ();
  bdesc_mark_ior()
}
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

function exec_v_add(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r64 : bits(64) = vec_int_bits_from_carrier32(a, srcl_t) + vec_int_bits_from_carrier32(b, srcr_t);
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_sub(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r64 : bits(64) = sub_bits(vec_int_bits_from_carrier32(a, srcl_t), vec_int_bits_from_carrier32(b, srcr_t));
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_and(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r64 : bits(64) = vec_int_bits_from_carrier32(a, srcl_t) & vec_int_bits_from_carrier32(b, srcr_t);
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_or(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r64 : bits(64) = vec_int_bits_from_carrier32(a, srcl_t) | vec_int_bits_from_carrier32(b, srcr_t);
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_xor(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r64 : bits(64) = xor_vec(vec_int_bits_from_carrier32(a, srcl_t), vec_int_bits_from_carrier32(b, srcr_t));
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

// Immediate forms: operate on 32-bit lanes with sign/zero extension per form.
function exec_v_addi(SrcL_k : bits(5), uimm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let imm : bits(64) = sail_zero_extend(uimm12, 64);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let r64 : bits(64) = vec_int_bits_from_carrier32(a, srcl_t) + vec_int_bits_from_value64(imm, srcl_t);
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_subi(SrcL_k : bits(5), uimm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let imm : bits(64) = sail_zero_extend(uimm12, 64);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let r64 : bits(64) = sub_bits(vec_int_bits_from_carrier32(a, srcl_t), vec_int_bits_from_value64(imm, srcl_t));
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_andi(SrcL_k : bits(5), simm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let imm : bits(64) = sext12_to64(simm12);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let r64 : bits(64) = vec_int_bits_from_carrier32(a, srcl_t) & vec_int_bits_from_value64(imm, srcl_t);
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_ori(SrcL_k : bits(5), simm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let imm : bits(64) = sext12_to64(simm12);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let r64 : bits(64) = vec_int_bits_from_carrier32(a, srcl_t) | vec_int_bits_from_value64(imm, srcl_t);
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_xori(SrcL_k : bits(5), simm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let imm : bits(64) = sext12_to64(simm12);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let r64 : bits(64) = xor_vec(vec_int_bits_from_carrier32(a, srcl_t), vec_int_bits_from_value64(imm, srcl_t));
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

// Compare ops: write lane predicate values (0 or 1).
function vec_bool32(b : bool) -> bits(32) = { if b then 0x0000_0001 else 0x0000_0000 }

function exec_v_cmp_eq(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let eq : bool = vec_int_bits_from_carrier32(a, srcl_t) == vec_int_bits_from_carrier32(b, srcr_t);
    let r : bits(32) = if active then vec_bool32(eq) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_ne(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let ne : bool = vec_int_bits_from_carrier32(a, srcl_t) != vec_int_bits_from_carrier32(b, srcr_t);
    let r : bits(32) = if active then vec_bool32(ne) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_lt(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(signed(vec_int_numeric_from_carrier32(a, srcl_t)) < signed(vec_int_numeric_from_carrier32(b, srcr_t))) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_ge(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(signed(vec_int_numeric_from_carrier32(a, srcl_t)) >= signed(vec_int_numeric_from_carrier32(b, srcr_t))) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_ltu(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(unsigned(vec_int_bits_from_carrier32(a, srcl_t)) < unsigned(vec_int_bits_from_carrier32(b, srcr_t))) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_geu(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let b = vec_get_lane32(rhs, i);
    let r : bits(32) = if active then vec_bool32(unsigned(vec_int_bits_from_carrier32(a, srcl_t)) >= unsigned(vec_int_bits_from_carrier32(b, srcr_t))) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

// Compare immediate forms.
function exec_v_cmp_eqi(SrcL_k : bits(5), simm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let imm : bits(64) = sext12_to64(simm12);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(vec_int_bits_from_carrier32(a, srcl_t) == vec_int_bits_from_value64(imm, srcl_t)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_nei(SrcL_k : bits(5), simm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let imm : bits(64) = sext12_to64(simm12);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(vec_int_bits_from_carrier32(a, srcl_t) != vec_int_bits_from_value64(imm, srcl_t)) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_lti(SrcL_k : bits(5), simm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let imm : bits(64) = sext12_to64(simm12);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(signed(vec_int_numeric_from_carrier32(a, srcl_t)) < signed(vec_int_numeric_from_value64(imm, srcl_t))) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_gei(SrcL_k : bits(5), simm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let imm : bits(64) = sext12_to64(simm12);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(signed(vec_int_numeric_from_carrier32(a, srcl_t)) >= signed(vec_int_numeric_from_value64(imm, srcl_t))) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_ltui(SrcL_k : bits(5), uimm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let imm : bits(64) = sail_zero_extend(uimm12, 64);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(unsigned(vec_int_bits_from_carrier32(a, srcl_t)) < unsigned(vec_int_bits_from_value64(imm, srcl_t))) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

function exec_v_cmp_geui(SrcL_k : bits(5), uimm12 : bits(12), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let imm : bits(64) = sail_zero_extend(uimm12, 64);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a = vec_get_lane32(lhs, i);
    let r : bits(32) = if active then vec_bool32(unsigned(vec_int_bits_from_carrier32(a, srcl_t)) >= unsigned(vec_int_bits_from_value64(imm, srcl_t))) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  }; write_vt(Dst_k, out)
}

// Boolean combines (treat non-zero as true; produce 0/1).
function exec_v_cmp_and(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
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

function exec_v_cmp_or(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
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

function exec_v_cmp_andi(SrcL_k : bits(5), simm12 : bits(12), Dst_k : bits(5)) -> unit = {
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

function exec_v_cmp_ori(SrcL_k : bits(5), simm12 : bits(12), Dst_k : bits(5)) -> unit = {
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
function exec_v_csel(SrcP_k : bits(5), SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
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
function exec_v_bcnt(SrcL_k : bits(5), Nminus1 : bits(6), M : bits(6), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let dst_t : bits(5) = decoded_vec_dst_type();
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
    let r : bits(32) = if active then vec_int_pack_carrier32(sail_zeros(64) + c, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_clz(SrcL_k : bits(5), Nminus1 : bits(6), M : bits(6), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let dst_t : bits(5) = decoded_vec_dst_type();
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
    let r : bits(32) = if active then vec_int_pack_carrier32(sail_zeros(64) + c, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_ctz(SrcL_k : bits(5), Nminus1 : bits(6), M : bits(6), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let dst_t : bits(5) = decoded_vec_dst_type();
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
    let r : bits(32) = if active then vec_int_pack_carrier32(sail_zeros(64) + c, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_bxu(SrcL_k : bits(5), Nminus1 : bits(6), M : bits(6), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let dst_t : bits(5) = decoded_vec_dst_type();
  let n0 : int = unsigned(Nminus1) + 1;
  let n : int = if n0 > 32 then 32 else n0;
  let m : int = unsigned(M);
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let x : bits(32) = vec_get_lane32(lhs, i);
    let f : bits(32) = bitfield_wrap32(x, m, n);
    let r : bits(32) = if active then vec_int_pack_carrier32(zext32_from32(f), dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_bxs(SrcL_k : bits(5), Nminus1 : bits(6), M : bits(6), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let dst_t : bits(5) = decoded_vec_dst_type();
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
    let r : bits(32) = if active then vec_int_pack_carrier32(zext32_from32(sx), dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_bic(SrcL_k : bits(5), Nminus1 : bits(6), M : bits(6), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let dst_t : bits(5) = decoded_vec_dst_type();
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
    let r : bits(32) = if active then vec_int_pack_carrier32(zext32_from32(y), dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_bis(SrcL_k : bits(5), Nminus1 : bits(6), M : bits(6), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let dst_t : bits(5) = decoded_vec_dst_type();
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
    let r : bits(32) = if active then vec_int_pack_carrier32(zext32_from32(y), dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

// For V.BXU/BXS we already use the bitfield wrap helpers above.

function exec_v_div(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let ai : int = signed(vec_int_numeric_from_carrier32(a, srcl_t));
    let bi : int = signed(vec_int_numeric_from_carrier32(b, srcr_t));
    let qi : int = if b == 0x0000_0000 then 0 else (tdiv_int(ai, bi));
    let r : bits(32) = if active then vec_int_pack_carrier32(sail_zeros(64) + qi, dst_t) else undefined_bitvector(32);
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

function exec_v_mul(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let prod : int = unsigned(vec_int_bits_from_carrier32(a, srcl_t)) * unsigned(vec_int_bits_from_carrier32(b, srcr_t));
    let r : bits(32) = if active then vec_int_pack_carrier32(sail_zeros(64) + prod, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_madd(SrcL_k : bits(5), SrcR_k : bits(5), SrcD_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let add = read_vt(SrcD_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let srca_t : bits(5) = decoded_vec_srca_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let d : bits(32) = vec_get_lane32(add, i);
    let prod : int = unsigned(vec_int_bits_from_carrier32(a, srcl_t)) * unsigned(vec_int_bits_from_carrier32(b, srcr_t));
    let sum  : int = prod + unsigned(vec_int_bits_from_carrier32(d, srca_t));
    let r : bits(32) = if active then vec_int_pack_carrier32(sail_zeros(64) + sum, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_max(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r64 : bits(64) = if signed(vec_int_numeric_from_carrier32(a, srcl_t)) >= signed(vec_int_numeric_from_carrier32(b, srcr_t))
      then vec_int_numeric_from_carrier32(a, srcl_t)
      else vec_int_numeric_from_carrier32(b, srcr_t);
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_min(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let r64 : bits(64) = if signed(vec_int_numeric_from_carrier32(a, srcl_t)) <= signed(vec_int_numeric_from_carrier32(b, srcr_t))
      then vec_int_numeric_from_carrier32(a, srcl_t)
      else vec_int_numeric_from_carrier32(b, srcr_t);
    let r : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_rem(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let lhs = read_vt(SrcL_k);
  let rhs = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let a : bits(32) = vec_get_lane32(lhs, i);
    let b : bits(32) = vec_get_lane32(rhs, i);
    let ai : int = signed(vec_int_numeric_from_carrier32(a, srcl_t));
    let bi : int = signed(vec_int_numeric_from_carrier32(b, srcr_t));
    let ri : int = if b == 0x0000_0000 then ai else (ai - (tdiv_int(ai, bi) * bi));
    let r : bits(32) = if active then vec_int_pack_carrier32(sail_zeros(64) + ri, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_rev(SrcL_k : bits(5), immr : bits(6), imml : bits(6), Dst_k : bits(5)) -> unit = {
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

function exec_v_lb(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lbu(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lh(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lhu(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lw(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_ld(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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
function exec_v_lb_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lbu_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_ld_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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
function exec_v_lbi(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lbui(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_ldi(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lbi_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lbi(SrcL, simm24, Dst_k, local)
}

function exec_v_lbui_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lbui(SrcL, simm24, Dst_k, local)
}

function exec_v_ldi_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_ldi(SrcL, simm24, Dst_k, local)
}

// More BRG variants.
function exec_v_lh_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lhu_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lw_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lwu(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
  // 32-bit load, zero-extended; in 32-bit lanes this is a direct write.
  exec_v_lw(SrcL, SrcR_k, shamt, Dst_k, local)
}

function exec_v_lwu_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lw_brg(SrcL, SrcR_k, shamt, Dst_k, local)
}

// Immediate-offset loads (I) for 16/32.
function exec_v_lhi(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lhi_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lhi(SrcL, simm24, Dst_k, local)
}

function exec_v_lhui(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lhui_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lhui(SrcL, simm24, Dst_k, local)
}

function exec_v_lwi(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_lwi_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

function exec_v_lwui(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

function exec_v_lwui_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

// Unscaled (.U) forms: staged model currently treats these the same as the scaled forms.
function exec_v_ldi_u(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_ldi(SrcL, simm24, Dst_k, local)
}

function exec_v_ldi_u_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_ldi(SrcL, simm24, Dst_k, local)
}

function exec_v_lhi_u(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lhi(SrcL, simm24, Dst_k, local)
}

function exec_v_lhi_u_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lhi(SrcL, simm24, Dst_k, local)
}

function exec_v_lhui_u(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lhui(SrcL, simm24, Dst_k, local)
}

function exec_v_lhui_u_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lhui(SrcL, simm24, Dst_k, local)
}

function exec_v_lwi_u(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

function exec_v_lwi_u_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

function exec_v_lwui_u(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

function exec_v_lwui_u_brg(SrcL : bits(5), simm24 : bits(24), Dst_k : bits(5), local : bits(1)) -> unit = {
  exec_v_lwi(SrcL, simm24, Dst_k, local)
}

// -----------------------------------------------------------------------------
// Vector atomic RMW loads (staged)
//
// Spec: docs/architecture/isa-manual/src/generated/instruction_details.adoc
//
// Staged note: We do not model atomicity between lanes/cores; we implement the
// informative Read/Modify/Write sequence on memory.

function exec_v_lw_add(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      let next : bits(64) = vec_int_bits_from_carrier32(old, dst_t) + vec_int_bits_from_carrier32(b, src_t);
      mem_store32_le(ea, vec_int_pack_carrier32(next, dst_t));
      out = vec_set_lane32(out, i, vec_int_pack_carrier32(vec_int_bits_from_carrier32(old, dst_t), dst_t))
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_lw_and(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      let next : bits(64) = vec_int_bits_from_carrier32(old, dst_t) & vec_int_bits_from_carrier32(b, src_t);
      mem_store32_le(ea, vec_int_pack_carrier32(next, dst_t));
      out = vec_set_lane32(out, i, vec_int_pack_carrier32(vec_int_bits_from_carrier32(old, dst_t), dst_t))
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_lw_or(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      let next : bits(64) = vec_int_bits_from_carrier32(old, dst_t) | vec_int_bits_from_carrier32(b, src_t);
      mem_store32_le(ea, vec_int_pack_carrier32(next, dst_t));
      out = vec_set_lane32(out, i, vec_int_pack_carrier32(vec_int_bits_from_carrier32(old, dst_t), dst_t))
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_lw_xor(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      let next : bits(64) = xor_vec(vec_int_bits_from_carrier32(old, dst_t), vec_int_bits_from_carrier32(b, src_t));
      mem_store32_le(ea, vec_int_pack_carrier32(next, dst_t));
      out = vec_set_lane32(out, i, vec_int_pack_carrier32(vec_int_bits_from_carrier32(old, dst_t), dst_t))
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_lw_max(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      let old64 : bits(64) = vec_int_numeric_from_carrier32(old, dst_t);
      let b64   : bits(64) = vec_int_numeric_from_carrier32(b, src_t);
      let next  : bits(64) = if signed(old64) >= signed(b64) then old64 else b64;
      mem_store32_le(ea, vec_int_pack_carrier32(next, dst_t));
      out = vec_set_lane32(out, i, vec_int_pack_carrier32(old64, dst_t))
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_lw_min(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  var out = read_vt(RegDst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      let old64 : bits(64) = vec_int_numeric_from_carrier32(old, dst_t);
      let b64   : bits(64) = vec_int_numeric_from_carrier32(b, src_t);
      let next  : bits(64) = if signed(old64) <= signed(b64) then old64 else b64;
      mem_store32_le(ea, vec_int_pack_carrier32(next, dst_t));
      out = vec_set_lane32(out, i, vec_int_pack_carrier32(old64, dst_t))
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_ld_add(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
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

function exec_v_ld_and(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
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

function exec_v_ld_or(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
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

function exec_v_ld_xor(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
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
      mem_store64_le(ea, xor_vec(old, b));
      out = vec_store64_packed(out, i, old)
    } else ()
  };
  write_vt(RegDst_k, out)
}

function exec_v_ld_max(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
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

function exec_v_ld_min(RegDst_k : bits(5), SrcL : bits(5), SrcR_k : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
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

function exec_v_sd_add(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
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

function exec_v_sd_and(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
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

function exec_v_sd_or(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
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

function exec_v_sd_xor(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
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
      mem_store64_le(ea, xor_vec(old, b))
    } else ()
  }
}

function exec_v_sd_max(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
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

function exec_v_sd_min(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
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

function exec_v_sw_add(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, vec_int_pack_carrier32(vec_int_bits_from_carrier32(old, src_t) + vec_int_bits_from_carrier32(b, src_t), src_t))
    } else ()
  }
}

function exec_v_sw_and(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, vec_int_pack_carrier32(vec_int_bits_from_carrier32(old, src_t) & vec_int_bits_from_carrier32(b, src_t), src_t))
    } else ()
  }
}

function exec_v_sw_or(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, vec_int_pack_carrier32(vec_int_bits_from_carrier32(old, src_t) | vec_int_bits_from_carrier32(b, src_t), src_t))
    } else ()
  }
}

function exec_v_sw_xor(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      mem_store32_le(ea, vec_int_pack_carrier32(xor_vec(vec_int_bits_from_carrier32(old, src_t), vec_int_bits_from_carrier32(b, src_t)), src_t))
    } else ()
  }
}

function exec_v_sw_max(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      let old64 : bits(64) = vec_int_numeric_from_carrier32(old, src_t);
      let b64   : bits(64) = vec_int_numeric_from_carrier32(b, src_t);
      let n     : bits(64) = if signed(old64) >= signed(b64) then old64 else b64;
      mem_store32_le(ea, vec_int_pack_carrier32(n, src_t))
    } else ()
  }
}

function exec_v_sw_min(SrcL : bits(5), SrcR_k : bits(5), rl : bits(1), far : bits(1), rd : bits(1)) -> unit = {
  let _ = rl; let _ = far; let _ = rd;
  let ea : bits(64) = read_reg5(SrcL);
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src = read_vt(SrcR_k);
  let src_t : bits(5) = decoded_vec_srcr_type();
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let old : bits(32) = mem_load32_le(ea);
      let b   : bits(32) = vec_get_lane32(src, i);
      let old64 : bits(64) = vec_int_numeric_from_carrier32(old, src_t);
      let b64   : bits(64) = vec_int_numeric_from_carrier32(b, src_t);
      let n     : bits(64) = if signed(old64) <= signed(b64) then old64 else b64;
      mem_store32_le(ea, vec_int_pack_carrier32(n, src_t))
    } else ()
  }
}

// -----------------------------------------------------------------------------
// Vector shifts (staged)
// Spec: docs/architecture/isa-manual/src/generated/instruction_details.adoc

function exec_v_sll(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let a = read_vt(SrcL_k);
  let b = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let bv : bits(32) = vec_get_lane32(b, i);
    let sh : int = vec_int_shift_amount(bv, srcr_t);
    let r64 : bits(64) = sail_shiftleft(vec_int_bits_from_carrier32(av, srcl_t), sh);
    let r  : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_slli(SrcL_k : bits(5), shamt : bits(6), Dst_k : bits(5)) -> unit = {
  let a = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let sh : int = tmod_int(unsigned(shamt), if vec_int_effective_width(srcl_t) > 64 then 64 else vec_int_effective_width(srcl_t));
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let r64 : bits(64) = sail_shiftleft(vec_int_bits_from_carrier32(av, srcl_t), sh);
    let r  : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_sra(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let a = read_vt(SrcL_k);
  let b = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let bv : bits(32) = vec_get_lane32(b, i);
    let sh : int = vec_int_shift_amount(bv, srcr_t);
    let r64 : bits(64) = sail_arith_shiftright(vec_int_numeric_from_carrier32(av, srcl_t), sh);
    let r  : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_srai(SrcL_k : bits(5), shamt : bits(6), Dst_k : bits(5)) -> unit = {
  let a = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let sh : int = tmod_int(unsigned(shamt), if vec_int_effective_width(srcl_t) > 64 then 64 else vec_int_effective_width(srcl_t));
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let r64 : bits(64) = sail_arith_shiftright(vec_int_numeric_from_carrier32(av, srcl_t), sh);
    let r  : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_srl(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let a = read_vt(SrcL_k);
  let b = read_vt(SrcR_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let srcr_t : bits(5) = decoded_vec_srcr_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let bv : bits(32) = vec_get_lane32(b, i);
    let sh : int = vec_int_shift_amount(bv, srcr_t);
    let r64 : bits(64) = sail_shiftright(vec_int_bits_from_carrier32(av, srcl_t), sh);
    let r  : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
    out = vec_set_lane32(out, i, r)
  };
  write_vt(Dst_k, out)
}

function exec_v_srli(SrcL_k : bits(5), shamt : bits(6), Dst_k : bits(5)) -> unit = {
  let a = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let dst_t  : bits(5) = decoded_vec_dst_type();
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let sh : int = tmod_int(unsigned(shamt), if vec_int_effective_width(srcl_t) > 64 then 64 else vec_int_effective_width(srcl_t));
  var out = read_vt(Dst_k);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    let active = bitvector_access(pm, i) == 0b1;
    let av : bits(32) = vec_get_lane32(a, i);
    let r64 : bits(64) = sail_shiftright(vec_int_bits_from_carrier32(av, srcl_t), sh);
    let r  : bits(32) = if active then vec_int_pack_carrier32(r64, dst_t) else undefined_bitvector(32);
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

function exec_v_shfl_bfly(SrcL_k : bits(5), SrcP_k : bits(5), Dst_k : bits(5)) -> unit = {
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

function exec_v_shfl_down(SrcL_k : bits(5), SrcR_k : bits(5), SrcP_k : bits(5), Dst_k : bits(5)) -> unit = {
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

function exec_v_shfl_idx(SrcL_k : bits(5), SrcR_k : bits(5), SrcP_k : bits(5), Dst_k : bits(5)) -> unit = {
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

function exec_v_shfl_up(SrcL_k : bits(5), SrcR_k : bits(5), SrcP_k : bits(5), Dst_k : bits(5)) -> unit = {
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

function exec_v_shfli_bfly(SrcL_k : bits(5), imm7 : bits(14), Dst_k : bits(5)) -> unit = {
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

function exec_v_shfli_down(SrcL_k : bits(5), SrcR_k : bits(5), imm7 : bits(14), Dst_k : bits(5)) -> unit = {
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

function exec_v_shfli_idx(SrcL_k : bits(5), SrcR_k : bits(5), imm7 : bits(14), Dst_k : bits(5)) -> unit = {
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

function exec_v_shfli_up(SrcL_k : bits(5), SrcR_k : bits(5), imm7 : bits(14), Dst_k : bits(5)) -> unit = {
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

function exec_v_qpush(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
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

function exec_v_qpop(SrcL_k : bits(5), Dst_k : bits(5)) -> unit = {
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

function exec_v_rdadd(RegDst : bits(5), SrcL_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  var acc : bits(64) = 0x0000_0000_0000_0000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then acc = acc + vec_int_numeric_from_carrier32(vec_get_lane32(a, i), srcl_t) else ()
  };
  write_regdst(RegDst, acc)
}

function exec_v_rdand(RegDst : bits(5), SrcL_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let width : int = vec_int_effective_width(srcl_t);
  var acc : bits(64) = vec_int_bits_from_value64(0xFFFF_FFFF_FFFF_FFFF, srcl_t);
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then acc = acc & vec_int_bits_from_carrier32(vec_get_lane32(a, i), srcl_t) else ()
  };
  write_regdst(RegDst, vec_int_bits_from_value64(acc, if width > 32 then 0b00000 else srcl_t))
}

function exec_v_rdor(RegDst : bits(5), SrcL_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let width : int = vec_int_effective_width(srcl_t);
  var acc : bits(64) = 0x0000_0000_0000_0000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then acc = acc | vec_int_bits_from_carrier32(vec_get_lane32(a, i), srcl_t) else ()
  };
  write_regdst(RegDst, vec_int_bits_from_value64(acc, if width > 32 then 0b00000 else srcl_t))
}

function exec_v_rdxor(RegDst : bits(5), SrcL_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  let width : int = vec_int_effective_width(srcl_t);
  var acc : bits(64) = 0x0000_0000_0000_0000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then acc = xor_vec(acc, vec_int_bits_from_carrier32(vec_get_lane32(a, i), srcl_t)) else ()
  };
  write_regdst(RegDst, vec_int_bits_from_value64(acc, if width > 32 then 0b00000 else srcl_t))
}

function exec_v_rdmax(RegDst : bits(5), SrcL_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  var any : bool = false;
  var acc : bits(64) = 0x0000_0000_0000_0000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let x = vec_int_numeric_from_carrier32(vec_get_lane32(a, i), srcl_t);
      if not_bool(any) then { acc = x; any = true }
      else acc = if signed(acc) >= signed(x) then acc else x
    } else ()
  };
  write_regdst(RegDst, if any then acc else 0x0000_0000_0000_0000)
}

function exec_v_rdmin(RegDst : bits(5), SrcL_k : bits(5)) -> unit = {
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  let srcl_t : bits(5) = decoded_vec_srcl_type();
  var any : bool = false;
  var acc : bits(64) = 0x0000_0000_0000_0000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let x = vec_int_numeric_from_carrier32(vec_get_lane32(a, i), srcl_t);
      if not_bool(any) then { acc = x; any = true }
      else acc = if signed(acc) <= signed(x) then acc else x
    } else ()
  };
  write_regdst(RegDst, if any then acc else 0x0000_0000_0000_0000)
}

function exec_v_rdfadd(RegDst : bits(5), SrcL_k : bits(5)) -> unit = {
  // Reduce add over active lanes, interpreting lanes as FP32 bitpatterns.
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let a = read_vt(SrcL_k);
  var any : bool = false;
  var acc : bits(32) = 0x0000_0000;
  var flags : bits(5) = 0b00000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let x : bits(32) = vec_get_lane32(a, i);
      if not_bool(any) then {
        any = true;
        acc = x
      } else {
        let (sum, step_flags) = linx_fp_add(fp_active_rm(), 0b00001, zext32_from32(acc), zext32_from32(x));
        acc = sum[31..0];
        flags = flags | step_flags
      }
    } else ()
  };
  fp_record_flags(flags);
  write_regdst(RegDst, if any then zext32_from32(acc) else 0x0000_0000_0000_0000)
}

function exec_v_rdfmax(RegDst : bits(5), SrcL_k : bits(5)) -> unit = {
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

function exec_v_rdfmin(RegDst : bits(5), SrcL_k : bits(5)) -> unit = {
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

function exec_v_icvt(SrcL_k : bits(5), SrcType : bits(5), DstType : bits(5), Dst_k : bits(5)) -> unit = {
  // Strict bring-up: format conversion selected by 5-bit SrcType/DstType codes.
  // The manual table (see RegId10 operand encoding + convert tables) defines these codes.
  // This Sail model currently implements a conservative subset:
  // - Integer types: u64/u32/u16/u8 and s64/s32/s16/s8
  //   * narrowing: truncate low bits
  //   * widening: sign-extend if src signed, else zero-extend
  // - Other/packed/experimental types: deterministic 0 result in the staged model.
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

function exec_v_icvtf(SrcL_k : bits(5), SrcType : bits(5), DstType : bits(5), Dst_k : bits(5)) -> unit = {
  // Numeric integer -> floating conversion selected by the same 5-bit SrcType /
  // DstType tables used by the convert-class scalar instructions.
  if not_bool(int_type_code_supported(SrcType) & fp_type_code_supported(DstType)) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let src_bits : int = int_type_width(SrcType);
    let dst_bits : int = float_type_width(DstType);
    let src_is_d : bool = src_bits == 64;
    let dst_is_d : bool = dst_bits == 64;

    let vw32 : int = vec_length_from_lcfr();
    let src_elems : int = if src_is_d then tdiv_int(vw32, 2) else vw32;
    let dst_elems : int = if dst_is_d then tdiv_int(vw32, 2) else vw32;
    let n : int = if src_elems < dst_elems then src_elems else dst_elems;
    let pm = read_predicate_p();
    let a = read_vt(SrcL_k);
    var out = read_vt(Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (n - 1)) {
      assert((0 <= i) & (i < 64));
      let wide : bool = src_is_d | dst_is_d;
      if wide then assert(i < 32) else ();
      let pidx : int = if wide then 2*i else i;
      assert((0 <= pidx) & (pidx < 64));
      let active = bitvector_access(pm, pidx) == 0b1;
      if active then {
        let x64 : bits(64) =
          if src_is_d then {
            let lo : bits(32) = vec_get_lane32(a, 2*i);
            let hi : bits(32) = vec_get_lane32(a, 2*i + 1);
            hi @ lo
          } else {
            zext32_from32(vec_get_lane32(a, i))
          };

        let y64 : bits(64) =
          if src_bits == 64 then x64
          else if src_bits == 32 then sail_zeros(32) @ x64[31..0]
          else if src_bits == 16 then sail_zeros(48) @ x64[15..0]
          else if src_bits == 8 then sail_zeros(56) @ x64[7..0]
          else if src_bits == 4 then sail_zeros(60) @ x64[3..0]
          else if src_bits == 2 then sail_zeros(62) @ x64[1..0]
          else sail_zeros(63) @ x64[0..0];

        let (result, step_flags) = linx_int_to_fp(fp_active_rm(), SrcType, DstType, y64);
        flags = flags | step_flags;
        if dst_is_d then {
          out = vec_store64_packed(out, i, result)
        } else {
          out = vec_set_lane32(out, i, pack_low_bits_into_lane32(result, dst_bits))
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
    fp_record_flags(flags);
    write_vt(Dst_k, out)
  }
}

function exec_xb(acr_id : bits(12), cross_bid : bits(8)) -> unit = {
  // Strict bring-up: XB is a controlled cross-block call dispatcher.
  // The generic v0.4 contract standardizes legality, permission, and lookup.
  // The binary entry layout remains platform-defined, so the model records the
  // resolved dispatch request instead of decoding a non-canonical block body.
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
    if w0 == 0x0000_0000_0000_0000 then {
      trap_e_inst(0x11, 0x00, read_pc_or_tpc())
    } else {
      record_xb_dispatch(target_acr, cid, ea, w0)
    }
  };
}

// -----------------------------------------------------------------------------
// Vector stores (staged)
//
// Spec: docs/architecture/isa-manual/src/generated/instruction_details.adoc

function exec_v_shi(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
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

function exec_v_shi_brg(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_shi(SrcL_k, SrcR, simm24, local)
}

function exec_v_shi_u(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_shi(SrcL_k, SrcR, simm24, local)
}

function exec_v_shi_u_brg(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_shi(SrcL_k, SrcR, simm24, local)
}

function exec_v_sb(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_sw(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_sw_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
  // BRG: lane0 address + lane0 data.
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let data = read_vt(SrcD_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, 4 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  mem_store32_le(ea0, vec_get_lane32(data, 0))
}

function exec_v_sw_u(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
  // Unscaled: staged model treats same as scaled.
  exec_v_sw(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_sw_u_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
  exec_v_sw_brg(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_swi(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
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

function exec_v_swi_brg(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_swi(SrcL_k, SrcR, simm24, local)
}

function exec_v_swi_u(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_swi(SrcL_k, SrcR, simm24, local)
}

function exec_v_swi_u_brg(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_swi(SrcL_k, SrcR, simm24, local)
}

function exec_v_sb_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_sh(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_sh_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
  let _ = local;
  let base : bits(64) = read_reg5(SrcL);
  let idxv = read_vt(SrcR_k);
  let data = read_vt(SrcD_k);
  let idx0 : bits(32) = vec_get_lane32(idxv, 0);
  let ea0 : bits(64) = vec_compute_ea(base, 2 * unsigned(ssr_lc0[31..0]), vec_off_from_idx32(idx0, shamt));
  let h0 : bits(16) = vec_get_lane32(data, 0)[15..0];
  mem_store16_le(ea0, h0)
}

function exec_v_sh_u(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
  exec_v_sh(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_sh_u_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
  exec_v_sh_brg(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_sd(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_sd_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
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

function exec_v_sd_u(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
  exec_v_sd(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_sd_u_brg(SrcL : bits(5), SrcR_k : bits(5), shamt : bits(5), SrcD_k : bits(5), local : bits(1)) -> unit = {
  exec_v_sd_brg(SrcL, SrcR_k, shamt, SrcD_k, local)
}

function exec_v_sbi(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
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

function exec_v_sbi_brg(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_sbi(SrcL_k, SrcR, simm24, local)
}

function exec_v_sdi(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
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

function exec_v_sdi_brg(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_sdi(SrcL_k, SrcR, simm24, local)
}

function exec_v_sdi_u(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_sdi(SrcL_k, SrcR, simm24, local)
}

function exec_v_sdi_u_brg(SrcL_k : bits(5), SrcR : bits(5), simm24 : bits(24), local : bits(1)) -> unit = {
  exec_v_sdi(SrcL_k, SrcR, simm24, local)
}

// -----------------------------------------------------------------------------
// V.F* vector floating-point (FSU)
//
// Canonical Sail rule:
// - every architectural vector lane stores a 32-bit carrier,
// - decode supplies the semantic type when the encoding has one,
// - execution numerically converts carrier -> semantic type -> result -> carrier.
// Non-convert V.F* forms currently default to the live encoded FP32 carrier domain.

function exec_v_fadd(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t) & (src_t == decoded_vec_srcr_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b_raw, f1) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        let (sum_raw, f2) = linx_fp_add(fp_active_rm(), src_t, a_raw, b_raw);
        let (carrier, f3) = vec_fp_result_to_carrier32(sum_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2 | f3;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fsub(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t) & (src_t == decoded_vec_srcr_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b_raw, f1) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        let (diff_raw, f2) = linx_fp_sub(fp_active_rm(), src_t, a_raw, b_raw);
        let (carrier, f3) = vec_fp_result_to_carrier32(diff_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2 | f3;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fmul(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t) & (src_t == decoded_vec_srcr_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b_raw, f1) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        let (prod_raw, f2) = linx_fp_mul(fp_active_rm(), src_t, a_raw, b_raw);
        let (carrier, f3) = vec_fp_result_to_carrier32(prod_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2 | f3;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fdiv(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t) & (src_t == decoded_vec_srcr_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b_raw, f1) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        let (quot_raw, f2) = linx_fp_div(fp_active_rm(), src_t, a_raw, b_raw);
        let (carrier, f3) = vec_fp_result_to_carrier32(quot_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2 | f3;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fsqrt(SrcL_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t)) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (res_raw, f1) = linx_fp_sqrt(fp_active_rm(), src_t, a_raw);
        let (carrier, f2) = vec_fp_result_to_carrier32(res_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_frecip(SrcL_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t)) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (res_raw, f1) = linx_fp_recip(fp_active_rm(), src_t, a_raw);
        let (carrier, f2) = vec_fp_result_to_carrier32(res_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fexp(SrcL_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t)) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (res_raw, f1) = linx_fp_exp(fp_active_rm(), src_t, a_raw);
        let (carrier, f2) = vec_fp_result_to_carrier32(res_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fabs(SrcL_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t)) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let carrier_in : bits(32) = read_vec_operand_lane32(decoded_vec_srcl_regid(), i);
        let (norm, f0) = vec_fp_to_fp64_norm(carrier_in, src_t);
        let abs_norm : bits(64) = norm & 0x7FFF_FFFF_FFFF_FFFF;
        let (abs_raw, f1) =
          if src_t == 0b00000 then (abs_norm, 0b00000)
          else linx_fp_to_fp(fp_active_rm(), src_t, 0b00000, abs_norm);
        let (carrier, f2) = vec_fp_result_to_carrier32(abs_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fclass(SrcL_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let vw : int = vec_length_from_lcfr();
  let pm = read_predicate_p();
  let src_t : bits(5) = decoded_vec_srcl_type();
  var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
  var flags : bits(5) = 0b00000;
  foreach (i from 0 to (vw - 1)) {
    assert((0 <= i) & (i < 64));
    if bitvector_access(pm, i) == 0b1 then {
      let (norm, f0) = vec_fp_to_fp64_norm(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
      flags = flags | f0;
      out = vec_set_lane32(out, i, fp64_class_mask(norm))
    } else ()
  };
  fp_record_flags(flags);
  write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
}

function exec_v_fcvt(SrcL_k : bits(5), SrcType : bits(5), DstType : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  if not_bool(fp_type_code_supported(SrcType) & fp_type_code_supported(DstType)) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (src_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), SrcType);
        let (dst_raw, f1) = linx_fp_to_fp(fp_active_rm(), DstType, SrcType, src_raw);
        let (carrier, f2) = vec_fp_to_carrier32(dst_raw, DstType);
        flags = flags | f0 | f1 | f2;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fcvti(SrcL_k : bits(5), SrcType : bits(5), DstType : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  if not_bool(fp_type_code_supported(SrcType) & int_type_code_supported(DstType)) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (src_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), SrcType);
        let (dst_raw, f1) = linx_fp_to_int(fp_active_rm(), DstType, SrcType, src_raw);
        let carrier : bits(32) = pack_low_int_bits_into_lane32(dst_raw, int_type_width(DstType));
        flags = flags | f0 | f1;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fmadd(SrcL_k : bits(5), SrcR_k : bits(5), SrcA_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let _ = SrcA_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t) & (src_t == decoded_vec_srcr_type()) & (src_t == decoded_vec_srca_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b_raw, f1) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        let (c_raw, f2) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srca_regid(), i), src_t);
        let (res_raw, f3) = linx_fp_fmadd(fp_active_rm(), src_t, a_raw, b_raw, c_raw);
        let (carrier, f4) = vec_fp_result_to_carrier32(res_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2 | f3 | f4;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fmsub(SrcL_k : bits(5), SrcR_k : bits(5), SrcA_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let _ = SrcA_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t) & (src_t == decoded_vec_srcr_type()) & (src_t == decoded_vec_srca_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b_raw, f1) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        let (c_raw, f2) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srca_regid(), i), src_t);
        let (res_raw, f3) = linx_fp_fmsub(fp_active_rm(), src_t, a_raw, b_raw, c_raw);
        let (carrier, f4) = vec_fp_result_to_carrier32(res_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2 | f3 | f4;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fnmadd(SrcL_k : bits(5), SrcR_k : bits(5), SrcA_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let _ = SrcA_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t) & (src_t == decoded_vec_srcr_type()) & (src_t == decoded_vec_srca_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b_raw, f1) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        let (c_raw, f2) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srca_regid(), i), src_t);
        let (res_raw, f3) = linx_fp_fnmadd(fp_active_rm(), src_t, a_raw, b_raw, c_raw);
        let (carrier, f4) = vec_fp_result_to_carrier32(res_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2 | f3 | f4;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fnmsub(SrcL_k : bits(5), SrcR_k : bits(5), SrcA_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let _ = SrcA_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t) & (src_t == decoded_vec_srcr_type()) & (src_t == decoded_vec_srca_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a_raw, f0) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b_raw, f1) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        let (c_raw, f2) = vec_fp_from_carrier32(read_vec_operand_lane32(decoded_vec_srca_regid(), i), src_t);
        let (res_raw, f3) = linx_fp_fnmsub(fp_active_rm(), src_t, a_raw, b_raw, c_raw);
        let (carrier, f4) = vec_fp_result_to_carrier32(res_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2 | f3 | f4;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

// Vector FP compares: ordered; NaN => false. Results are 0/1 carriers in each lane.
function exec_v_feq(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  if not_bool(fp_type_code_supported(src_t) & (src_t == decoded_vec_srcr_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a64, f0) = vec_fp_to_fp64_norm(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b64, f1) = vec_fp_to_fp64_norm(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        flags = flags | f0 | f1;
        out = vec_set_lane32(out, i, vec_bool32(fp64_eq(a64, b64)))
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_flt(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  if not_bool(fp_type_code_supported(src_t) & (src_t == decoded_vec_srcr_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a64, f0) = vec_fp_to_fp64_norm(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b64, f1) = vec_fp_to_fp64_norm(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        flags = flags | f0 | f1;
        out = vec_set_lane32(out, i, vec_bool32(fp64_lt(a64, b64)))
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fge(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  if not_bool(fp_type_code_supported(src_t) & (src_t == decoded_vec_srcr_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a64, f0) = vec_fp_to_fp64_norm(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b64, f1) = vec_fp_to_fp64_norm(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        flags = flags | f0 | f1;
        out = vec_set_lane32(out, i, vec_bool32(fp64_ge(a64, b64)))
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fne(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  if not_bool(fp_type_code_supported(src_t) & (src_t == decoded_vec_srcr_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let (a64, f0) = vec_fp_to_fp64_norm(read_vec_operand_lane32(decoded_vec_srcl_regid(), i), src_t);
        let (b64, f1) = vec_fp_to_fp64_norm(read_vec_operand_lane32(decoded_vec_srcr_regid(), i), src_t);
        flags = flags | f0 | f1;
        out = vec_set_lane32(out, i, vec_bool32(not_bool(fp64_eq(a64, b64))))
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

// S-variants are aliases.
function exec_v_feqs(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = { exec_v_feq(SrcL_k, SrcR_k, Dst_k) }
function exec_v_flts(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = { exec_v_flt(SrcL_k, SrcR_k, Dst_k) }
function exec_v_fges(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = { exec_v_fge(SrcL_k, SrcR_k, Dst_k) }
function exec_v_fnes(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = { exec_v_fne(SrcL_k, SrcR_k, Dst_k) }

function exec_v_fmax(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t) & (src_t == decoded_vec_srcr_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let a_carrier : bits(32) = read_vec_operand_lane32(decoded_vec_srcl_regid(), i);
        let b_carrier : bits(32) = read_vec_operand_lane32(decoded_vec_srcr_regid(), i);
        let (a_raw, f0) = vec_fp_from_carrier32(a_carrier, src_t);
        let (b_raw, f1) = vec_fp_from_carrier32(b_carrier, src_t);
        let (a64, f2) = vec_fp_to_fp64_norm(a_carrier, src_t);
        let (b64, f3) = vec_fp_to_fp64_norm(b_carrier, src_t);
        let nan_a = fp64_is_nan(a64);
        let nan_b = fp64_is_nan(b64);
        let both_zero = fp64_is_zero(a64) & fp64_is_zero(b64);
        let (qnan_raw, f4) = vec_fp_qnan_in_type(src_t);
        let (zero_raw, f5) =
          if src_t == 0b00000 then (0x0000_0000_0000_0000, 0b00000)
          else linx_fp_to_fp(fp_active_rm(), src_t, 0b00000, 0x0000_0000_0000_0000);
        let chosen_raw : bits(64) =
          if nan_a & nan_b then qnan_raw
          else if nan_a then b_raw
          else if nan_b then a_raw
          else if both_zero then zero_raw
          else if fp64_ge(a64, b64) then a_raw else b_raw;
        let (carrier, f6) = vec_fp_result_to_carrier32(chosen_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2 | f3 | f4 | f5 | f6;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

function exec_v_fmin(SrcL_k : bits(5), SrcR_k : bits(5), Dst_k : bits(5)) -> unit = {
  let _ = SrcL_k;
  let _ = SrcR_k;
  let src_t : bits(5) = decoded_vec_srcl_type();
  let dst_t : bits(5) = decoded_vec_dst_type();
  if not_bool(fp_type_code_supported(src_t) & fp_type_code_supported(dst_t) & (src_t == decoded_vec_srcr_type())) then {
    trap_illegal_inst(read_pc_or_tpc())
  } else {
    let vw : int = vec_length_from_lcfr();
    let pm = read_predicate_p();
    var out = read_vec_dest_value(decoded_vec_dst_regid(), Dst_k);
    var flags : bits(5) = 0b00000;
    foreach (i from 0 to (vw - 1)) {
      assert((0 <= i) & (i < 64));
      if bitvector_access(pm, i) == 0b1 then {
        let a_carrier : bits(32) = read_vec_operand_lane32(decoded_vec_srcl_regid(), i);
        let b_carrier : bits(32) = read_vec_operand_lane32(decoded_vec_srcr_regid(), i);
        let (a_raw, f0) = vec_fp_from_carrier32(a_carrier, src_t);
        let (b_raw, f1) = vec_fp_from_carrier32(b_carrier, src_t);
        let (a64, f2) = vec_fp_to_fp64_norm(a_carrier, src_t);
        let (b64, f3) = vec_fp_to_fp64_norm(b_carrier, src_t);
        let nan_a = fp64_is_nan(a64);
        let nan_b = fp64_is_nan(b64);
        let both_zero = fp64_is_zero(a64) & fp64_is_zero(b64);
        let neg0 = (a64[63] == 0b1) | (b64[63] == 0b1);
        let (qnan_raw, f4) = vec_fp_qnan_in_type(src_t);
        let (zero_raw, f5) =
          if src_t == 0b00000 then {
            (if neg0 then 0x8000_0000_0000_0000 else 0x0000_0000_0000_0000, 0b00000)
          } else {
            linx_fp_to_fp(
              fp_active_rm(),
              src_t,
              0b00000,
              if neg0 then 0x8000_0000_0000_0000 else 0x0000_0000_0000_0000
            )
          };
        let chosen_raw : bits(64) =
          if nan_a & nan_b then qnan_raw
          else if nan_a then b_raw
          else if nan_b then a_raw
          else if both_zero then zero_raw
          else if fp64_lt(a64, b64) then a_raw else b_raw;
        let (carrier, f6) = vec_fp_result_to_carrier32(chosen_raw, src_t, dst_t);
        flags = flags | f0 | f1 | f2 | f3 | f4 | f5 | f6;
        out = vec_set_lane32(out, i, carrier)
      } else ()
    };
    fp_record_flags(flags);
    write_vec_dest_value(decoded_vec_dst_regid(), Dst_k, out)
  }
}

// (32-bit helpers defined earlier near V.* block)

function exec_v_psel(SrcP_k : bits(5), SrcL_k : bits(5), SrcR_k : bits(5), neg : bits(1), Dst_k : bits(5)) -> unit = {
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
    let b : bits(32) = if neg == 0b1 then sub_bits(0x0000_0000, b0) else b0;
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
    let r32 = xor_vec(a32, 0x8000_0000);
    write_regdst(RegDst, zext32_from32(r32))
  } else {
    write_regdst(RegDst, xor_vec(a64, 0x8000_0000_0000_0000))
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
function rmw32_xor(a : bits(32), b : bits(32)) -> bits(32) = { xor_vec(a, b) }

function rmw32_smax(a : bits(32), b : bits(32)) -> bits(32) = { if (signed(a) >= signed(b)) then a else b }
function rmw32_smin(a : bits(32), b : bits(32)) -> bits(32) = { if (signed(a) <= signed(b)) then a else b }
function rmw32_umax(a : bits(32), b : bits(32)) -> bits(32) = { if (unsigned(a) >= unsigned(b)) then a else b }
function rmw32_umin(a : bits(32), b : bits(32)) -> bits(32) = { if (unsigned(a) <= unsigned(b)) then a else b }

function rmw64_add(a : bits(64), b : bits(64)) -> bits(64) = { a + b }
function rmw64_and(a : bits(64), b : bits(64)) -> bits(64) = { a & b }
function rmw64_or(a : bits(64), b : bits(64)) -> bits(64) = { a | b }
function rmw64_xor(a : bits(64), b : bits(64)) -> bits(64) = { xor_vec(a, b) }

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

function hl_ea_pcr(simm17 : bits(29)) -> bits(64) = {
  hl_pc_aligned4() + sail_shiftleft(sext29_to64(simm17), 2)
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
function exec_hl_lb_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, sext8_from8(b))
}
function exec_hl_lbu_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, zext8_from8(b))
}
function exec_hl_lh_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}
function exec_hl_lhu_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}
function exec_hl_lw_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}
function exec_hl_lwu_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}
function exec_hl_ld_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
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
function exec_hl_sb_pcr(SrcD : bits(5), simm17 : bits(29)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(ea, v)
}
function exec_hl_sh_pcr(SrcD : bits(5), simm17 : bits(29)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}
function exec_hl_sw_pcr(SrcD : bits(5), simm17 : bits(29)) -> unit = {
  let ea = hl_ea_pcr(simm17);
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}
function exec_hl_sd_pcr(SrcD : bits(5), simm17 : bits(29)) -> unit = {
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
