// LinxISA 0.59.1 execution functions. The model entry supplies the state and common helpers.

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
// architecturally specified in v0.57 semantics yet.
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

function exec_hl_qpop(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), e : bits(1), r : bits(1)) -> unit = {
  let _ = SrcL; let _ = e; let _ = r;
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
// BRU: comparisons and commit-argument setting (strict v0.57 staged).
//
// NOTE: these are scalar boolean results (0/1) written via RegDst or to the
// block-control commit-argument domain (BARG.CARG).

// (bool_to_u64 defined near top of file)

function exec_cmp_eq(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  write_regdst(RegDst, bool_to_u64(a == b))
}

function exec_cmp_ne(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  write_regdst(RegDst, bool_to_u64(a != b))
}

function exec_cmp_lt(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  write_regdst(RegDst, bool_to_u64(signed(a) < signed(b)))
}

function exec_cmp_ge(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  write_regdst(RegDst, bool_to_u64(signed(a) >= signed(b)))
}

function exec_cmp_ltu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  write_regdst(RegDst, bool_to_u64(unsigned(a) < unsigned(b)))
}

function exec_cmp_geu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  write_regdst(RegDst, bool_to_u64(unsigned(a) >= unsigned(b)))
}

function exec_cmp_and(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_compare_srcrtype_logic64(SrcRType, b0);
  write_regdst(RegDst, bool_to_u64((a & b) != 0x0000_0000_0000_0000))
}

function exec_cmp_or(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_compare_srcrtype_logic64(SrcRType, b0);
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
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  set_commit_argument(bool_to_u64(a == b))
}

function exec_setc_ne(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  set_commit_argument(bool_to_u64(a != b))
}

function exec_setc_lt(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  set_commit_argument(bool_to_u64(signed(a) < signed(b)))
}

function exec_setc_ge(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  set_commit_argument(bool_to_u64(signed(a) >= signed(b)))
}

function exec_setc_ltu(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  set_commit_argument(bool_to_u64(unsigned(a) < unsigned(b)))
}

function exec_setc_geu(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_restricted_compare_srcrtype64(SrcRType, b0);
  set_commit_argument(bool_to_u64(unsigned(a) >= unsigned(b)))
}

function exec_setc_and(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_compare_srcrtype_logic64(SrcRType, b0);
  set_commit_argument(bool_to_u64((a & b) != 0x0000_0000_0000_0000))
}

