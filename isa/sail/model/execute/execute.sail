// LinxISA execute semantics (bring-up; v0.3).

// This file will be grown incrementally. For now, it provides helpers and a
// minimal ALU subset.

// NOTE: Baseline policy (per user): implement semantics according to the
// current manual + golden, and leave ambiguous behavior unimplemented until
// confirmed.

// include state + common helpers

include "../lib/common.sail"
include "../state/state.sail"

// ALU helpers.

function exec_add(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b1 = apply_srcrtype_arith64(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b = b1 << sh;
  let r = a + b;
  write_regdst(RegDst, r)
}

function exec_sub(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b1 = apply_srcrtype_arith64(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b = b1 << sh;
  let r = a - b;
  write_regdst(RegDst, r)
}

function exec_and(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b1 = apply_srcrtype_logic64(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b = b1 << sh;
  let r = a & b;
  write_regdst(RegDst, r)
}

function exec_or(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b1 = apply_srcrtype_logic64(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b = b1 << sh;
  let r = a | b;
  write_regdst(RegDst, r)
}

function exec_xor(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b0 = read_reg5(SrcR);
  let b1 = apply_srcrtype_logic64(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b = b1 << sh;
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

// HL (48-bit) arithmetic-immediate forms: same arithmetic semantics with 24-bit unsigned immediates.

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
  let imm : bits(32) = zext24_to64(uimm24)[31..0];
  let r : bits(32) = a + imm;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_hl_subiw(RegDst : bits(5), SrcL : bits(5), uimm24 : bits(24)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let imm : bits(32) = zext24_to64(uimm24)[31..0];
  let r : bits(32) = a - imm;
  write_regdst(RegDst, sext32_from32(r))
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
  let b : bits(32) = b1 << sh;
  let r : bits(32) = a + b;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_subw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let b0 = read_reg5(SrcR);
  let b1 : bits(32) = apply_srcrtype_arith32(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b : bits(32) = b1 << sh;
  let r : bits(32) = a - b;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_andw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let b0 = read_reg5(SrcR);
  let b1 : bits(32) = apply_srcrtype_logic32(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b : bits(32) = b1 << sh;
  let r : bits(32) = a & b;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_orw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let b0 = read_reg5(SrcR);
  let b1 : bits(32) = apply_srcrtype_logic32(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b : bits(32) = b1 << sh;
  let r : bits(32) = a | b;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_xorw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let b0 = read_reg5(SrcR);
  let b1 : bits(32) = apply_srcrtype_logic32(SrcRType, b0);
  let sh : int = unsigned(shamt);
  let b : bits(32) = b1 << sh;
  let r : bits(32) = a ^ b;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_addiw(RegDst : bits(5), SrcL : bits(5), uimm12 : bits(12)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let imm : bits(32) = (0x0000_0000 | uimm12);
  let r : bits(32) = a + imm;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_subiw(RegDst : bits(5), SrcL : bits(5), uimm12 : bits(12)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let imm : bits(32) = (0x0000_0000 | uimm12);
  let r : bits(32) = a - imm;
  write_regdst(RegDst, sext32_from32(r))
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
  write_regdst(RegDst, a << sh)
}

function exec_srl(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(mask_shamt64(read_reg5(SrcR)));
  write_regdst(RegDst, a >> sh)
}

function exec_sra(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(mask_shamt64(read_reg5(SrcR)));
  write_regdst(RegDst, ashr64(a, sh))
}

function exec_slli(RegDst : bits(5), SrcL : bits(5), shamt : bits(6)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  write_regdst(RegDst, a << sh)
}

function exec_srli(RegDst : bits(5), SrcL : bits(5), shamt : bits(6)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  write_regdst(RegDst, a >> sh)
}

function exec_srai(RegDst : bits(5), SrcL : bits(5), shamt : bits(6)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  write_regdst(RegDst, ashr64(a, sh))
}

function exec_sllw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let sh : int = unsigned(mask_shamt32(read_reg5(SrcR)));
  let r : bits(32) = a << sh;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_srlw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let sh : int = unsigned(mask_shamt32(read_reg5(SrcR)));
  let r : bits(32) = a >> sh;
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
  let r : bits(32) = a << sh;
  write_regdst(RegDst, sext32_from32(r))
}

function exec_srliw(RegDst : bits(5), SrcL : bits(5), shamt : bits(5)) -> unit = {
  let a : bits(32) = read_reg5(SrcL)[31..0];
  let sh : int = unsigned(shamt);
  let r : bits(32) = a >> sh;
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
  write_regdst(RegDst, a << sh)
}

function exec_c_srli(RegDst : bits(5), SrcL : bits(5), imm5 : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(imm5);
  write_regdst(RegDst, a >> sh)
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
  let ea = base + (off << 2);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(reg_t(), sext32_from32(w))
}

function exec_c_ldi(SrcL : bits(5), simm5 : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext5_to64(simm5);
  let ea = base + (off << 3);
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(reg_t(), d)
}

function exec_c_swi(SrcL : bits(5), simm5 : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext5_to64(simm5);
  let ea = base + (off << 2);
  let v : bits(32) = read_reg5(reg_t1())[31..0];
  mem_store32_le(ea, v)
}

function exec_c_sdi(SrcL : bits(5), simm5 : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off = sext5_to64(simm5);
  let ea = base + (off << 3);
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

function exec_c_ebreak(imm5 : bits(5)) -> unit = {
  // Semantics are identical to EBREAK; imm is for debugger patching heuristics.
  let _ = imm5;
  exec_ebreak()
}

function exec_c_sext_b(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[7..0];
  // Sign-extend from bit 7.
  if a[7] == 1b1 then write_regdst(reg_t(), 0xFFFF_FFFF_FFFF_FF00 | a)
  else write_regdst(reg_t(), 0x0000_0000_0000_0000 | a)
}

function exec_c_sext_h(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[15..0];
  if a[15] == 1b1 then write_regdst(reg_t(), 0xFFFF_FFFF_FFFF_0000 | a)
  else write_regdst(reg_t(), 0x0000_0000_0000_0000 | a)
}

function exec_c_sext_w(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[31..0];
  write_regdst(reg_t(), sext32_from32(a))
}

function exec_c_zext_b(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[7..0];
  write_regdst(reg_t(), 0x0000_0000_0000_0000 | a)
}

function exec_c_zext_h(SrcL : bits(5)) -> unit = {
  let a = read_reg5(SrcL)[15..0];
  write_regdst(reg_t(), 0x0000_0000_0000_0000 | a)
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
  write_regdst(RegDst, to_bits(64, c))
}

function exec_ctz(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  let f = bitfield_wrap(x, m, n);
  let c : int = ctz_low_n(f, n);
  write_regdst(RegDst, to_bits(64, c))
}

function exec_bcnt(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  let f = bitfield_wrap(x, m, n);
  let c : int = popcount_low_n(f, n);
  write_regdst(RegDst, to_bits(64, c))
}

function exec_bic(RegDst : bits(5), SrcL : bits(5), Nminus1 : bits(6), M : bits(6)) -> unit = {
  let x = read_reg5(SrcL);
  let n : int = unsigned(Nminus1) + 1;
  let m : int = unsigned(M);
  let r = ror64(x, m);
  let cleared = r & (~mask_low_n(n));
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
  if (n % 8) != 0 then write_regdst(RegDst, 0x0000_0000_0000_0000)
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

function bool_to_u64(b : bool) -> bits(64) = {
  if b then 0x0000_0000_0000_0001 else 0x0000_0000_0000_0000
}

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

// SETC immediate variants (with encoded shamt): imm = (sext/zext(imm) << shamt).

function exec_setc_eqi(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext12_to64(simm12) << sh;
  set_commit_argument(bool_to_u64(a == imm))
}

function exec_setc_nei(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext12_to64(simm12) << sh;
  set_commit_argument(bool_to_u64(a != imm))
}

function exec_setc_lti(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext12_to64(simm12) << sh;
  set_commit_argument(bool_to_u64(signed(a) < signed(imm)))
}

function exec_setc_gei(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext12_to64(simm12) << sh;
  set_commit_argument(bool_to_u64(signed(a) >= signed(imm)))
}

function exec_setc_ltui(SrcL : bits(5), shamt : bits(5), uimm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = zext12_to64(uimm12) << sh;
  set_commit_argument(bool_to_u64(unsigned(a) < unsigned(imm)))
}

function exec_setc_geui(SrcL : bits(5), shamt : bits(5), uimm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = zext12_to64(uimm12) << sh;
  set_commit_argument(bool_to_u64(unsigned(a) >= unsigned(imm)))
}

function exec_setc_andi(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext12_to64(simm12) << sh;
  set_commit_argument(bool_to_u64((a & imm) != 0x0000_0000_0000_0000))
}

function exec_setc_ori(SrcL : bits(5), shamt : bits(5), simm12 : bits(12)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext12_to64(simm12) << sh;
  set_commit_argument(bool_to_u64((a | imm) != 0x0000_0000_0000_0000))
}

// HL (48-bit) SETC.*I forms: same semantics, but with 24-bit immediates.

function exec_hl_setc_eqi(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext24_to64(simm24) << sh;
  set_commit_argument(bool_to_u64(a == imm))
}

function exec_hl_setc_nei(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext24_to64(simm24) << sh;
  set_commit_argument(bool_to_u64(a != imm))
}

function exec_hl_setc_lti(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext24_to64(simm24) << sh;
  set_commit_argument(bool_to_u64(signed(a) < signed(imm)))
}

function exec_hl_setc_gei(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext24_to64(simm24) << sh;
  set_commit_argument(bool_to_u64(signed(a) >= signed(imm)))
}

function exec_hl_setc_ltui(SrcL : bits(5), shamt : bits(5), uimm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = zext24_to64(uimm24) << sh;
  set_commit_argument(bool_to_u64(unsigned(a) < unsigned(imm)))
}

function exec_hl_setc_geui(SrcL : bits(5), shamt : bits(5), uimm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = zext24_to64(uimm24) << sh;
  set_commit_argument(bool_to_u64(unsigned(a) >= unsigned(imm)))
}

function exec_hl_setc_andi(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext24_to64(simm24) << sh;
  set_commit_argument(bool_to_u64((a & imm) != 0x0000_0000_0000_0000))
}

function exec_hl_setc_ori(SrcL : bits(5), shamt : bits(5), simm24 : bits(24)) -> unit = {
  let a = read_reg5(SrcL);
  let sh : int = unsigned(shamt);
  let imm = sext24_to64(simm24) << sh;
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
// - Immediate offsets are halfword-scaled: target = base + (sext(offset) << 1).
// - B.Z/B.NZ consult predicate register p (modeled via read_predicate_p()).
// - Misaligned/unfetchable targets are reported as E_BLOCK(EC_BFETCH) by the fetch machinery.

function tpc_rel_target_from_imm12(simm12 : bits(12)) -> bits(64) = {
  let off = sext12_to64(simm12) << 1;
  read_tpc() + off
}

function tpc_rel_target_from_imm22(simm22 : bits(22)) -> bits(64) = {
  let off = sext22_to64(simm22) << 1;
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
  let off = sext12_to64(simm12) << 1;
  write_tpc(base + off)
}


// -----------------------------------------------------------------------------
// PC-relative operations (ADDTPC/SETRET)

function exec_addtpc(RegDst : bits(5), imm20 : bits(20)) -> unit = {
  let base = read_pc_or_tpc();
  let off = sext20_to64(imm20) << 1;
  write_regdst(RegDst, base + off)
}

function exec_setret(imm20 : bits(20)) -> unit = {
  let base = read_pc_or_tpc();
  let off = zext20_to64(imm20) << 1;
  write_regdst(0b01010, base + off)  // RA
}

function exec_hl_addtpc(RegDst : bits(5), imm32 : bits(32)) -> unit = {
  let base = read_pc_or_tpc();
  let off = sext32_from32(imm32) << 1;
  write_regdst(RegDst, base + off)
}

function exec_hl_setret(imm32 : bits(32)) -> unit = {
  let base = read_pc_or_tpc();
  let off = zext32_from32(imm32) << 1;
  write_regdst(0b01010, base + off)  // RA
}

function exec_c_setret(uimm5 : bits(5)) -> unit = {
  let base = read_pc_or_tpc();
  let off = (0x0000_0000_0000_0000 | uimm5) << 1;
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
  let t = if (SrcRType == 0b11) then 0b11 else 0b00;
  let b = match t {
    0b00 => b0,
    0b11 => (0x0000_0000_0000_0000 - b0),
    _ => b0
  };
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
    else (signed(a) / signed(b));
  write_regdst(RegDst, to_bits(64, qi))
}

function exec_divu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let qi : int = if b == 0x0000_0000_0000_0000 then 0 else (unsigned(a) / unsigned(b));
  write_regdst(RegDst, to_bits(64, qi))
}

function exec_rem(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let ai : int = signed(a);
  let bi : int = signed(b);
  let qi : int =
    if b == 0x0000_0000_0000_0000 then 0
    else if (a == 0x8000_0000_0000_0000) & (b == 0xFFFF_FFFF_FFFF_FFFF) then ai
    else (ai / bi);
  let ri : int = if b == 0x0000_0000_0000_0000 then ai else (ai - (qi * bi));
  write_regdst(RegDst, to_bits(64, ri))
}

function exec_remu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let ai : int = unsigned(a);
  let bi : int = unsigned(b);
  let qi : int = if b == 0x0000_0000_0000_0000 then 0 else (ai / bi);
  let ri : int = if b == 0x0000_0000_0000_0000 then ai else (ai - (qi * bi));
  write_regdst(RegDst, to_bits(64, ri))
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
    else (ai / bi);
  let q32 : bits(32) = to_bits(32, qi);
  write_regdst(RegDst, sext32_from32(q32))
}

function exec_divuw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let ai : int = unsigned(zext32_from32(a32));
  let bi : int = unsigned(zext32_from32(b32));
  let qi : int = if b32 == 0x0000_0000 then 0 else (ai / bi);
  let q32 : bits(32) = to_bits(32, qi);
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
    else (ai / bi);
  let ri : int = if b32 == 0x0000_0000 then ai else (ai - (qi * bi));
  let r32 : bits(32) = to_bits(32, ri);
  write_regdst(RegDst, sext32_from32(r32))
}

function exec_remuw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let ai : int = unsigned(zext32_from32(a32));
  let bi : int = unsigned(zext32_from32(b32));
  let qi : int = if b32 == 0x0000_0000 then 0 else (ai / bi);
  let ri : int = if b32 == 0x0000_0000 then ai else (ai - (qi * bi));
  let r32 : bits(32) = to_bits(32, ri);
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
    else (ai / bi);
  let ri : int =
    if b == 0x0000_0000_0000_0000 then ai
    else if (a == 0x8000_0000_0000_0000) & (b == 0xFFFF_FFFF_FFFF_FFFF) then 0
    else (ai - (qi * bi));
  write_regdst(RegDst0, to_bits(64, qi));
  write_regdst(RegDst1, to_bits(64, ri))
}

function exec_hl_divu(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let ai : int = unsigned(a);
  let bi : int = unsigned(b);
  let qi : int = if b == 0x0000_0000_0000_0000 then 0 else (ai / bi);
  let ri : int = if b == 0x0000_0000_0000_0000 then ai else (ai - (qi * bi));
  write_regdst(RegDst0, to_bits(64, qi));
  write_regdst(RegDst1, to_bits(64, ri))
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
    else (ai / bi);
  let ri : int =
    if b32 == 0x0000_0000 then ai
    else if (a32 == 0x8000_0000) & (b32 == 0xFFFF_FFFF) then 0
    else (ai - (qi * bi));
  let q32 : bits(32) = to_bits(32, qi);
  let r32 : bits(32) = to_bits(32, ri);
  write_regdst(RegDst0, sext32_from32(q32));
  write_regdst(RegDst1, sext32_from32(r32))
}

function exec_hl_divuw(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let ai : int = unsigned(zext32_from32(a32));
  let bi : int = unsigned(zext32_from32(b32));
  let qi : int = if b32 == 0x0000_0000 then 0 else (ai / bi);
  let ri : int = if b32 == 0x0000_0000 then ai else (ai - (qi * bi));
  let q32 : bits(32) = to_bits(32, qi);
  let r32 : bits(32) = to_bits(32, ri);
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
  write_regdst(RegDst, to_bits(64, pi))
}

function exec_mulu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let pi : int = unsigned(a) * unsigned(b);
  write_regdst(RegDst, to_bits(64, pi))
}

function exec_mulw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let pi : int = signed(sext32_from32(a32)) * signed(sext32_from32(b32));
  let p32 : bits(32) = to_bits(32, pi);
  write_regdst(RegDst, sext32_from32(p32))
}

function exec_muluw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let pi : int = unsigned(zext32_from32(a32)) * unsigned(zext32_from32(b32));
  let p32 : bits(32) = to_bits(32, pi);
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
  let p128 : bits(128) = to_bits(128, pi);
  let lo : bits(64) = p128[63..0];
  let hi : bits(64) = p128[127..64];
  write_regdst(RegDst0, lo);
  write_regdst(RegDst1, hi)
}

function exec_hl_mulu(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let a = read_reg5(SrcL);
  let b = read_reg5(SrcR);
  let pi : int = unsigned(a) * unsigned(b);
  let p128 : bits(128) = to_bits(128, pi);
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
  write_regdst(RegDst, to_bits(64, ri))
}

function exec_maddw(RegDst : bits(5), SrcD : bits(5), SrcL : bits(5), SrcR : bits(5)) -> unit = {
  let d32 : bits(32) = read_reg5(SrcD)[31..0];
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let b32 : bits(32) = read_reg5(SrcR)[31..0];
  let di : int = signed(sext32_from32(d32));
  let ai : int = signed(sext32_from32(a32));
  let bi : int = signed(sext32_from32(b32));
  let ri : int = ai * bi + di;
  let r32 : bits(32) = to_bits(32, ri);
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
  let acc128 : bits(128) = to_bits(128, acc);
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
  let acc128 : bits(128) = to_bits(128, acc);
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
  let imm = sext20_to64(imm20) << 12;
  write_regdst(RegDst, imm)
}

function exec_hl_lui(RegDst : bits(5), imm32 : bits(32)) -> unit = {
  // HL.LUI: load a 32-bit immediate and sign-extend to 64-bit (no <<12).
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

function exec_oriw(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let imm32 : bits(32) = sext12_to64(simm12)[31..0];
  let r32 : bits(32) = a32 | imm32;
  write_regdst(RegDst, sext32_from32(r32))
}

function exec_xoriw(RegDst : bits(5), SrcL : bits(5), simm12 : bits(12)) -> unit = {
  let a32 : bits(32) = read_reg5(SrcL)[31..0];
  let imm32 : bits(32) = sext12_to64(simm12)[31..0];
  let r32 : bits(32) = a32 ^ imm32;
  write_regdst(RegDst, sext32_from32(r32))
}


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
  base + (idx << sh)
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
  (exp == to_bits(11, 0x7FF)) & (frac != to_bits(52, 0))
}

function fp64_is_zero(x : bits(64)) -> bool = {
  (x & 0x7FFF_FFFF_FFFF_FFFF) == 0x0000_0000_0000_0000
}

function fp64_key(x : bits(64)) -> bits(64) = {
  // Total-order key for non-NaNs (matches LinxCore RTL ordering trick).
  if x[63] == 1b1 then ~x else (x ^ 0x8000_0000_0000_0000)
}

function fp64_eq(a : bits(64), b : bits(64)) -> bool = {
  let nan = fp64_is_nan(a) | fp64_is_nan(b);
  let both_zero = fp64_is_zero(a) & fp64_is_zero(b);
  (~nan) & ((a == b) | both_zero)
}

function fp64_lt(a : bits(64), b : bits(64)) -> bool = {
  let nan = fp64_is_nan(a) | fp64_is_nan(b);
  let both_zero = fp64_is_zero(a) & fp64_is_zero(b);
  (~nan) & (~both_zero) & (unsigned(fp64_key(a)) < unsigned(fp64_key(b)))
}

function fp64_ge(a : bits(64), b : bits(64)) -> bool = {
  let nan = fp64_is_nan(a) | fp64_is_nan(b);
  let both_zero = fp64_is_zero(a) & fp64_is_zero(b);
  (~nan) & (both_zero | (unsigned(fp64_key(a)) >= unsigned(fp64_key(b))))
}

function fp32_is_nan(x : bits(32)) -> bool = {
  let exp : bits(8) = x[30..23];
  let frac : bits(23) = x[22..0];
  (exp == to_bits(8, 0xFF)) & (frac != to_bits(23, 0))
}

function fp32_is_zero(x : bits(32)) -> bool = {
  (x & 0x7FFF_FFFF) == 0x0000_0000
}

function fp32_key(x : bits(32)) -> bits(32) = {
  if x[31] == 1b1 then ~x else (x ^ 0x8000_0000)
}

function fp32_eq(a : bits(32), b : bits(32)) -> bool = {
  let nan = fp32_is_nan(a) | fp32_is_nan(b);
  let both_zero = fp32_is_zero(a) & fp32_is_zero(b);
  (~nan) & ((a == b) | both_zero)
}

function fp32_lt(a : bits(32), b : bits(32)) -> bool = {
  let nan = fp32_is_nan(a) | fp32_is_nan(b);
  let both_zero = fp32_is_zero(a) & fp32_is_zero(b);
  (~nan) & (~both_zero) & (unsigned(fp32_key(a)) < unsigned(fp32_key(b)))
}

function fp32_ge(a : bits(32), b : bits(32)) -> bool = {
  let nan = fp32_is_nan(a) | fp32_is_nan(b);
  let both_zero = fp32_is_zero(a) & fp32_is_zero(b);
  (~nan) & (both_zero | (unsigned(fp32_key(a)) >= unsigned(fp32_key(b))))
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
  write_regdst(RegDst, bool_to_u64((~eq)))
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
    let neg0 = (a32[31] == 1b1) | (b32[31] == 1b1);
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
    let neg0 = (a64[63] == 1b1) | (b64[63] == 1b1);
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
// Execution control

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
  if not(is_canonical_va48(va)) then {
    // Manual: must raise translation fault (treated as MMU_PF).
    // Trap wiring is still staged, so keep the failure explicit.
    unimplemented("tlb.iv: non-canonical VA => E_DATA(MMU_PF)")
  } else {
    ()
  }
}

function exec_tlb_iav(SrcL : bits(5)) -> unit = {
  let va = read_reg5(SrcL);
  if not(is_canonical_va48(va)) then {
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

// -----------------------------------------------------------------------------
// SSR access (staged)

function exec_ssrget(RegDst : bits(5), SSR_ID : bits(12)) -> unit = {
  let id : bits(24) = 0x000000 | SSR_ID;
  write_regdst(RegDst, ssr_read(id))
}

function exec_ssrset(SrcL : bits(5), SSR_ID : bits(12)) -> unit = {
  let id : bits(24) = 0x000000 | SSR_ID;
  ssr_write(id, read_reg5(SrcL))
}

function exec_ssrswap(RegDst : bits(5), SrcL : bits(5), SSR_ID : bits(12)) -> unit = {
  let id : bits(24) = 0x000000 | SSR_ID;
  let oldv = ssr_read(id);
  ssr_write(id, read_reg5(SrcL));
  write_regdst(RegDst, oldv)
}

function exec_hl_ssrget(RegDst : bits(5), SSR_ID : bits(24)) -> unit = {
  write_regdst(RegDst, ssr_read(SSR_ID))
}

function exec_hl_ssrset(SrcL : bits(5), SSR_ID : bits(24)) -> unit = {
  ssr_write(SSR_ID, read_reg5(SrcL))
}

function exec_c_ssrget(SSRID : bits(5)) -> unit = {
  // C16 encoding carries a small SSR-ID field; zero-extend.
  let id : bits(24) = 0x000000 | SSRID;
  write_regdst(reg_t(), ssr_read(id))
}

function exec_ebreak() -> unit = {
  // Software breakpoint.
  trap_sw_breakpoint(read_pc_or_tpc())
}

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
  if not(is_block_start_marker(tgt)) then {
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

function exec_b_dim() -> unit = { bdesc_mark_dim() }
function exec_c_b_dim() -> unit = { bdesc_mark_dim() }
function exec_c_b_dimi() -> unit = { bdesc_mark_dim() }

function exec_b_text() -> unit = { bdesc_mark_text() }
function exec_b_arg() -> unit = { bdesc_mark_arg() }
function exec_b_ior() -> unit = { bdesc_mark_ior() }
function exec_b_iot() -> unit = { bdesc_mark_iot() }
function exec_b_ioti() -> unit = { bdesc_mark_iot() }

function exec_b_attr() -> unit = { () }
function exec_b_hint() -> unit = { () }
function exec_b_iod() -> unit = { () }

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
  write_regdst(RegDst, if ok then 0x0 else 0x1)
}

function exec_sc_h(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let v16 : bits(16) = read_reg5(SrcL)[15..0];
  let ea = read_reg5(SrcR);
  let ok = excl_check(ea);
  if ok then mem_store16_le(ea, v16) else ();
  excl_clear();
  write_regdst(RegDst, if ok then 0x0 else 0x1)
}

function exec_sc_w(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let v32 : bits(32) = read_reg5(SrcL)[31..0];
  let ea = read_reg5(SrcR);
  let ok = excl_check(ea);
  if ok then mem_store32_le(ea, v32) else ();
  excl_clear();
  write_regdst(RegDst, if ok then 0x0 else 0x1)
}

function exec_sc_d(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), aq : bits(1), far : bits(1), rl : bits(1)) -> unit = {
  let _ = aq; let _ = far; let _ = rl;
  let v64 : bits(64) = read_reg5(SrcL);
  let ea = read_reg5(SrcR);
  let ok = excl_check(ea);
  if ok then mem_store64_le(ea, v64) else ();
  excl_clear();
  write_regdst(RegDst, if ok then 0x0 else 0x1)
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

function mem_load16_le(ea : bits(64)) -> bits(16) = {
  let b0 : bits(8) = read_mem8(ea);
  let b1 : bits(8) = read_mem8(ea + 0x1);
  (0x0000 | b0) | ((0x0000 | b1) << 8)
}

function mem_load32_le(ea : bits(64)) -> bits(32) = {
  let b0 : bits(8) = read_mem8(ea + 0x0);
  let b1 : bits(8) = read_mem8(ea + 0x1);
  let b2 : bits(8) = read_mem8(ea + 0x2);
  let b3 : bits(8) = read_mem8(ea + 0x3);
  (0x0000_0000 | b0)
    | ((0x0000_0000 | b1) << 8)
    | ((0x0000_0000 | b2) << 16)
    | ((0x0000_0000 | b3) << 24)
}

function mem_load64_le(ea : bits(64)) -> bits(64) = {
  let w0 : bits(32) = mem_load32_le(ea + 0x0);
  let w1 : bits(32) = mem_load32_le(ea + 0x4);
  (0x0000_0000_0000_0000 | w0) | ((0x0000_0000_0000_0000 | w1) << 32)
}

function exec_lb(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (off1 << sh);
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, sext8_from8(b))
}

function exec_lbu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (off1 << sh);
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, zext8_from8(b))
}

function exec_lh(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (off1 << sh);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}

function exec_lhu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (off1 << sh);
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}

function exec_lw(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (off1 << sh);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}

function exec_lwu(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (off1 << sh);
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}

function exec_ld(RegDst : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let sh : int = unsigned(shamt);
  let ea = base + (off1 << sh);
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst, d)
}

function mem_store16_le(ea : bits(64), v : bits(16)) -> unit = {
  let b0 : bits(8) = v[7..0];
  let b1 : bits(8) = v[15..8];
  write_mem8(ea + 0x0, b0);
  write_mem8(ea + 0x1, b1)
}

function mem_store32_le(ea : bits(64), v : bits(32)) -> unit = {
  mem_store16_le(ea + 0x0, v[15..0]);
  mem_store16_le(ea + 0x2, v[31..16])
}

function mem_store64_le(ea : bits(64), v : bits(64)) -> unit = {
  mem_store32_le(ea + 0x0, v[31..0]);
  mem_store32_le(ea + 0x4, v[63..32])
}

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
  let ea = base + (off1 << 1);
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}

function exec_sw(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let ea = base + (off1 << 2);
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}

function exec_sd(SrcD : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let base = read_reg5(SrcL);
  let off0 = read_reg5(SrcR);
  let off1 = apply_srcrtype_arith64(SrcRType, off0);
  let ea = base + (off1 << 3);
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
  let ea = base + (off << 1);
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
  let ea = base + (off << 1);
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
  let ea = base + (off << 2);
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
  let ea = base + (off << 2);
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
  let ea = base + (off << 3);
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
  let ea = base + (off << 1);
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
  let ea = base + (off << 2);
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
  let ea = base + (off << 3);
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
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, sext8_from8(b))
}

function exec_lbu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let b : bits(8) = read_mem8(ea);
  write_regdst(RegDst, zext8_from8(b))
}

