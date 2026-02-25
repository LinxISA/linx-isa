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