function exec_setc_or(SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b = apply_compare_srcrtype_logic64(SrcRType, b0);
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
// Contract summary (PTO ISA 0.58.6):
// - Updates TPC (body-local PC), not architectural global PC.
// - PC-relative base is *current instruction* TPC.
// - Immediate offsets are halfword-scaled: target = base + sail_shiftleft(sext(offset, 1)).
// - Retired B.EQ/NE/LT/GE/LTU/GEU/Z/NZ words are reserved and decode illegal.
// - Misaligned/unfetchable targets are reported as E_BLOCK(EC_BFETCH) by the fetch machinery.

function tpc_rel_target_from_imm22(simm22 : bits(22)) -> bits(64) = {
  let off = sail_shiftleft(sext22_to64(simm22), 1);
  read_tpc() + off
}

function exec_j(simm22 : bits(22)) -> unit = {
  write_tpc(tpc_rel_target_from_imm22(simm22))
}

function exec_jr(SrcL : bits(5), simm12 : bits(12)) -> unit = {
  // NOTE: JR encoding also contains a SrcZero field; strict v0.57 ignores it.
  let base = read_reg5(SrcL);
  let off = sail_shiftleft(sext12_to64(simm12), 1);
  write_tpc(base + off)
}


// -----------------------------------------------------------------------------
// PC-relative operations (ADDTPC/SETRET)

// The staged model has no Reg5 queue state.  Keep this increment honest:
// physical GPR sources are 0..23 and destination codes 24..29 discard. Queue
// sources 24..31 and destinations 30/31 reject before effects in these paths.
// These rejections describe model
// coverage and do not make the golden selector codes architecturally invalid.
function scalar_gpr_source_supported(selector : bits(5)) -> bool = {
  unsigned(selector) < 24
}

function scalar_gpr_or_discard_destination_supported(selector : bits(5)) -> bool = {
  unsigned(selector) < 30
}

function write_scalar_gpr_or_discard(selector : bits(5), value : bits(64)) -> unit = {
  if unsigned(selector) < 24 then write_reg5(selector, value)
  else if unsigned(selector) < 30 then ()
  else trap_illegal_inst(read_pc_or_tpc())
}

function exec_addtpc(RegDst : bits(5), imm20 : bits(20)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then
    trap_illegal_inst(read_pc_or_tpc())
  else {
    let base = read_pc_or_tpc();
    let off = sail_shiftleft(sext20_to64(imm20), 12);
    write_scalar_gpr_or_discard(RegDst, base + off)
  }
}

function exec_setret(imm20 : bits(20)) -> unit = {
  let base = read_pc_or_tpc();
  let off = sail_shiftleft(zext20_to64(imm20), 1);
  write_regdst(0b01010, base + off)  // RA
}

function exec_hl_addtpc(RegDst : bits(5), imm32 : bits(32)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then
    trap_illegal_inst(read_pc_or_tpc())
  else {
    let base = read_pc_or_tpc();
    let off = sail_shiftleft(sext32_from32(imm32), 12);
    write_scalar_gpr_or_discard(RegDst, base + off)
  }
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
  // Select SrcL for a nonzero predicate, otherwise select SrcR. CSEL uses
  // SrcRType=11 for its optional .neg spelling; every other value is plain.
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
  // HL.LUI places the split immediate in bits 63:32 and clears bits 31:0.
  write_regdst(RegDst, sail_shiftleft(zext32_from32(imm32), 32))
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
  let idx = apply_address_srcrtype64(srcrtype, read_reg5(srcr));
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

function read_launch_system_register(id24 : bits(24)) -> bits(64) = {
  match hscb_read_geometry(id24) {
    Some(value) => value,
    None() => read_system_register(id24)
  }
}

function msgb_instruction_fault(result : msgb_bse_outcome) -> unit = {
  match result {
    MSGB_BSE_BAD_CONTEXT => trap_illegal_inst(read_pc_or_tpc()),
    MSGB_BSE_BAD_ENVELOPE => raise_trap(trapnum_block_trap(), sail_zeros(24), read_tpc(), 0b0),
    MSGB_BSE_BLOCKED => msgb_instruction_blocked = true,
    MSGB_BSE_COMPLETED => ()
  }
}

function msgb_system_block() -> bool = {
  barg_valid & barg_block_type_cur == 0b0001
}

function msgb_execute_get(dst : bits(5), address : bits(24)) -> unit = {
  msgb_instruction_blocked = false;
  if not_bool(msgb_system_block()) then msgb_instruction_fault(MSGB_BSE_BAD_ENVELOPE)
  else match msgb_platform_instruction_context() {
    None() => trap_illegal_ssr(),
    Some(ctx) => match msgb_read_preflight(ctx, address) {
      MSGB_BSE_COMPLETED => match msgb_register_read(ctx, address) {
        None() => trap_illegal_ssr(),
        Some(value) => write_regdst(dst, value)
      },
      result => msgb_instruction_fault(result)
    }
  }
}

function msgb_execute_set(src : bits(5), address : bits(24)) -> unit = {
  msgb_instruction_blocked = false;
  if not_bool(msgb_system_block()) then msgb_instruction_fault(MSGB_BSE_BAD_ENVELOPE)
  else if not_bool(msgb_register_writable(address)) then trap_illegal_ssr()
  else match msgb_platform_instruction_context() {
    None() => trap_illegal_ssr(),
    Some(ctx) => match msgb_effect_preflight(ctx, msgb_config_address(address)) {
      MSGB_BSE_COMPLETED =>
        if not_bool(msgb_register_write(ctx, address, read_reg5(src))) then trap_illegal_ssr()
        else (),
      result => msgb_instruction_fault(result)
    }
  }
}

function exec_ssrget(RegDst : bits(5), ssr_id12 : bits(12)) -> unit = {
  let id24 : bits(24) = sail_zero_extend(ssr_id12, 24);
  if msgb_address(id24) then msgb_execute_get(RegDst, id24)
  else if not_bool(system_register_readable(id24)) then trap_illegal_ssr()
  else write_regdst(RegDst, read_launch_system_register(id24))
}

function exec_ssrset(SrcL : bits(5), ssr_id12 : bits(12)) -> unit = {
  let id24 : bits(24) = sail_zero_extend(ssr_id12, 24);
  if msgb_address(id24) then msgb_execute_set(SrcL, id24)
  else if not_bool(system_register_writable(id24)) then trap_illegal_ssr()
  else write_system_register(id24, read_reg5(SrcL))
}

function exec_ssrswap(RegDst : bits(5), SrcL : bits(5), ssr_id12 : bits(12)) -> unit = {
  let id24 : bits(24) = sail_zero_extend(ssr_id12, 24);
  if not_bool(system_register_readable(id24) & system_register_writable(id24)) then {
    trap_illegal_ssr()
  } else {
    let old = swap_system_register(id24, read_reg5(SrcL));
    write_regdst(RegDst, old)
  }
}

function exec_hl_ssrget(RegDst : bits(5), ssr_id24 : bits(24)) -> unit = {
  if msgb_address(ssr_id24) then msgb_execute_get(RegDst, ssr_id24)
  else if not_bool(system_register_readable(ssr_id24)) then trap_illegal_ssr()
  else write_regdst(RegDst, read_launch_system_register(ssr_id24))
}

function exec_hl_ssrset(SrcL : bits(5), ssr_id24 : bits(24)) -> unit = {
  if msgb_address(ssr_id24) then msgb_execute_set(SrcL, ssr_id24)
  else if not_bool(system_register_writable(ssr_id24)) then trap_illegal_ssr()
  else write_system_register(ssr_id24, read_reg5(SrcL))
}

function exec_c_ssrget(ssrid : bits(5)) -> unit = {
  // C.SSRGET encodes a small SSR_ID domain directly in the low bits (no remap).
  // SSR_ID[4:0] = SSRID.
  let id12 : bits(12) = (sail_zeros(7) @ ssrid);
  let id24 : bits(24) = sail_zero_extend(id12, 24);
  if not_bool(system_register_readable(id24)) then trap_illegal_ssr()
  else write_regdst(reg_t(), read_system_register(id24))
}

function exec_lsrget(RegDst : bits(5), lsr_id12 : bits(12)) -> unit = {
  // Normative op (informative):
  //   value = ReadSystemRegister(ID)
  //   Write(Dst, value)
  // Source: docs/architecture/isa-manual/src/generated/instruction_details.adoc (LSRGET)
  let id24 : bits(24) = sail_zero_extend(lsr_id12, 24);
  if not_bool(system_register_readable(id24)) then trap_illegal_ssr()
  else write_regdst(RegDst, read_launch_system_register(id24))
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
// R975/R980 architectural semantics: immediate-only F arithmetic, inclusive
// R2..R23 ring ranges, high-end frame slots, and retained event progress.

function template_sp() -> bits(5) = { 0b00001 }

function template_ra() -> bits(5) = { 0b01010 }

function template_endpoint_valid(r : bits(5)) -> bool = {
  let x : int = unsigned(r);
  (x >= 2) & (x <= 23)
}

function template_range_count(begin : bits(5), endv : bits(5)) -> int = {
  let b : int = unsigned(begin);
  let e : int = unsigned(endv);
  if e >= b then (e - b + 1) else ((24 - b) + (e - 2) + 1)
}

function template_reg_at(begin : bits(5), idx : int) -> bits(5) = {
  let raw : int = unsigned(begin) + idx;
  if raw <= 23 then (sail_zeros(5) + raw) else (sail_zeros(5) + (2 + (raw - 24)))
}

function template_frame_legal(begin : bits(5), endv : bits(5), f : int, require_r10_begin : bool) -> bool = {
  let n : int = template_range_count(begin, endv);
  template_endpoint_valid(begin)
  & template_endpoint_valid(endv)
  & (n >= 1)
  & (n <= 22)
  & (tmod_int(f, 8) == 0)
  & (f >= (8 * n))
  & (not_bool(require_r10_begin) | (begin == template_ra()))
}

function template_slot_addr(caller_sp : bits(64), idx : int) -> bits(64) = {
  sub_bits(caller_sp, sail_zeros(64) + (8 * (idx + 1)))
}

function template_marker_proven(addr : bits(64)) -> bool = {
  template_marker_check_count = template_marker_check_count + 0x0000_0000_0000_0001;
  (block_marker0_valid & (block_marker0_pc == addr))
  | (block_marker1_valid & (block_marker1_pc == addr))
  | (block_marker2_valid & (block_marker2_pc == addr))
  | (block_marker3_valid & (block_marker3_pc == addr))
}

function template_vload_admitted() -> bool = {
  template_vload_admission_check_count = template_vload_admission_check_count + 0x0000_0000_0000_0001;
  template_vload_class == 0b001
}

function template_load64(ea : bits(64)) -> bits(64) = {
  if template_memory_hook_enabled then {
    let _ = ea;
    template_memory_hook_load_count = template_memory_hook_load_count + 0x0000_0000_0000_0001;
    template_memory_hook_load_value
  } else mem_load64_le(ea)
}

function template_store64(ea : bits(64), v : bits(64)) -> unit = {
  if template_memory_hook_enabled then {
    let _ = ea;
    let _ = v;
    template_memory_hook_store_count = template_memory_hook_store_count + 0x0000_0000_0000_0001
  } else mem_store64_le(ea, v)
}

function template_publish_target(tgt : bits(64)) -> unit = {
  set_commit_target_value(tgt);
  template_target_publish_count = template_target_publish_count + 0x0000_0000_0000_0001
}

function template_complete_event(kind : bits(8)) -> unit = {
  template_last_event_kind = kind;
  template_event_commit_count = template_event_commit_count + 0x0000_0000_0000_0001;
  template_step_index = template_step_index + 0x01;
  if template_step_index == template_event_count then template_phase = 0b10 else ()
}

function template_capture_entry_values(begin : bits(5), nregs : int) -> unit = {
  var i : int = 0;
  while i < nregs do {
    template_set_saved_value(i, read_reg5(template_reg_at(begin, i)));
    i = i + 1
  }
}

function template_maybe_stop_event(kind : bits(8), faultarg : bits(64)) -> bool = {
  if template_data_fault_step == template_step_index then {
    if (kind == 0x02) | (kind == 0x04) then {
      template_raise_phase1_data_fault(faultarg);
      false
    } else {
      template_data_fault_ignored_count = template_data_fault_ignored_count + 0x0000_0000_0000_0001;
      if template_interrupt_step == template_step_index then {
        template_raise_phase1_interrupt(kind);
        false
      } else true
    }
  } else if template_interrupt_step == template_step_index then {
    template_raise_phase1_interrupt(kind);
    false
  } else true
}

function template_execute_one_event() -> bool = {
  if not_bool(template_valid & (template_phase == 0b01)) then false
  else {
    let step : int = unsigned(template_step_index);
    let form : bits(3) = template_form;
    if form == 0b001 then {
      if step == 0 then {
        if template_maybe_stop_event(0x01, 0x0000_0000_0000_0000) then {
          write_reg5(template_sp(), template_sp_a);
          template_complete_event(0x01);
          true
        } else false
      } else {
        let i : int = step - 1;
        let slot : bits(64) = template_slot_addr(template_sp_c, i);
        if template_maybe_stop_event(0x02, slot) then {
          template_store64(slot, template_get_saved_value(i));
          template_complete_event(0x02);
          true
        } else false
      }
    } else if form == 0b010 then {
      if step == 0 then {
        if template_maybe_stop_event(0x03, 0x0000_0000_0000_0000) then {
          write_reg5(template_sp(), template_sp_c);
          template_complete_event(0x03);
          true
        } else false
      } else {
        let i : int = step - 1;
        let slot : bits(64) = template_slot_addr(template_sp_c, i);
        if template_maybe_stop_event(0x04, slot) then {
          let r : bits(5) = template_reg_at(template_begin, i);
          let v : bits(64) = template_load64(slot);
          write_reg5(r, v);
          template_complete_event(0x04);
          true
        } else false
      }
    } else if form == 0b011 then {
      if step == 0 then {
        if template_maybe_stop_event(0x05, 0x0000_0000_0000_0000) then {
          template_publish_target(template_retained_target);
          template_complete_event(0x05);
          true
        } else false
      } else if step == 1 then {
        if template_maybe_stop_event(0x03, 0x0000_0000_0000_0000) then {
          write_reg5(template_sp(), template_sp_c);
          template_complete_event(0x03);
          true
        } else false
      } else {
        let i : int = step - 2;
        let slot : bits(64) = template_slot_addr(template_sp_c, i);
        if template_maybe_stop_event(0x04, slot) then {
          let r : bits(5) = template_reg_at(template_begin, i);
          let v : bits(64) = template_load64(slot);
          write_reg5(r, v);
          template_complete_event(0x04);
          true
        } else false
      }
    } else if form == 0b100 then {
      if step == 0 then {
        if template_maybe_stop_event(0x03, 0x0000_0000_0000_0000) then {
          write_reg5(template_sp(), template_sp_c);
          template_complete_event(0x03);
          true
        } else false
      } else if step == 1 then {
        if template_maybe_stop_event(0x06, 0x0000_0000_0000_0000) then {
          write_reg5(template_ra(), template_retained_slot0);
          template_restore_r10_count = template_restore_r10_count + 0x0000_0000_0000_0001;
          template_complete_event(0x06);
          true
        } else false
      } else if step == 2 then {
        if template_maybe_stop_event(0x05, 0x0000_0000_0000_0000) then {
          template_publish_target(template_retained_target);
          template_complete_event(0x05);
          true
        } else false
      } else {
        let i : int = step - 2;
        let slot : bits(64) = template_slot_addr(template_sp_c, i);
        if template_maybe_stop_event(0x04, slot) then {
          let r : bits(5) = template_reg_at(template_begin, i);
          let v : bits(64) = template_load64(slot);
          write_reg5(r, v);
          template_complete_event(0x04);
          true
        } else false
      }
    } else false
  }
}

function template_final_boundary() -> unit = {
  if template_valid & (template_phase == 0b10) then {
    if (template_form == 0b011) | (template_form == 0b100) then {
      barg_valid = true;
      barg_bpc_cur = template_source_pc;
      set_commit_target_value(template_retained_target);
      block_commit_boundary()
    } else ();
    template_final_count = template_final_count + 0x0000_0000_0000_0001;
    template_clear()
  } else ()
}

function template_run_current() -> unit = {
  var keep_going : bool = true;
  while keep_going & template_valid & (template_phase == 0b01) do {
    keep_going = template_execute_one_event()
  };
  if template_valid & (template_phase == 0b10) then template_final_boundary() else ()
}

function template_start_frame(form : bits(3), begin : bits(5), endv : bits(5), f : int, sp_a : bits(64), sp_c : bits(64), event_count : int) -> unit = {
  let nregs : int = template_range_count(begin, endv);
  if form == 0b001 then template_capture_entry_values(begin, nregs) else ();
  template_enter_phase1(form, read_pc_or_tpc(), begin, endv, nregs, f, sp_a, sp_c, event_count);
  template_run_current()
}

function exec_fentry(SrcBegin : bits(5), SrcEnd : bits(5), uimm15 : bits(15)) -> unit = {
  let f : int = unsigned(uimm15);
  let src_pc = read_pc_or_tpc();
  if not_bool(template_frame_legal(SrcBegin, SrcEnd, f, false)) then {
    template_record_phase0(0b001, src_pc);
    trap_illegal_inst(src_pc)
  } else {
    let c : bits(64) = read_reg5(template_sp());
    let a : bits(64) = sub_bits(c, sail_zeros(64) + f);
    template_start_frame(0b001, SrcBegin, SrcEnd, f, a, c, template_range_count(SrcBegin, SrcEnd) + 1)
  }
}

function exec_fexit(DstBegin : bits(5), DstEnd : bits(5), uimm15 : bits(15)) -> unit = {
  let f : int = unsigned(uimm15);
  let src_pc = read_pc_or_tpc();
  if not_bool(template_frame_legal(DstBegin, DstEnd, f, false)) then {
    template_record_phase0(0b010, src_pc);
    trap_illegal_inst(src_pc)
  } else {
    let a : bits(64) = read_reg5(template_sp());
    let c : bits(64) = a + (sail_zeros(64) + f);
    template_start_frame(0b010, DstBegin, DstEnd, f, a, c, template_range_count(DstBegin, DstEnd) + 1)
  }
}

function exec_fret_ra(DstBegin : bits(5), DstEnd : bits(5), uimm15 : bits(15)) -> unit = {
  let f : int = unsigned(uimm15);
  let src_pc = read_pc_or_tpc();
  if not_bool(template_frame_legal(DstBegin, DstEnd, f, false)) then {
    template_record_phase0(0b011, src_pc);
    trap_illegal_inst(src_pc)
  } else if not_bool(template_marker_proven(src_pc)) then {
    template_record_phase0(0b011, src_pc);
    trap_block_cfi(0x1, src_pc)
  } else {
    let target : bits(64) = read_reg5(template_ra());
    if not_bool(template_marker_proven(target)) then {
      template_record_phase0(0b011, src_pc);
      trap_block_cfi(0x1, src_pc)
    } else {
      let a : bits(64) = read_reg5(template_sp());
      let c : bits(64) = a + (sail_zeros(64) + f);
      template_retained_target = target;
      template_start_frame(0b011, DstBegin, DstEnd, f, a, c, template_range_count(DstBegin, DstEnd) + 2)
    }
  }
}

function exec_fret_stk(DstBegin : bits(5), DstEnd : bits(5), uimm15 : bits(15)) -> unit = {
  let f : int = unsigned(uimm15);
  let src_pc = read_pc_or_tpc();
  if not_bool(template_frame_legal(DstBegin, DstEnd, f, true)) then {
    template_record_phase0(0b100, src_pc);
    trap_illegal_inst(src_pc)
  } else if not_bool(template_marker_proven(src_pc)) then {
    template_record_phase0(0b100, src_pc);
    trap_block_cfi(0x1, src_pc)
  } else {
    let a : bits(64) = read_reg5(template_sp());
    let c : bits(64) = a + (sail_zeros(64) + f);
    let slot0 : bits(64) = template_slot_addr(c, 0);
    if not_bool(template_vload_admitted()) then {
      template_record_phase0(0b100, src_pc);
      template_vload_forbidden_zero_read_count = template_vload_forbidden_zero_read_count + 0x0000_0000_0000_0001;
      template_trap_vload_mmu_perm(slot0)
    } else {
      template_vload_read_count = template_vload_read_count + 0x0000_0000_0000_0001;
      let target : bits(64) = template_load64(slot0);
      if not_bool(template_marker_proven(target)) then {
        template_record_phase0(0b100, src_pc);
        trap_block_cfi(0x1, src_pc)
      } else {
        template_retained_slot0 = target;
        template_retained_target = target;
        template_start_frame(0b100, DstBegin, DstEnd, f, a, c, template_range_count(DstBegin, DstEnd) + 2)
      }
    }
  }
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

// Decode-only: the executable subset has no L2SPM allocator or completion
// model. Reject before operand reads or effects instead of inventing a replica.
function exec_mcopy_ds(RegDst : bits(5), RegSrc0 : bits(5), RegSrc1 : bits(5), RegSrc2 : bits(5)) -> unit = {
  trap_illegal_inst(read_pc_or_tpc())
}

function exec_mcopy_dl(RegDst : bits(5), RegSrc0 : bits(5), RegSrc1 : bits(5), RegSrc2 : bits(5)) -> unit = {
  trap_illegal_inst(read_pc_or_tpc())
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

// The extension-owned context forms reject before interpreting operands.
function exec_esave(RegSrc0 : bits(5), RegSrc1 : bits(5), RegSrc2 : bits(5)) -> unit = {
  trap_illegal_inst(read_pc_or_tpc())
}

function exec_ercov(RegSrc0 : bits(5), RegSrc1 : bits(5), RegSrc2 : bits(5)) -> unit = {
  trap_illegal_inst(read_pc_or_tpc())
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
  } else if template_valid & template_dirty & (RRA_Type == 0x0) then {
    template_integrity_assert_fail(0x01)
  } else if template_valid & template_dirty & template_resume_ok & (RRA_Type == 0x1) then {
    template_run_current()
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
function exec_bwe(SrcL : bits(5)) -> unit = {
  msgb_instruction_blocked = false;
  if not_bool(msgb_system_block()) then msgb_instruction_fault(MSGB_BSE_BAD_ENVELOPE)
  else {
    publish_execution_control(WaitEvent, read_reg5(SrcL));
    match msgb_platform_instruction_context() {
      Some(ctx) => hscb_observe_wait(ctx),
      None() => ()
    }
  }
}

function exec_bse(SrcL : bits(5)) -> unit = {
  msgb_instruction_blocked = false;
  if not_bool(msgb_system_block()) then msgb_instruction_fault(MSGB_BSE_BAD_ENVELOPE)
  // PTO selects MSGB only for the current bound kernel context.
  else match msgb_platform_instruction_context() {
    Some(ctx) if msgb_kernel_context_active(ctx, msgb_endpoints[msgb_context_index(ctx)]) =>
      match msgb_effect_preflight(ctx, false) {
        MSGB_BSE_COMPLETED => msgb_instruction_fault(msgb_bse(ctx, read_reg5(SrcL))),
        result => msgb_instruction_fault(result)
      },
    _ => publish_execution_control(SendEvent, read_reg5(SrcL))
  }
}

// -----------------------------------------------------------------------------
// PTO ISA 0.58 tile transaction envelope

function decode_pe_mode(PEMode : bits(3)) -> bits(4) = {
  match PEMode {
    0b000 => 0x0,
    0b001 => 0x8,
    0b010 => 0x4,
    0b011 => 0x2,
    0b100 => 0x1,
    0b101 => 0xC,
    0b110 => 0xE,
    _ => 0xF
  }
}

function tile_effect_begin(family : bits(2), selector : bits(5)) -> unit = {
  tile_effect_pending = true;
  tile_effect_family = family;
  tile_effect_function = selector;
  tile_effect_datatype = decoded_tile_datatype();
  tile_effect_restart_pending = false;
  tile_effect_reset_descriptors()
}

function tile_effect_append_iot(raw : bits(64)) -> unit = {
  let func : bits(3) = raw[14..12];
  let pe_mode : bits(3) = raw[11..9];
  let pe_mask : bits(4) = decode_pe_mode(pe_mode);
  let source_count : bits(6) =
    if func == 0b100 then 0b00_0010
    else if func == 0b101 then 0b00_0001
    else if func == 0b110 then 0b00_0000
    else 0b00_0000;
  let size : bits(4) = raw[18..15];
  let dst : bits(2) = raw[8..7];
  let output_active = (unsigned(size) >= 1) & (unsigned(size) <= 10);
  let last = raw[19] == 0b1;
  // PTO 0.58.6 makes PEMode=000 a strict no-effect path before placement,
  // duplicate, schema, allocation, descriptor, memory, and fault checks.
  if pe_mask == 0x0 then ()
  else if not_bool(tile_effect_iot_legal) then ()
  else if unsigned(tile_effect_iot_count) >= 4 then {
    // Fifth effective binding: Illegal Block / invalid B.IOT stream.
    trap_blockfmt(0x05, 0x01, read_pc_or_tpc());
    tile_effect_iot_legal = false
  }
  else if tile_effect_pe_mode_valid & (pe_mode != tile_effect_pe_mode) then {
    // Linx mapping of PTO Fault_TileLegality for a mismatched decoded mask.
    trap_blockfmt(0x05, 0x03, read_pc_or_tpc());
    tile_effect_iot_legal = false
  }
  else {
    if not_bool(tile_effect_pe_mode_valid) then {
      tile_effect_pe_mode_valid = true;
      tile_effect_pe_mode = pe_mode;
      tile_effect_pe_mask = pe_mask
    } else ();
    if tile_effect_last_seen then tile_effect_after_last = true else ();
    if last then tile_effect_last_seen = true else ();
    tile_effect_iot_count = tile_effect_iot_count + 0b00_0001;
    tile_effect_source_count = tile_effect_source_count + source_count;
    if output_active then tile_effect_output_count = tile_effect_output_count + 0b00_0001 else ();
    if (func != 0b100) & (func != 0b101) & (func != 0b110) then tile_effect_iot_legal = false else ();
    if (size != 0b0000) & not_bool(output_active) then tile_effect_iot_legal = false else ();
    if (func == 0b110) & not_bool(output_active) then tile_effect_iot_legal = false else ();
    // L terminates only the effective binding sequence; it never releases a
    // source in the 0.58.6 contract.
    bdesc_mark_iot()
  }
}

function tile_tlsu_required_sources(selector : bits(5)) -> bits(6) = {
  if selector == 0b00100 then 0b00_0001       // MGATHER
  else if selector == 0b00110 then 0b00_0010  // MGATHER.MASK
  else if selector == 0b00101 then 0b00_0010  // MSCATTER
  else if selector == 0b00111 then 0b00_0011  // MSCATTER.MASK
  else if selector == 0b01000 then 0b00_0011  // MGATHER.CAS
  else 0b00_0000
}

function tile_tlsu_produces_output(selector : bits(5)) -> bool = {
  (selector == 0b00100) | (selector == 0b00110) | (selector == 0b01000)
}

function tile_cube_required_sources(selector : bits(5)) -> bits(6) = {
  if (selector == 0b00000) | (selector == 0b00010) |
     (selector == 0b10000) | (selector == 0b10010) then 0b00_0010
  else if (selector == 0b00001) | (selector == 0b10001) then 0b00_0011
  else if (selector == 0b00100) | (selector == 0b00110) |
          (selector == 0b10100) | (selector == 0b10110) then 0b00_0100
  else if (selector == 0b00101) | (selector == 0b10101) then 0b00_0101
  else 0b00_0000
}

function tile_cube_is_mx(selector : bits(5)) -> bool = {
  (selector == 0b00100) | (selector == 0b00101) | (selector == 0b00110) |
  (selector == 0b10100) | (selector == 0b10101) | (selector == 0b10110)
}

function tile_cube_is_bias(selector : bits(5)) -> bool = {
  (selector == 0b00001) | (selector == 0b00101) |
  (selector == 0b10001) | (selector == 0b10101)
}

function tile_cube_is_accumulate(selector : bits(5)) -> bool = {
  (selector == 0b00010) | (selector == 0b00110) |
  (selector == 0b10010) | (selector == 0b10110)
}

function tile_numeric_ordinary(dtype : bits(5)) -> bool = {
  (unsigned(dtype) <= 12) | (dtype == 0b01110) |
  ((unsigned(dtype) >= 16) & (unsigned(dtype) <= 20)) |
  ((unsigned(dtype) >= 24) & (unsigned(dtype) <= 28))
}

function tile_cube_dim(value : bits(64)) -> bits(64) = {
  value
}

function tile_effect_header_legal() -> bool = {
  if tile_effect_family == 0b01 then {
    if tile_effect_function == 0b00011 then {
      // TPREFETCH has scalar address/byte-count operands and no Tile IO.
      bdesc_seen_datr & bdesc_seen_ior &
      (tile_effect_iot_count == 0b00_0000)
    } else {
      let required = tile_tlsu_required_sources(tile_effect_function);
      let output_ok =
        if tile_tlsu_produces_output(tile_effect_function) then tile_effect_output_count == 0b00_0001
        else tile_effect_output_count == 0b00_0000;
      (required != 0b00_0000) & bdesc_seen_datr & bdesc_seen_ior & bdesc_seen_iot &
      tile_effect_iot_legal & tile_effect_last_seen &
      not_bool(tile_effect_after_last) & (unsigned(tile_effect_iot_count) <= 4) &
      (tile_effect_source_count == required) & output_ok &
      ((tile_effect_function != 0b01000) | (bcatr_raw[17] == 0b1))
    }
  } else if tile_effect_family == 0b10 then {
    let required = tile_cube_required_sources(tile_effect_function);
    let mx = tile_cube_is_mx(tile_effect_function);
    let accumulate = tile_cube_is_accumulate(tile_effect_function);
    let m = tile_cube_dim(ssr_lb0);
    let n = tile_cube_dim(ssr_lb1);
    let k = tile_cube_dim(ssr_lb2);
    let dtype_ok = if mx then tile_effect_datatype == 0b00001 else tile_numeric_ordinary(tile_effect_datatype);
    let acc_ok =
      if accumulate then tile_acc_valid & (tile_acc_rows == m) & (tile_acc_cols == n) &
        (tile_acc_k == k) & (tile_acc_datatype == (if mx then 0b00001 else tile_effect_datatype))
      else true;
    let dimensions_ok = (m != sail_zeros(64)) & (n != sail_zeros(64)) &
      (k != sail_zeros(64));
    (required != 0b00_0000) & bdesc_seen_datr & bdesc_seen_iot & dimensions_ok &
    bdesc_seen_fpatr &
    tile_effect_iot_legal & tile_effect_last_seen &
    not_bool(tile_effect_after_last) & (unsigned(tile_effect_iot_count) <= 4) &
    (tile_effect_source_count == required) &
    (tile_effect_output_count == 0b00_0000) & dtype_ok & acc_ok
  } else false
}

function tile_effect_publish() -> unit = {
  let family = tile_effect_family;
  let selector = tile_effect_function;
  let mx = (family == 0b10) & tile_cube_is_mx(selector);
  let bias = (family == 0b10) & tile_cube_is_bias(selector);
  let accumulate = (family == 0b10) & tile_cube_is_accumulate(selector);
  tile_effect_preflight_seq = tile_effect_preflight_seq + 1;
  tile_effect_commit_seq = tile_effect_commit_seq + 1;
  tile_effect_lifetime_releases = tile_effect_lifetime_releases + sail_zero_extend(tile_effect_release_count, 64);
  tile_effect_last_family = family;
  tile_effect_last_function = selector;
  tile_effect_last_datatype = tile_effect_datatype;
  tile_effect_last_masked = (family == 0b01) & ((selector == 0b00110) | (selector == 0b00111));
  tile_effect_last_mask_suppresses_access = tile_effect_last_masked;
  tile_effect_last_pad = bdatr_raw[28..27];
  tile_effect_last_mx = mx;
  tile_effect_last_bias = bias;
  tile_effect_last_accumulate = accumulate;
  if family == 0b01 then {
    if selector != 0b00011 then tile_effect_memory_seq = tile_effect_memory_seq + 1 else ();
    if tile_tlsu_produces_output(selector) then tile_effect_tile_seq = tile_effect_tile_seq + 1 else ()
  } else if family == 0b10 then {
    let m = tile_cube_dim(ssr_lb0);
    let n = tile_cube_dim(ssr_lb1);
    let k = tile_cube_dim(ssr_lb2);
    tile_effect_acc_seq = tile_effect_acc_seq + 1;
    tile_acc_valid = true;
    tile_acc_datatype = if mx then 0b00001 else tile_effect_datatype;
    tile_acc_rows = m;
    tile_acc_cols = n;
    tile_acc_k = k;
    if mx then {
      let groups_i : int = tdiv_int(unsigned(k) + 31, 32);
      let groups : bits(64) = sail_zeros(64) + groups_i;
      tile_effect_last_scale_a_rows = m;
      tile_effect_last_scale_a_cols = groups;
      tile_effect_last_scale_b_rows = groups;
      tile_effect_last_scale_b_cols = n;
      // B.IOT authored source order: A, B, ScaleA, ScaleB, optional Bias.
      tile_effect_last_scale_a_source = 0b00_0010;
      tile_effect_last_scale_b_source = 0b00_0011
    } else ()
  } else ();
  tile_effect_pending = false;
  tile_effect_restart_pending = false
}

function tile_effect_finalize() -> bool = {
  if not_bool(tile_effect_pending) then true
  else if not_bool(tile_effect_header_legal()) then {
    // Descriptor/operand preflight fails before every architectural effect.
    trap_blockfmt(0x05, 0x01, read_pc_or_tpc());
    tile_effect_restart_pending = true;
    false
  } else if not_bool(tile_effect_access_set_valid) then {
    // The host memory/IOMMU hook reports the first failing original address.
    trap_data_page_fault(tile_effect_fault_address);
    tile_effect_restart_pending = true;
    false
  } else {
    tile_effect_publish();
    true
  }
}

// -----------------------------------------------------------------------------
// CMD: Block boundary markers (BSTART/BSTOP)
//
// Normative: docs/architecture/isa-manual/src/chapters/04_block_isa.adoc and
// docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc.
//
// Architectural rule: every control-flow target must land on a block start marker;
// violations trap with E_BLOCK(EC_CFI), kind=CFI_BAD_TARGET.

function exec_bstart_transition() -> bool = {
  // Generic BSTART (COND, <label>) form.
  // - Terminates previous block (commit boundary).
  // - Starts a new block and initializes BARG.
  // - Records block type/xfer kind/next target for commit.
  //
  // Decoder provides block metadata and target.
  let tgt = decoded_block_target_pc();
  if not_bool(is_block_start_marker(tgt)) then {
    // EC_CFI_KIND=1 (CFI_BAD_TARGET)
    trap_block_cfi(0x1, read_pc_or_tpc());
    false
  } else if tile_effect_pending & not_bool(tile_effect_finalize()) then {
    // A next BSTART also terminates the prior header.  Failed preflight leaves
    // the old operation pending and must not install the new block.
    false
  } else {
    block_commit_boundary();
    barg_reset_at_block_start();
    // Reset descriptor-seen state for the new block header.
    bdesc_reset();
    barg_set_block_type(decoded_block_type());
    barg_set_xfer_kind(decoded_block_xfer_kind());
    barg_set_next_pc_target(tgt);
    true
  }
}

function exec_bstart() -> unit = { let _accepted = exec_bstart_transition(); () }

function bstart_target_preflight() -> bool = {
  let tgt = decoded_block_target_pc();
  if not_bool(is_block_start_marker(tgt)) then {
    trap_block_cfi(0x1, read_pc_or_tpc());
    false
  } else true
}

function exec_cube_bstart() -> unit = {
  if not_bool(bstart_target_preflight()) then ()
  else if cube_first_use_enabled() then trap_cube_first_use()
  else exec_bstart()
}

function exec_tile_bstart(family : bits(2), selector : bits(5)) -> unit = {
  if (family == 0b10) & not_bool(bstart_target_preflight()) then {
    ()
  } else if (family == 0b10) & cube_first_use_enabled() then {
    trap_cube_first_use()
  } else if exec_bstart_transition() then tile_effect_begin(family, selector) else ()
}

// Typed 32/48-bit BSTART variants share the same boundary semantics; the decoder
// distinguishes the specific block type/xfer kind encoding.
function exec_bstart_std() -> unit = { exec_bstart() }
function exec_bstart_fp() -> unit = { exec_bstart() }
function exec_bstart_sys() -> unit = { exec_bstart() }
function exec_bstart_cube() -> unit = { exec_cube_bstart() }
function exec_bstart_tepl() -> unit = { exec_bstart() }
function exec_bstart_tload() -> unit = { exec_bstart() }
function exec_bstart_tstore() -> unit = { exec_bstart() }
function exec_bstart_tmov() -> unit = { exec_bstart() }
function exec_bstart_tmatmul() -> unit = { exec_tile_bstart(0b10, 0b00000) }
function exec_bstart_tmatmul_acc() -> unit = { exec_tile_bstart(0b10, 0b00010) }
function exec_bstart_mgather() -> unit = { exec_tile_bstart(0b01, 0b00100) }
function exec_bstart_mgather_cas() -> unit = { exec_tile_bstart(0b01, 0b01000) }
function exec_bstart_mgather_mask() -> unit = { exec_tile_bstart(0b01, 0b00110) }
function exec_bstart_mscatter() -> unit = { exec_tile_bstart(0b01, 0b00101) }
function exec_bstart_mscatter_mask() -> unit = { exec_tile_bstart(0b01, 0b00111) }
// PTO 0.58.6 adds the GM atomic/reduction and TIMG2COL start forms. Their
// exact encodings are decoded here, while the Linx Sail transaction model
// deliberately fails closed until it represents their full operand and
// atomic-publication contracts. semantics_policy.json grades these forms as
// decode-only so this cannot be mistaken for executable semantic coverage.
function exec_bstart_mgather_exch(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mgather_max(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mgather_min(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mgather_add(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mgather_inc(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mgather_dec(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mgather_and(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mgather_or(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mgather_xor(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mscatter_max(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mscatter_min(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mscatter_add(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mscatter_inc(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mscatter_dec(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mscatter_and(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mscatter_or(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mscatter_xor(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_mscatter_popc(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_timg2col(DataType : bits(5)) -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
function exec_bstart_tgemv() -> unit = { exec_tile_bstart(0b10, 0b10000) }
function exec_bstart_tgemv_acc() -> unit = { exec_tile_bstart(0b10, 0b10010) }
function exec_bstart_tgemv_bias() -> unit = { exec_tile_bstart(0b10, 0b10001) }
function exec_bstart_tgemvmx() -> unit = { exec_tile_bstart(0b10, 0b10100) }
function exec_bstart_tgemvmx_acc() -> unit = { exec_tile_bstart(0b10, 0b10110) }
function exec_bstart_tgemvmx_bias() -> unit = { exec_tile_bstart(0b10, 0b10101) }
function exec_bstart_tmatmul_bias() -> unit = { exec_tile_bstart(0b10, 0b00001) }
function exec_bstart_tmatmulmx() -> unit = { exec_tile_bstart(0b10, 0b00100) }
function exec_bstart_tmatmulmx_acc() -> unit = { exec_tile_bstart(0b10, 0b00110) }
function exec_bstart_tmatmulmx_bias() -> unit = { exec_tile_bstart(0b10, 0b00101) }
function exec_bstart_tprefetch() -> unit = { exec_tile_bstart(0b01, 0b00011) }
function exec_bstart_gmov(DataType : bits(5)) -> unit = {
  let _datatype = DataType;
  exec_tile_bstart(0b01, 0b01101)
}
function exec_fused_bstart_call(uimm5 : bits(5), embedded_setret_bytes : bits(64)) -> unit = {
  // The exact aggregate form is one atomic CALL transition composed from a
  // block-start target and an embedded C.SETRET.  The fields are independent:
  // simm12/simm25 selects decoded_block_target_pc(), while uimm5 selects ra.
  let tgt = decoded_block_target_pc();
  if not_bool(is_block_start_marker(tgt)) then {
    trap_block_cfi(0x1, read_pc_or_tpc())
  } else if tile_effect_pending & not_bool(tile_effect_finalize()) then {
    ()
  } else {
    let return_base = read_pc_or_tpc() + embedded_setret_bytes;
    let return_off = sail_shiftleft(sail_zero_extend(uimm5, 64), 1);
    block_commit_boundary();
    barg_reset_at_block_start();
    bdesc_reset();
    barg_set_block_type(decoded_block_type());
    barg_set_xfer_kind(block_xfer_call());
    barg_set_next_pc_target(tgt);
    write_regdst(0b01010, return_base + return_off)
  }
}

function exec_bstart_call(uimm5 : bits(5)) -> unit = {
  exec_fused_bstart_call(uimm5, sail_zeros(64) + 2)
}

function exec_bstart_icall(uimm5 : bits(5)) -> unit = {
  let source_pc = read_pc_or_tpc();
  let target = barg_bpc_tgt;
  let retiring_type_legal =
    (barg_block_type_cur == 0b0000) | (barg_block_type_cur == 0b0010);
  if not_bool(barg_valid & retiring_type_legal) then {
    trap_blockfmt(0x00, 0x02, source_pc)
  } else if target[0] == 0b1 then {
    trap_block_cfi(0x1, source_pc)
  } else if tile_effect_pending & not_bool(tile_effect_finalize()) then {
    ()
  } else {
    let return_off = sail_shiftleft(sail_zero_extend(uimm5, 64), 1);
    block_commit_boundary();
    barg_reset_at_block_start();
    bdesc_reset();
    barg_set_block_type(0b0000);
    barg_set_xfer_kind(block_xfer_icall());
    barg_set_next_pc_target(target);
    write_regdst(0b01010, source_pc + 2 + return_off)
  }
}

function exec_hl_bstart_call(uimm5 : bits(5)) -> unit = {
  exec_fused_bstart_call(uimm5, sail_zeros(64) + 4)
}

function exec_hl_bstart_std() -> unit = { exec_bstart() }
function exec_hl_bstart_fp() -> unit = { exec_bstart() }
function exec_hl_bstart_sys() -> unit = { exec_bstart() }

function exec_c_bstart() -> unit = { exec_bstart() }
function exec_c_bstart_std() -> unit = { exec_bstart() }
function exec_c_bstart_fp() -> unit = { exec_bstart() }
function exec_c_bstart_sys() -> unit = { exec_bstart() }

function exec_bstop() -> unit = {
  // Explicit block terminator.
  // For Tile headers, perform mandatory-descriptor validation at
  // the end of the header stream before committing the boundary.
  if tile_effect_pending then {
    if tile_effect_finalize() then block_commit_boundary() else ()
  } else {
    bdesc_validate_header_end(read_pc_or_tpc());
    block_commit_boundary()
  }
}

function exec_c_bstop() -> unit = { exec_bstop() }
function exec_l_bstop() -> unit = { exec_bstop() }

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
function exec_b_ios(SharedTileID : bits(6), SizeCode : bits(4), PEMode : bits(3)) -> unit = {
  // Role is consumed by the surrounding BSTART schema. The architectural
  // index is absolute (S0..S63). PEMode expands to the fixed four-PE mask;
  // mode zero is a strict no-op and does not mutate descriptors.
  let pe_mask = decode_pe_mode(PEMode);
  if pe_mask == 0x0 then ()
  else {
    shared_tile_binding_id = sail_zero_extend(SharedTileID, 8);
    shared_tile_binding_pe_mode = PEMode;
    shared_tile_binding_pe_mask = pe_mask;
    shared_tile_binding_size_code = SizeCode;
    shared_tile_binding_valid = true;
    bdesc_mark_iot()
  }
}

function bior_selector_legal(selector : bits(5)) -> bool = {
  unsigned(selector) < 24
}

function exec_b_ior() -> unit = {
  let src0 = decoded_bior_regsrc0();
  let src1 = decoded_bior_regsrc1();
  let src2 = decoded_bior_regsrc2();
  let dst = decoded_bior_regdst();
  let execmask = decoded_bior_execmask();
  if not_bool(bior_selector_legal(src0) & bior_selector_legal(src1) &
      bior_selector_legal(src2) & bior_selector_legal(dst)) then
    trap_illegal_inst(read_pc_or_tpc())
  else if bior_record_count == 0b10 then
    trap_blockfmt(0x04, 0x02, read_pc_or_tpc())
  else if (bior_record_count == 0b01) & (bior0_execmask == 0b1) then
    trap_blockfmt(0x04, 0x02, read_pc_or_tpc())
  else if (bior_record_count == 0b01) & (dst != 0b00000) then
    trap_blockfmt(0x04, 0x02, read_pc_or_tpc())
  else {
    bior_store_record(src0, src1, src2, dst, execmask);
    bdesc_mark_ior()
  }
}
function exec_b_iot() -> unit = { tile_effect_append_iot(decoded_biot_raw()) }

// PTO 0.58.6 range modifiers are present in the canonical decoder, but their
// generation/range state is not yet represented in this Sail subset. Reject
// them before effects and keep their coverage grade decode-only.
function exec_b_subview(SrcSelect : bits(1), uimm11 : bits(11), RegSrc : bits(5), SubviewSizeCode : bits(4)) -> unit = {
  trap_illegal_inst(read_pc_or_tpc())
}

function exec_b_assemble(INIT : bits(1), uimm11 : bits(11), RegSrc : bits(5), LAST : bits(1), WriterSizeCode : bits(4)) -> unit = {
  trap_illegal_inst(read_pc_or_tpc())
}

function exec_b_catr() -> unit = {
  // Staged semantics: latch raw control-attribute word so DR (bit 26) can be consulted.
  bcatr_raw = decoded_bcatr_raw()
}

function exec_b_datr() -> unit = {
  // Staged semantics: latch raw data-attribute word so datatype/layout/rmode/sat can be consulted.
  bdatr_raw = decoded_bdatr_raw();
  bdesc_mark_datr()
}
function exec_b_fpatr(PreQuantMode : bits(6), ReluMode : bits(3), GroupNCode : bits(4), RowMaxEn : bits(1), GroupMaxEn : bits(1), RowMaxInit : bits(1), MaxAbsEn : bits(1), TransA : bits(1), TransB : bits(1)) -> unit = {
  let row_max = RowMaxEn == 0b1;
  let group_max = GroupMaxEn == 0b1;
  let row_init = RowMaxInit == 0b1;
  let max_abs = MaxAbsEn == 0b1;
  let legal_combination =
    (not_bool(row_init) | row_max) &
    ((GroupNCode == 0x0) == not_bool(group_max)) &
    (not_bool(max_abs) | row_max | group_max);
  let legal_position =
    tile_effect_pending & (tile_effect_family == 0b10) &
    not_bool(bdesc_seen_fpatr) & not_bool(bdesc_seen_ior) &
    not_bool(bdesc_seen_iot);
  if not_bool(legal_position & legal_combination) then {
    trap_blockfmt(0x06, 0x02, read_pc_or_tpc())
  } else {
    bfpatr_pre_quant_mode = PreQuantMode;
    bfpatr_relu_mode = ReluMode;
    bfpatr_group_n_code = GroupNCode;
    bfpatr_row_max_en = row_max;
    bfpatr_group_max_en = group_max;
    bfpatr_row_max_init = row_init;
    bfpatr_max_abs_en = max_abs;
    bfpatr_trans_a = TransA == 0b1;
    bfpatr_trans_b = TransB == 0b1;
    bdesc_mark_fpatr()
  }
}
function exec_b_hint() -> unit = { () }
// -----------------------------------------------------------------------------
function exec_xb(acr_id : bits(12), cross_bid : bits(8)) -> unit = {
  trap_illegal_inst(read_pc_or_tpc())
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
// AGU / Load-Store (staged bring-up; strict v0.57 conventions)
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

function exec_casb(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), rl : bits(1)) -> unit = {
  exec_hl_casb(RegDst, SrcL, SrcR, SrcD, aq, 0b0, rl)
}

function exec_cash(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), rl : bits(1)) -> unit = {
  exec_hl_cash(RegDst, SrcL, SrcR, SrcD, aq, 0b0, rl)
}

function exec_casw(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), rl : bits(1)) -> unit = {
  exec_hl_casw(RegDst, SrcL, SrcR, SrcD, aq, 0b0, rl)
}

function exec_casd(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), rl : bits(1)) -> unit = {
  exec_hl_casd(RegDst, SrcL, SrcR, SrcD, aq, 0b0, rl)
}

function exec_dma(SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let _ = SrcL; let _ = SrcR;
  trap_illegal_inst(read_pc_or_tpc())
}

// Decode-only until L2SPM allocation/release and completion are modeled.
function exec_dma_free_s(SrcL : bits(5)) -> unit = {
  trap_illegal_inst(read_pc_or_tpc())
}

function exec_dma_free_l(SrcL : bits(5)) -> unit = {
  trap_illegal_inst(read_pc_or_tpc())
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

function rmw8_add(a : bits(8), b : bits(8)) -> bits(8) = { a + b }
function rmw8_sub(a : bits(8), b : bits(8)) -> bits(8) = { sub_bits(a, b) }
function rmw16_add(a : bits(16), b : bits(16)) -> bits(16) = { a + b }
function rmw16_sub(a : bits(16), b : bits(16)) -> bits(16) = { sub_bits(a, b) }
function rmw32_sub(a : bits(32), b : bits(32)) -> bits(32) = { sub_bits(a, b) }
function rmw64_sub(a : bits(64), b : bits(64)) -> bits(64) = { sub_bits(a, b) }

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

function exec_sw_add(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_add(old, b));
  ()
}

function exec_sw_and(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_and(old, b));
  ()
}

function exec_sw_or(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_or(old, b));
  ()
}

function exec_sw_xor(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_xor(old, b));
  ()
}

function exec_sw_smax(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_smax(old, b));
  ()
}

function exec_sw_smin(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_smin(old, b));
  ()
}

function exec_sw_umax(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_umax(old, b));
  ()
}

function exec_sw_umin(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_umin(old, b));
  ()
}

function exec_sd_add(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_add(old, b));
  ()
}

function exec_sd_and(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_and(old, b));
  ()
}

function exec_sd_or(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_or(old, b));
  ()
}

function exec_sd_xor(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_xor(old, b));
  ()
}

function exec_sd_smax(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_smax(old, b));
  ()
}

function exec_sd_smin(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_smin(old, b));
  ()
}

function exec_sd_umax(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_umax(old, b));
  ()
}

function exec_sd_umin(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_umin(old, b));
  ()
}

// v0.58 store-op subtract (SW.SUB/SD.SUB) and byte/halfword size-override
// (SB.ADD/SB.SUB/SH.ADD/SH.SUB).  The S/L-store-op forms share the [SrcL], SrcR
// shape with the SW/SD slot and carry no far/aq bits.

function exec_sw_sub(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(32) = mem_load32_le(ea);
  let b : bits(32) = read_reg5(SrcR)[31..0];
  mem_store32_le(ea, rmw32_sub(old, b));
  ()
}

function exec_sd_sub(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(64) = mem_load64_le(ea);
  let b : bits(64) = read_reg5(SrcR);
  mem_store64_le(ea, rmw64_sub(old, b));
  ()
}

function exec_sb_add(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(8) = read_mem8(ea);
  let b : bits(8) = read_reg5(SrcR)[7..0];
  write_mem8(ea, rmw8_add(old, b))
}

function exec_sb_sub(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(8) = read_mem8(ea);
  let b : bits(8) = read_reg5(SrcR)[7..0];
  write_mem8(ea, rmw8_sub(old, b))
}

function exec_sh_add(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(16) = mem_load16_le(ea);
  let b : bits(16) = read_reg5(SrcR)[15..0];
  mem_store16_le(ea, rmw16_add(old, b))
}

function exec_sh_sub(SrcL : bits(5), SrcR : bits(5), rl : bits(1)) -> unit = {
  let _ = rl;
  let ea = read_reg5(SrcL);
  let old : bits(16) = mem_load16_le(ea);
  let b : bits(16) = read_reg5(SrcR)[15..0];
  mem_store16_le(ea, rmw16_sub(old, b))
}

// NOTE: mem_load{16,32,64}_le are provided by the staged memory model (state/memory.sail).

function exec_lb(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, sext8_from8(b))
}

function exec_lbu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, zext8_from8(b))
}

function exec_lh(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}

function exec_lhu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}

function exec_lw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}

function exec_lwu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (sail_shiftleft(off1, sh));
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}