function exec_lh_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, sext16_from16(h))
}

function exec_lhu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let h : bits(16) = mem_load16_le(ea);
  write_regdst(RegDst, zext16_from16(h))
}

function exec_lw_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, sext32_from32(w))
}

function exec_lwu_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let w : bits(32) = mem_load32_le(ea);
  write_regdst(RegDst, zext32_from32(w))
}

function exec_ld_pcr(RegDst : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let d : bits(64) = mem_load64_le(ea);
  write_regdst(RegDst, d)
}

function exec_sb_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let v : bits(8) = read_reg5(SrcD)[7..0];
  write_mem8(ea, v)
}

function exec_sh_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let v : bits(16) = read_reg5(SrcD)[15..0];
  mem_store16_le(ea, v)
}

function exec_sw_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let v : bits(32) = read_reg5(SrcD)[31..0];
  mem_store32_le(ea, v)
}

function exec_sd_pcr(SrcD : bits(5), simm17 : bits(17)) -> unit = {
  let pc0 = read_pc_or_tpc();
  let pc = pc0 & 0xFFFF_FFFF_FFFF_FFFC; // align 2 (4-byte)
  let off = (sext17_to64(simm17) << 2);
  let ea = pc + off;
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(ea, v)
}

// -----------------------------------------------------------------------------
// HL (48-bit) pre/post-index loads/stores.
// Contract (per decision):
//   - PR: new_base = base + off; access at new_base; Dst1/Rd = new_base
//   - PO: access at base; new_base = base + off; Dst1/Rd = new_base
// off = (apply_srcrtype_arith64(SrcRType, SrcR) << shamt_or_scale)

