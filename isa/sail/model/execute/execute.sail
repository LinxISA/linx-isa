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