function exec_ld(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
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
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let ea = base + off1;
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(ea, v)
}

function exec_sh(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let ea = base + (sail_shiftleft(off1, 1));
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}

function exec_sw(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let ea = base + (sail_shiftleft(off1, 2));
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}

function exec_sd(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let ea = base + (sail_shiftleft(off1, 3));
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v)
}

// Unscaled store variants (.U): no implicit <<{1,2,3} scaling.

function exec_sh_u(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let ea = base + off1;
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}

function exec_sw_u(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
  let ea = base + off1;
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}

function exec_sd_u(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_address_srcrtype64(SrcRType, off0);
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

function ea_pcr17(simm17 : bits(17), scale : int) -> bits(64) = {
  scalar_pcr_address(read_pc_or_tpc(), sext17_to64(simm17), scale)
}

function exec_lb_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let b : bits(8) = read_mem8(ea);
    write_scalar_gpr_or_discard(RegDst, sext8_from8(b))
  }
}

function exec_lbu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let b : bits(8) = read_mem8(ea);
    write_scalar_gpr_or_discard(RegDst, zext8_from8(b))
  }
}

function exec_lh_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let h : bits(16) = mem_load16_le(ea);
    write_scalar_gpr_or_discard(RegDst, sext16_from16(h))
  }
}