function hl_off_shamt(SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> bits(64) = {
  let idx0 = read_reg5(SrcR);
  let idx1 = apply_srcrtype_arith64(SrcRType, idx0);
  (idx1 << shamt)
}

function hl_off_scale(SrcR : bits(5), SrcRType : bits(2), scale : int) -> bits(64) = {
  let idx0 = read_reg5(SrcR);
  let idx1 = apply_srcrtype_arith64(SrcRType, idx0);
  (idx1 << scale)
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

// -----------------------------------------------------------------------------
// HL (48-bit) PC-relative / immediate / pair addressing.
//
// Conventions:
// - .PCR uses EA = align4(PC/TPC) + (sext17(simm17) << 2)
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
  hl_pc_aligned4() + (sext17_to64(simm17) << 2)
}

function hl_ea_imm_scaled(base : bits(64), simm22 : bits(22), scale : int) -> bits(64) = {
  let off = sext22_to64(simm22);
  base + (off << scale)
}

function hl_ea_imm_unscaled(base : bits(64), simm22 : bits(22)) -> bits(64) = {
  base + sext22_to64(simm22)
}

function hl_ea_imm17_scaled(base : bits(64), simm17 : bits(17), scale : int) -> bits(64) = {
  let off = sext17_to64(simm17);
  base + (off << scale)
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
  let v1 : bits(8) = read_mem8(ea + 0x1);
  write_regdst(RegDst0, sext8_from8(v0));
  write_regdst(RegDst1, sext8_from8(v1))
}
function exec_hl_lbuip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 0);
  let v0 : bits(8) = read_mem8(ea);
  let v1 : bits(8) = read_mem8(ea + 0x1);
  write_regdst(RegDst0, zext8_from8(v0));
  write_regdst(RegDst1, zext8_from8(v1))
}
function exec_hl_lhip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 1);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + 0x2);
  write_regdst(RegDst0, sext16_from16(v0));
  write_regdst(RegDst1, sext16_from16(v1))
}
function exec_hl_lhip_u(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcL), simm17);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + 0x2);
  write_regdst(RegDst0, sext16_from16(v0));
  write_regdst(RegDst1, sext16_from16(v1))
}
function exec_hl_lhuip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 1);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + 0x2);
  write_regdst(RegDst0, zext16_from16(v0));
  write_regdst(RegDst1, zext16_from16(v1))
}
function exec_hl_lhuip_u(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcL), simm17);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + 0x2);
  write_regdst(RegDst0, zext16_from16(v0));
  write_regdst(RegDst1, zext16_from16(v1))
}
function exec_hl_lwip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 2);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + 0x4);
  write_regdst(RegDst0, sext32_from32(v0));
  write_regdst(RegDst1, sext32_from32(v1))
}
function exec_hl_lwip_u(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcL), simm17);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + 0x4);
  write_regdst(RegDst0, sext32_from32(v0));
  write_regdst(RegDst1, sext32_from32(v1))
}
function exec_hl_lwuip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 2);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + 0x4);
  write_regdst(RegDst0, zext32_from32(v0));
  write_regdst(RegDst1, zext32_from32(v1))
}
function exec_hl_lwuip_u(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcL), simm17);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + 0x4);
  write_regdst(RegDst0, zext32_from32(v0));
  write_regdst(RegDst1, zext32_from32(v1))
}
function exec_hl_ldip(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcL), simm17, 3);
  let v0 : bits(64) = mem_load64_le(ea);
  let v1 : bits(64) = mem_load64_le(ea + 0x8);
  write_regdst(RegDst0, v0);
  write_regdst(RegDst1, v1)
}
function exec_hl_ldip_u(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcL), simm17);
  let v0 : bits(64) = mem_load64_le(ea);
  let v1 : bits(64) = mem_load64_le(ea + 0x8);
  write_regdst(RegDst0, v0);
  write_regdst(RegDst1, v1)
}

// ---- HL load pair: reg+reg+shamt ----
function exec_hl_lbp(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(8) = read_mem8(ea);
  let v1 : bits(8) = read_mem8(ea + 0x1);
  write_regdst(RegDst0, sext8_from8(v0));
  write_regdst(RegDst1, sext8_from8(v1))
}
function exec_hl_lbup(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(8) = read_mem8(ea);
  let v1 : bits(8) = read_mem8(ea + 0x1);
  write_regdst(RegDst0, zext8_from8(v0));
  write_regdst(RegDst1, zext8_from8(v1))
}
function exec_hl_lhp(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + 0x2);
  write_regdst(RegDst0, sext16_from16(v0));
  write_regdst(RegDst1, sext16_from16(v1))
}
function exec_hl_lhup(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(16) = mem_load16_le(ea);
  let v1 : bits(16) = mem_load16_le(ea + 0x2);
  write_regdst(RegDst0, zext16_from16(v0));
  write_regdst(RegDst1, zext16_from16(v1))
}
function exec_hl_lwp(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + 0x4);
  write_regdst(RegDst0, sext32_from32(v0));
  write_regdst(RegDst1, sext32_from32(v1))
}
function exec_hl_lwup(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(32) = mem_load32_le(ea);
  let v1 : bits(32) = mem_load32_le(ea + 0x4);
  write_regdst(RegDst0, zext32_from32(v0));
  write_regdst(RegDst1, zext32_from32(v1))
}
function exec_hl_ldp(RegDst0 : bits(5), RegDst1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2), shamt : bits(5)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_shamt(SrcR, SrcRType, shamt);
  let v0 : bits(64) = mem_load64_le(ea);
  let v1 : bits(64) = mem_load64_le(ea + 0x8);
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
  write_mem8(ea + 0x1, v1)
}
function exec_hl_ship(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcR), simm17, 1);
  let v0 : bits(16) = read_reg5(SrcD0)[15..0];
  let v1 : bits(16) = read_reg5(SrcD1)[15..0];
  mem_store16_le(ea, v0);
  mem_store16_le(ea + 0x2, v1)
}
function exec_hl_ship_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcR), simm17);
  let v0 : bits(16) = read_reg5(SrcD0)[15..0];
  let v1 : bits(16) = read_reg5(SrcD1)[15..0];
  mem_store16_le(ea, v0);
  mem_store16_le(ea + 0x2, v1)
}
function exec_hl_swip(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcR), simm17, 2);
  let v0 : bits(32) = read_reg5(SrcD0)[31..0];
  let v1 : bits(32) = read_reg5(SrcD1)[31..0];
  mem_store32_le(ea, v0);
  mem_store32_le(ea + 0x4, v1)
}
function exec_hl_swip_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcR), simm17);
  let v0 : bits(32) = read_reg5(SrcD0)[31..0];
  let v1 : bits(32) = read_reg5(SrcD1)[31..0];
  mem_store32_le(ea, v0);
  mem_store32_le(ea + 0x4, v1)
}
function exec_hl_sdip(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_scaled(read_reg5(SrcR), simm17, 3);
  let v0 : bits(64) = read_reg5(SrcD0);
  let v1 : bits(64) = read_reg5(SrcD1);
  mem_store64_le(ea, v0);
  mem_store64_le(ea + 0x8, v1)
}
function exec_hl_sdip_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcR : bits(5), simm17 : bits(17)) -> unit = {
  let ea = hl_ea_imm17_unscaled(read_reg5(SrcR), simm17);
  let v0 : bits(64) = read_reg5(SrcD0);
  let v1 : bits(64) = read_reg5(SrcD1);
  mem_store64_le(ea, v0);
  mem_store64_le(ea + 0x8, v1)
}