function exec_lhu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let h : bits(16) = mem_load16_le(ea);
    write_scalar_gpr_or_discard(RegDst, zext16_from16(h))
  }
}

function exec_lw_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let w : bits(32) = mem_load32_le(ea);
    write_scalar_gpr_or_discard(RegDst, sext32_from32(w))
  }
}

function exec_lwu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let w : bits(32) = mem_load32_le(ea);
    write_scalar_gpr_or_discard(RegDst, zext32_from32(w))
  }
}

function exec_ld_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let d : bits(64) = mem_load64_le(ea);
    write_scalar_gpr_or_discard(RegDst, d)
  }
}

function exec_sb_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_source_supported(SrcD)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let v : bits(8) = read_reg5(SrcD)[7..0];
    write_mem8(ea, v)
  }
}

function exec_sh_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_source_supported(SrcD)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let v : bits(16) = read_reg5(SrcD)[15..0];
    mem_store16_le(ea, v)
  }
}

function exec_sw_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_source_supported(SrcD)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let v : bits(32) = read_reg5(SrcD)[31..0];
    mem_store32_le(ea, v)
  }
}

function exec_sd_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  if not_bool(scalar_gpr_source_supported(SrcD)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = ea_pcr17(simm17, 2);
    let v : bits(64) = read_reg5(SrcD);
    mem_store64_le(ea, v)
  }
}