// ---- HL store pair: reg+reg addressing ----
function exec_hl_sbp(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_scale(SrcR, SrcRType, 0);
  let v0 : bits(8) = read_reg5(SrcD0)[7..0];
  let v1 : bits(8) = read_reg5(SrcD1)[7..0];
  write_mem8(ea, v0);
  write_mem8(ea + 0x1, v1)
}
function exec_hl_shp(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_scale(SrcR, SrcRType, 1);
  let v0 : bits(16) = read_reg5(SrcD0)[15..0];
  let v1 : bits(16) = read_reg5(SrcD1)[15..0];
  mem_store16_le(ea, v0);
  mem_store16_le(ea + 0x2, v1)
}
function exec_hl_shp_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + apply_srcrtype_arith64(SrcRType, read_reg5(SrcR));
  let v0 : bits(16) = read_reg5(SrcD0)[15..0];
  let v1 : bits(16) = read_reg5(SrcD1)[15..0];
  mem_store16_le(ea, v0);
  mem_store16_le(ea + 0x2, v1)
}
function exec_hl_swp(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_scale(SrcR, SrcRType, 2);
  let v0 : bits(32) = read_reg5(SrcD0)[31..0];
  let v1 : bits(32) = read_reg5(SrcD1)[31..0];
  mem_store32_le(ea, v0);
  mem_store32_le(ea + 0x4, v1)
}
function exec_hl_swp_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + apply_srcrtype_arith64(SrcRType, read_reg5(SrcR));
  let v0 : bits(32) = read_reg5(SrcD0)[31..0];
  let v1 : bits(32) = read_reg5(SrcD1)[31..0];
  mem_store32_le(ea, v0);
  mem_store32_le(ea + 0x4, v1)
}
function exec_hl_sdp(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + hl_off_scale(SrcR, SrcRType, 3);
  let v0 : bits(64) = read_reg5(SrcD0);
  let v1 : bits(64) = read_reg5(SrcD1);
  mem_store64_le(ea, v0);
  mem_store64_le(ea + 0x8, v1)
}
function exec_hl_sdp_u(SrcD0 : bits(5), SrcD1 : bits(5), SrcL : bits(5), SrcR : bits(5), SrcRType : bits(2)) -> unit = {
  let ea = read_reg5(SrcL) + apply_srcrtype_arith64(SrcRType, read_reg5(SrcR));
  let v0 : bits(64) = read_reg5(SrcD0);
  let v1 : bits(64) = read_reg5(SrcD1);
  mem_store64_le(ea, v0);
  mem_store64_le(ea + 0x8, v1)
}