// -----------------------------------------------------------------------------
// HL (48-bit) pre/post-index loads/stores.
// Contract (per decision):
//   - PR: new_base = base + off; access at new_base; Dst1/Rd = new_base
//   - PO: access at base; new_base = base + off; Dst1/Rd = new_base
// off = sail_shiftleft(apply_address_srcrtype64(SrcRType, SrcR), shamt_or_scale)

function hl_off_shamt(SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> bits(64) = {
  let idx0 = read_reg5(SrcR);
  let idx1 = apply_address_srcrtype64(SrcRType, idx0);
  (sail_shiftleft(idx1, unsigned(shamt)))
}

function hl_off_scale(SrcR : bits(5), SrcRType : bits(2), scale : int) -> bits(64) = {
  let idx0 = read_reg5(SrcR);
  let idx1 = apply_address_srcrtype64(SrcRType, idx0);
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
// - .PCR uses the form's catalog offset scale after sign extension.
// - *I uses long immediate simm22 with scaled offset by element size.
// - *I.U uses unscaled immediate simm22.
// - *I.PR/*I.PO use simm17 with writeback to Dst1 (per PR/PO contract).
// - *I.UPR/*I.UPO are unscaled pre/post-index (simm17) with writeback.
// - *IP/*P are pair forms: Dst0=mem[EA], Dst1=mem[EA+elem_size]. No writeback.

function hl_ea_pcr(simm : bits(29), scale : int) -> bits(64) = {
  scalar_pcr_address(read_pc_or_tpc(), sext29_to64(simm), scale)
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
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let b : bits(8) = read_mem8(ea);
    write_scalar_gpr_or_discard(RegDst, sext8_from8(b))
  }
}
function exec_hl_lbu_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let b : bits(8) = read_mem8(ea);
    write_scalar_gpr_or_discard(RegDst, zext8_from8(b))
  }
}
function exec_hl_lh_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let h : bits(16) = mem_load16_le(ea);
    write_scalar_gpr_or_discard(RegDst, sext16_from16(h))
  }
}
function exec_hl_lhu_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let h : bits(16) = mem_load16_le(ea);
    write_scalar_gpr_or_discard(RegDst, zext16_from16(h))
  }
}
function exec_hl_lw_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let w : bits(32) = mem_load32_le(ea);
    write_scalar_gpr_or_discard(RegDst, sext32_from32(w))
  }
}
function exec_hl_lwu_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let w : bits(32) = mem_load32_le(ea);
    write_scalar_gpr_or_discard(RegDst, zext32_from32(w))
  }
}
function exec_hl_ld_pcr(RegDst : bits(5), simm17 : bits(29)) -> unit = {
  if not_bool(scalar_gpr_or_discard_destination_supported(RegDst)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let d : bits(64) = mem_load64_le(ea);
    write_scalar_gpr_or_discard(RegDst, d)
  }
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
  if not_bool(scalar_gpr_source_supported(SrcD)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let v : bits(8) = read_reg5(SrcD)[7..0];
    write_mem8(ea, v)
  }
}
function exec_hl_sh_pcr(SrcD : bits(5), simm17 : bits(29)) -> unit = {
  if not_bool(scalar_gpr_source_supported(SrcD)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let v : bits(16) = read_reg5(SrcD)[15..0];
    mem_store16_le(ea, v)
  }
}
function exec_hl_sw_pcr(SrcD : bits(5), simm17 : bits(29)) -> unit = {
  if not_bool(scalar_gpr_source_supported(SrcD)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let v : bits(32) = read_reg5(SrcD)[31..0];
    mem_store32_le(ea, v)
  }
}
function exec_hl_sd_pcr(SrcD : bits(5), simm17 : bits(29)) -> unit = {
  if not_bool(scalar_gpr_source_supported(SrcD)) then trap_illegal_inst(read_pc_or_tpc()) else {
    let ea = hl_ea_pcr(simm17, 2);
    let v : bits(64) = read_reg5(SrcD);
    mem_store64_le(ea, v)
  }
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
  let ea = read_reg5(SrcL) + apply_address_srcrtype64(SrcRType, read_reg5(SrcR));
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
  let ea = read_reg5(SrcL) + apply_address_srcrtype64(SrcRType, read_reg5(SrcR));
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
  let ea = read_reg5(SrcL) + apply_address_srcrtype64(SrcRType, read_reg5(SrcR));
  let v0 : bits(64) = read_reg5(SrcD0);
  let v1 : bits(64) = read_reg5(SrcD1);
  mem_store64_le(ea, v0);
  mem_store64_le(ea + (sail_zeros(64) + 8), v1)
}

// SYNC.CORE is decoded; the single-context Sail subset has no four-PE rendezvous.
function exec_sync_core() -> unit = { trap_illegal_inst(read_pc_or_tpc()) }
