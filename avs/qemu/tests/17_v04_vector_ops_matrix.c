/*
 * v0.4 vector operation matrix tests.
 *
 * Coverage intent:
 * - Integer vector ALU/imm/shift/minmax/div/rem/madd/psel execution.
 * - Vector compare-immediate/boolean and bitfield execution.
 * - Floating-point vector min/max/compare/fused/unary execution.
 */

#include "linx_test.h"

__asm__(
    ".p2align 3\n"
    ".globl __linx_v04_logic_body\n"
    "__linx_v04_logic_body:\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.lw.brg [ri1, lc0<<2, zero], ->vu\n"
    "  v.addi vt#1, 7, ->vm\n"
    "  v.sw.brg vm#1, [ri2, lc0<<2, zero]\n"
    "  v.subi vt#1, 3, ->vm\n"
    "  v.sw.brg vm#1, [ri3, lc0<<2, zero]\n"
    "  v.and vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri4, lc0<<2, zero]\n"
    "  v.andi vt#1, 255, ->vm\n"
    "  v.sw.brg vm#1, [ri5, lc0<<2, zero]\n"
    "  v.or vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri6, lc0<<2, zero]\n"
    "  v.ori vt#1, 18, ->vm\n"
    "  v.sw.brg vm#1, [ri7, lc0<<2, zero]\n"
    "  v.xor vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri8, lc0<<2, zero]\n"
    "  v.xori vt#1, -1, ->vm\n"
    "  v.sw.brg vm#1, [ri9, lc0<<2, zero]\n"
    "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v04_shift_body\n"
    "__linx_v04_shift_body:\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.lw.brg [ri1, lc0<<2, zero], ->vu\n"
    "  v.sll vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri2, lc0<<2, zero]\n"
    "  v.slli vt#1, 3, ->vm\n"
    "  v.sw.brg vm#1, [ri3, lc0<<2, zero]\n"
    "  v.srl vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri4, lc0<<2, zero]\n"
    "  v.srli vt#1, 1, ->vm\n"
    "  v.sw.brg vm#1, [ri5, lc0<<2, zero]\n"
    "  v.subi zero, 16, ->vn\n"
    "  v.sra vn#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri6, lc0<<2, zero]\n"
    "  v.srai vn#1, 2, ->vm\n"
    "  v.sw.brg vm#1, [ri7, lc0<<2, zero]\n"
    "  v.max vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri8, lc0<<2, zero]\n"
    "  v.min vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri9, lc0<<2, zero]\n"
    "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v04_div_madd_body\n"
    "__linx_v04_div_madd_body:\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.lw.brg [ri1, lc0<<2, zero], ->vu\n"
    "  v.lw.brg [ri2, lc0<<2, zero], ->vm\n"
    "  v.div vt#1, vu#1, ->vn\n"
    "  v.sw.brg vn#1, [ri3, lc0<<2, zero]\n"
    "  v.rem vt#1, vu#1, ->vn\n"
    "  v.sw.brg vn#1, [ri4, lc0<<2, zero]\n"
    "  v.madd vt#1, vu#1, vm#1, ->vn\n"
    "  v.sw.brg vn#1, [ri5, lc0<<2, zero]\n"
    "  v.cmp.lt vt#1, vu#1, ->vn\n"
    "  .4byte 0x385203ff\n"
    "  .4byte 0x0e109077\n"
    "  v.sw.brg vn#1, [ri6, lc0<<2, zero]\n"
    "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v04_cmp_misc_body\n"
    "__linx_v04_cmp_misc_body:\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.lw.brg [ri1, lc0<<2, zero], ->vu\n"
    "  v.cmp.and vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri2, lc0<<2, zero]\n"
    "  v.cmp.or vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri3, lc0<<2, zero]\n"
    "  v.cmp.andi vt#1, 0, ->vm\n"
    "  v.sw.brg vm#1, [ri4, lc0<<2, zero]\n"
    "  v.cmp.eqi vt#1, 7, ->vm\n"
    "  v.sw.brg vm#1, [ri5, lc0<<2, zero]\n"
    "  v.cmp.gei vt#1, 0, ->vm\n"
    "  v.sw.brg vm#1, [ri6, lc0<<2, zero]\n"
    "  v.cmp.geui vt#1, 8, ->vm\n"
    "  v.sw.brg vm#1, [ri7, lc0<<2, zero]\n"
    "  v.cmp.lti vt#1, 0, ->vm\n"
    "  v.sw.brg vm#1, [ri8, lc0<<2, zero]\n"
    "  v.cmp.ltui vt#1, 8, ->vm\n"
    "  v.sw.brg vm#1, [ri9, lc0<<2, zero]\n"
    "  v.cmp.nei vt#1, 7, ->vm\n"
    "  v.sw.brg vm#1, [ri10, lc0<<2, zero]\n"
    "  v.cmp.ori vt#1, 0, ->vm\n"
    "  v.sw.brg vm#1, [ri11, lc0<<2, zero]\n"
    "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v04_bitfield_body\n"
    "__linx_v04_bitfield_body:\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.bxu vt#1, 452, ->vu\n"
    "  v.sw.brg vu#1, [ri1, lc0<<2, zero]\n"
    "  v.bxs vt#1, 452, ->vu\n"
    "  v.sw.brg vu#1, [ri2, lc0<<2, zero]\n"
    "  v.bic vt#1, 452, ->vu\n"
    "  v.sw.brg vu#1, [ri3, lc0<<2, zero]\n"
    "  v.bis vt#1, 452, ->vu\n"
    "  v.sw.brg vu#1, [ri4, lc0<<2, zero]\n"
    "  v.ctz vt#1, 452, ->vu\n"
    "  v.sw.brg vu#1, [ri5, lc0<<2, zero]\n"
    "  v.clz vt#1, 452, ->vu\n"
    "  v.sw.brg vu#1, [ri6, lc0<<2, zero]\n"
    "  v.bcnt vt#1, 452, ->vu\n"
    "  v.sw.brg vu#1, [ri7, lc0<<2, zero]\n"
    "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v04_fp_cmp_body\n"
    "__linx_v04_fp_cmp_body:\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.lw.brg [ri1, lc0<<2, zero], ->vu\n"
    "  v.fmax vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri2, lc0<<2, zero]\n"
    "  v.fmin vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri3, lc0<<2, zero]\n"
    "  v.feqs vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri4, lc0<<2, zero]\n"
    "  v.fnes vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri5, lc0<<2, zero]\n"
    "  v.flts vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri6, lc0<<2, zero]\n"
    "  v.fges vt#1, vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri7, lc0<<2, zero]\n"
    "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v04_fp_fma_body\n"
    "__linx_v04_fp_fma_body:\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.lw.brg [ri1, lc0<<2, zero], ->vu\n"
    "  v.lw.brg [ri2, lc0<<2, zero], ->vm\n"
    "  v.fmadd vt#1, vu#1, vm#1, ->vt\n"
    "  v.sw.brg vt#1, [ri3, lc0<<2, zero]\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.fmsub vt#1, vu#1, vm#1, ->vt\n"
    "  v.sw.brg vt#1, [ri4, lc0<<2, zero]\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.fnmadd vt#1, vu#1, vm#1, ->vt\n"
    "  v.sw.brg vt#1, [ri5, lc0<<2, zero]\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.fnmsub vt#1, vu#1, vm#1, ->vt\n"
    "  v.sw.brg vt#1, [ri6, lc0<<2, zero]\n"
    "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v04_fp_unary_body\n"
    "__linx_v04_fp_unary_body:\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.lw.brg [ri1, lc0<<2, zero], ->vn\n"
    "  v.fsqrt vt#1, ->vu\n"
    "  v.sw.brg vu#1, [ri2, lc0<<2, zero]\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.frecip vt#1, ->vu\n"
    "  v.sw.brg vu#1, [ri3, lc0<<2, zero]\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.fexp vt#1, ->vu\n"
    "  v.sw.brg vu#1, [ri4, lc0<<2, zero]\n"
    "  v.lw.brg [ri1, lc0<<2, zero], ->vn\n"
    "  v.fclass vn#1, ->vu\n"
    "  v.sw.brg vu#1, [ri5, lc0<<2, zero]\n"
    "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v04_convert_rev_body\n"
    "__linx_v04_convert_rev_body:\n"
    "  v.lw.brg [ri0, lc0<<2, zero], ->vt\n"
    "  v.lw.brg [ri1, lc0<<2, zero], ->vn\n"
    "  v.icvt.sw2uw vt#1, ->vu\n"
    "  v.sw.brg vu#1, [ri2, lc0<<2, zero]\n"
    "  v.icvtf.sw2fs vt#1, ->vu\n"
    "  v.sw.brg vu#1, [ri3, lc0<<2, zero]\n"
    "  v.fcvti.fs2uw vn#1, ->vm\n"
    "  v.sw.brg vm#1, [ri4, lc0<<2, zero]\n"
    "  v.icvtf.sd2fs vt#1, ->vu\n"
    "  v.fcvt.fs2fd vu#1, ->vm\n"
    "  v.sw.brg vm#1, [ri5, lc0<<2, zero]\n"
    "  v.rev vt#1, 0, 31, ->vu\n"
    "  v.sw.brg vu#1, [ri6, lc0<<2, zero]\n"
    "  C.BSTOP\n");

static void test_v_logic_imm_matrix(void)
{
    enum { N = 32 };

    static uint32_t a[N], b[N];
    static uint32_t addi[N], subi[N], andv[N], andi[N], orv[N], oriv[N], xorv[N], xoriv[N];

    for (unsigned i = 0; i < N; i++) {
        a[i] = 0x1100u + i * 13u;
        b[i] = 0x0040u + i * 3u;
        addi[i] = subi[i] = andv[i] = andi[i] = 0u;
        orv[i] = oriv[i] = xorv[i] = xoriv[i] = 0u;
    }

    __asm__ volatile(
        "BSTART.MSEQ 0\n"
        "B.TEXT __linx_v04_logic_body\n"
        "B.IOR [%0, %1, %2],[]\n"
        "B.IOR [%3, %4, %5],[]\n"
        "B.IOR [%6, %7, %8],[]\n"
        "B.IOR [%9],[]\n"
        "C.B.DIMI 32, ->lb0\n"
        "C.BSTART\n"
        :
        : "r"((uint64_t)(uintptr_t)&a[0]), "r"((uint64_t)(uintptr_t)&b[0]),
          "r"((uint64_t)(uintptr_t)&addi[0]), "r"((uint64_t)(uintptr_t)&subi[0]),
          "r"((uint64_t)(uintptr_t)&andv[0]), "r"((uint64_t)(uintptr_t)&andi[0]),
          "r"((uint64_t)(uintptr_t)&orv[0]), "r"((uint64_t)(uintptr_t)&oriv[0]),
          "r"((uint64_t)(uintptr_t)&xorv[0]), "r"((uint64_t)(uintptr_t)&xoriv[0])
        : "memory");

    for (unsigned i = 0; i < N; i++) {
        TEST_EQ32(addi[i], a[i] + 7u, 0x1700u + i);
        TEST_EQ32(subi[i], a[i] - 3u, 0x1720u + i);
        TEST_EQ32(andv[i], a[i] & b[i], 0x1740u + i);
        TEST_EQ32(andi[i], a[i] & 255u, 0x1760u + i);
        TEST_EQ32(orv[i], a[i] | b[i], 0x1780u + i);
        TEST_EQ32(oriv[i], a[i] | 18u, 0x17A0u + i);
        TEST_EQ32(xorv[i], a[i] ^ b[i], 0x17C0u + i);
        TEST_EQ32(xoriv[i], a[i] ^ 0xffffffffu, 0x17E0u + i);
    }
}

static void test_v_shift_minmax_matrix(void)
{
    enum { N = 32 };

    static uint32_t a[N], sh[N];
    static uint32_t sllv[N], slliv[N], srlv[N], srliv[N], srav[N], sraiv[N], maxv[N], minv[N];

    for (unsigned i = 0; i < N; i++) {
        a[i] = 3u + i;
        sh[i] = i & 7u;
        sllv[i] = slliv[i] = srlv[i] = srliv[i] = 0u;
        srav[i] = sraiv[i] = maxv[i] = minv[i] = 0u;
    }

    __asm__ volatile(
        "BSTART.MSEQ 0\n"
        "B.TEXT __linx_v04_shift_body\n"
        "B.IOR [%0, %1, %2],[]\n"
        "B.IOR [%3, %4, %5],[]\n"
        "B.IOR [%6, %7, %8],[]\n"
        "B.IOR [%9],[]\n"
        "C.B.DIMI 32, ->lb0\n"
        "C.BSTART\n"
        :
        : "r"((uint64_t)(uintptr_t)&a[0]), "r"((uint64_t)(uintptr_t)&sh[0]),
          "r"((uint64_t)(uintptr_t)&sllv[0]), "r"((uint64_t)(uintptr_t)&slliv[0]),
          "r"((uint64_t)(uintptr_t)&srlv[0]), "r"((uint64_t)(uintptr_t)&srliv[0]),
          "r"((uint64_t)(uintptr_t)&srav[0]), "r"((uint64_t)(uintptr_t)&sraiv[0]),
          "r"((uint64_t)(uintptr_t)&maxv[0]), "r"((uint64_t)(uintptr_t)&minv[0])
        : "memory");

    for (unsigned i = 0; i < N; i++) {
        TEST_EQ32(sllv[i], a[i] << (sh[i] & 31u), 0x1800u + i);
        TEST_EQ32(slliv[i], a[i] << 3, 0x1820u + i);
        TEST_EQ32(srlv[i], a[i] >> (sh[i] & 31u), 0x1840u + i);
        TEST_EQ32(srliv[i], a[i] >> 1, 0x1860u + i);
        TEST_EQ32(srav[i], (uint32_t)((int64_t)-16 >> (sh[i] & 31u)), 0x1880u + i);
        TEST_EQ32(sraiv[i], (uint32_t)((int64_t)-16 >> 2), 0x18A0u + i);
        TEST_EQ32(maxv[i], a[i] > sh[i] ? a[i] : sh[i], 0x18C0u + i);
        TEST_EQ32(minv[i], a[i] < sh[i] ? a[i] : sh[i], 0x18E0u + i);
    }
}

static void test_v_div_madd_psel_matrix(void)
{
    enum { N = 32 };

    static uint32_t a[N], b[N], c[N];
    static uint32_t divv[N], remv[N], maddv[N], pselv[N];

    for (unsigned i = 0; i < N; i++) {
        a[i] = 64u + i * 7u;
        b[i] = 2u + (i & 7u);
        c[i] = 5u + i;
        divv[i] = remv[i] = maddv[i] = pselv[i] = 0u;
    }

    __asm__ volatile(
        "BSTART.MSEQ 0\n"
        "B.TEXT __linx_v04_div_madd_body\n"
        "B.IOR [%0, %1, %2],[]\n"
        "B.IOR [%3, %4, %5],[]\n"
        "B.IOR [%6],[]\n"
        "C.B.DIMI 32, ->lb0\n"
        "C.BSTART\n"
        :
        : "r"((uint64_t)(uintptr_t)&a[0]), "r"((uint64_t)(uintptr_t)&b[0]),
          "r"((uint64_t)(uintptr_t)&c[0]), "r"((uint64_t)(uintptr_t)&divv[0]),
          "r"((uint64_t)(uintptr_t)&remv[0]), "r"((uint64_t)(uintptr_t)&maddv[0]),
          "r"((uint64_t)(uintptr_t)&pselv[0])
        : "memory");

    for (unsigned i = 0; i < N; i++) {
        TEST_EQ32(divv[i], a[i] / b[i], 0x1900u + i);
        TEST_EQ32(remv[i], a[i] % b[i], 0x1920u + i);
        TEST_EQ32(maddv[i], a[i] * b[i] + c[i], 0x1940u + i);
        TEST_EQ32(pselv[i], a[i] < b[i] ? a[i] : b[i], 0x1960u + i);
    }
}

static void test_v_cmp_misc_matrix(void)
{
    enum { N = 32 };

    static int32_t a[N];
    static uint32_t b[N];
    static uint32_t andv[N], orv[N], andiv[N], eqiv[N], geiv[N];
    static uint32_t geuiv[N], ltiv[N], ltuiv[N], neiv[N], oriv[N];

    for (unsigned i = 0; i < N; i++) {
        switch (i & 7u) {
        case 0:
            a[i] = -8;
            break;
        case 1:
            a[i] = -1;
            break;
        case 2:
            a[i] = 0;
            break;
        case 3:
            a[i] = 1;
            break;
        case 4:
            a[i] = 7;
            break;
        case 5:
            a[i] = 8;
            break;
        case 6:
            a[i] = 15;
            break;
        default:
            a[i] = 1024 + (int32_t)i;
            break;
        }
        b[i] = (i % 3u) == 0u ? 0u : (0x10u + i);
        andv[i] = orv[i] = andiv[i] = eqiv[i] = geiv[i] = 0u;
        geuiv[i] = ltiv[i] = ltuiv[i] = neiv[i] = oriv[i] = 0u;
    }

    __asm__ volatile(
        "BSTART.MSEQ 0\n"
        "B.TEXT __linx_v04_cmp_misc_body\n"
        "B.IOR [%0, %1, %2],[]\n"
        "B.IOR [%3, %4, %5],[]\n"
        "B.IOR [%6, %7, %8],[]\n"
        "B.IOR [%9, %10, %11],[]\n"
        "C.B.DIMI 32, ->lb0\n"
        "C.BSTART\n"
        :
        : "r"((uint64_t)(uintptr_t)&a[0]), "r"((uint64_t)(uintptr_t)&b[0]),
          "r"((uint64_t)(uintptr_t)&andv[0]), "r"((uint64_t)(uintptr_t)&orv[0]),
          "r"((uint64_t)(uintptr_t)&andiv[0]), "r"((uint64_t)(uintptr_t)&eqiv[0]),
          "r"((uint64_t)(uintptr_t)&geiv[0]), "r"((uint64_t)(uintptr_t)&geuiv[0]),
          "r"((uint64_t)(uintptr_t)&ltiv[0]), "r"((uint64_t)(uintptr_t)&ltuiv[0]),
          "r"((uint64_t)(uintptr_t)&neiv[0]), "r"((uint64_t)(uintptr_t)&oriv[0])
        : "memory");

    for (unsigned i = 0; i < N; i++) {
        const uint32_t au = (uint32_t)a[i];
        const uint32_t ab = a[i] != 0 ? 1u : 0u;
        const uint32_t bb = b[i] != 0 ? 1u : 0u;
        TEST_EQ32(andv[i], ab & bb, 0x1C00u + i);
        TEST_EQ32(orv[i], ab | bb, 0x1C20u + i);
        TEST_EQ32(andiv[i], 0u, 0x1C40u + i);
        TEST_EQ32(eqiv[i], a[i] == 7 ? 1u : 0u, 0x1C60u + i);
        TEST_EQ32(geiv[i], a[i] >= 0 ? 1u : 0u, 0x1C80u + i);
        TEST_EQ32(geuiv[i], au >= 8u ? 1u : 0u, 0x1CA0u + i);
        TEST_EQ32(ltiv[i], a[i] < 0 ? 1u : 0u, 0x1CC0u + i);
        TEST_EQ32(ltuiv[i], au < 8u ? 1u : 0u, 0x1CE0u + i);
        TEST_EQ32(neiv[i], a[i] != 7 ? 1u : 0u, 0x1D00u + i);
        TEST_EQ32(oriv[i], ab, 0x1D20u + i);
    }
}

static uint32_t bitfield_clz8(uint32_t field)
{
    uint32_t count = 0u;

    for (uint32_t mask = 0x80u; mask != 0u && (field & mask) == 0u; mask >>= 1) {
        count++;
    }
    return count;
}

static uint32_t bitfield_ctz8(uint32_t field)
{
    uint32_t count = 0u;

    for (uint32_t mask = 0x01u; mask <= 0x80u && (field & mask) == 0u; mask <<= 1) {
        count++;
    }
    return count;
}

static uint32_t bitfield_popcount8(uint32_t field)
{
    uint32_t count = 0u;

    for (uint32_t mask = 0x01u; mask <= 0x80u; mask <<= 1) {
        if ((field & mask) != 0u) {
            count++;
        }
    }
    return count;
}

static void test_v_bitfield_matrix(void)
{
    enum { N = 32 };

    static uint32_t a[N];
    static uint32_t bxuv[N], bxsv[N], bicv[N], bisv[N], ctzv[N], clzv[N], bcntv[N];

    for (unsigned i = 0; i < N; i++) {
        const uint32_t field = (uint32_t)((i * 29u) & 0xffu);
        a[i] = 0xC0000003u ^ (i << 20) ^ (field << 4);
        bxuv[i] = bxsv[i] = bicv[i] = bisv[i] = ctzv[i] = clzv[i] = bcntv[i] = 0u;
    }

    __asm__ volatile(
        "BSTART.MSEQ 0\n"
        "B.TEXT __linx_v04_bitfield_body\n"
        "B.IOR [%0, %1, %2],[]\n"
        "B.IOR [%3, %4, %5],[]\n"
        "B.IOR [%6, %7],[]\n"
        "C.B.DIMI 32, ->lb0\n"
        "C.BSTART\n"
        :
        : "r"((uint64_t)(uintptr_t)&a[0]), "r"((uint64_t)(uintptr_t)&bxuv[0]),
          "r"((uint64_t)(uintptr_t)&bxsv[0]), "r"((uint64_t)(uintptr_t)&bicv[0]),
          "r"((uint64_t)(uintptr_t)&bisv[0]), "r"((uint64_t)(uintptr_t)&ctzv[0]),
          "r"((uint64_t)(uintptr_t)&clzv[0]), "r"((uint64_t)(uintptr_t)&bcntv[0])
        : "memory");

    for (unsigned i = 0; i < N; i++) {
        const uint32_t field = (a[i] >> 4) & 0xffu;
        TEST_EQ32(bxuv[i], field, 0x1D40u + i);
        TEST_EQ32(bxsv[i], (uint32_t)(int32_t)(int8_t)field, 0x1D60u + i);
        TEST_EQ32(bicv[i], a[i] & ~(0xffu << 4), 0x1D80u + i);
        TEST_EQ32(bisv[i], a[i] | (0xffu << 4), 0x1DA0u + i);
        TEST_EQ32(ctzv[i], bitfield_ctz8(field), 0x1DC0u + i);
        TEST_EQ32(clzv[i], bitfield_clz8(field), 0x1DE0u + i);
        TEST_EQ32(bcntv[i], bitfield_popcount8(field), 0x1E00u + i);
    }
}

static void test_v_fp_cmp_matrix(void)
{
    enum { N = 32 };

    static float a[N], b[N];
    static uint32_t fmaxv[N], fminv[N], feqv[N], fnev[N], fltv[N], fgev[N];

    for (unsigned i = 0; i < N; i++) {
        a[i] = (float)i * 0.5f;
        b[i] = (float)(i % 5) * 0.75f;
        fmaxv[i] = fminv[i] = feqv[i] = fnev[i] = fltv[i] = fgev[i] = 0u;
    }

    __asm__ volatile(
        "BSTART.MSEQ 0\n"
        "B.TEXT __linx_v04_fp_cmp_body\n"
        "B.IOR [%0, %1, %2],[]\n"
        "B.IOR [%3, %4, %5],[]\n"
        "B.IOR [%6, %7],[]\n"
        "C.B.DIMI 32, ->lb0\n"
        "C.BSTART\n"
        :
        : "r"((uint64_t)(uintptr_t)&a[0]), "r"((uint64_t)(uintptr_t)&b[0]),
          "r"((uint64_t)(uintptr_t)&fmaxv[0]), "r"((uint64_t)(uintptr_t)&fminv[0]),
          "r"((uint64_t)(uintptr_t)&feqv[0]), "r"((uint64_t)(uintptr_t)&fnev[0]),
          "r"((uint64_t)(uintptr_t)&fltv[0]), "r"((uint64_t)(uintptr_t)&fgev[0])
        : "memory");

    for (unsigned i = 0; i < N; i++) {
        union {
            float f;
            uint32_t u;
        } expect_max, expect_min;
        expect_max.f = a[i] > b[i] ? a[i] : b[i];
        expect_min.f = a[i] < b[i] ? a[i] : b[i];
        TEST_EQ32(fmaxv[i], expect_max.u, 0x1A00u + i);
        TEST_EQ32(fminv[i], expect_min.u, 0x1A20u + i);
        TEST_EQ32(feqv[i], a[i] == b[i] ? 1u : 0u, 0x1A40u + i);
        TEST_EQ32(fnev[i], a[i] != b[i] ? 1u : 0u, 0x1A60u + i);
        TEST_EQ32(fltv[i], a[i] < b[i] ? 1u : 0u, 0x1A80u + i);
        TEST_EQ32(fgev[i], a[i] >= b[i] ? 1u : 0u, 0x1AA0u + i);
    }
}

static void test_v_fp_fma_matrix(void)
{
    enum { N = 32 };

    static float a[N], b[N], c[N];
    static uint32_t fmaddv[N], fmsubv[N], fnmaddv[N], fnmsubv[N];

    for (unsigned i = 0; i < N; i++) {
        a[i] = 4.0f + (float)i;
        b[i] = 2.0f;
        c[i] = 1.0f;
        fmaddv[i] = fmsubv[i] = fnmaddv[i] = fnmsubv[i] = 0u;
    }

    __asm__ volatile(
        "BSTART.MSEQ 0\n"
        "B.TEXT __linx_v04_fp_fma_body\n"
        "B.IOR [%0, %1, %2],[]\n"
        "B.IOR [%3, %4, %5],[]\n"
        "B.IOR [%6],[]\n"
        "C.B.DIMI 32, ->lb0\n"
        "C.BSTART\n"
        :
        : "r"((uint64_t)(uintptr_t)&a[0]), "r"((uint64_t)(uintptr_t)&b[0]),
          "r"((uint64_t)(uintptr_t)&c[0]), "r"((uint64_t)(uintptr_t)&fmaddv[0]),
          "r"((uint64_t)(uintptr_t)&fmsubv[0]), "r"((uint64_t)(uintptr_t)&fnmaddv[0]),
          "r"((uint64_t)(uintptr_t)&fnmsubv[0])
        : "memory");

    for (unsigned i = 0; i < N; i++) {
        union {
            float f;
            uint32_t u;
        } fmadd_expect, fmsub_expect, fnmadd_expect, fnmsub_expect;
        fmadd_expect.f = (a[i] * b[i]) + c[i];
        fmsub_expect.f = (a[i] * b[i]) - c[i];
        fnmadd_expect.f = -(a[i] * b[i]) + c[i];
        fnmsub_expect.f = -(a[i] * b[i]) - c[i];
        TEST_EQ32(fmaddv[i], fmadd_expect.u, 0x1B00u + i);
        TEST_EQ32(fmsubv[i], fmsub_expect.u, 0x1B20u + i);
        TEST_EQ32(fnmaddv[i], fnmadd_expect.u, 0x1B40u + i);
        TEST_EQ32(fnmsubv[i], fnmsub_expect.u, 0x1B60u + i);
    }
}

static void test_v_fp_unary_class_matrix(void)
{
    enum { N = 4 };

    static const float a[N] = {4.0f, 9.0f, 1.0f, 0.5f};
    static const uint32_t class_src[N] = {
        0x00000000u,
        0x80000000u,
        0x7f800000u,
        0x7fc00000u,
    };
    static const uint32_t fsqrt_expect[N] = {
        0x40000000u,
        0x40400000u,
        0x3f800000u,
        0x3f3504f3u,
    };
    static const uint32_t frecip_expect[N] = {
        0x3e800000u,
        0x3de38e39u,
        0x3f800000u,
        0x40000000u,
    };
    static const uint32_t fexp_expect[N] = {
        0x425a6481u,
        0x45fd38acu,
        0x402df854u,
        0x3fd3094cu,
    };
    static const uint32_t fclass_expect[N] = {
        1u << 4,
        1u << 3,
        1u << 7,
        1u << 9,
    };
    static uint32_t fsqrtv[N], frecipv[N], fexpv[N], fclassv[N];

    for (unsigned i = 0; i < N; i++) {
        fsqrtv[i] = frecipv[i] = fexpv[i] = fclassv[i] = 0u;
    }

    __asm__ volatile(
        "BSTART.MSEQ 0\n"
        "B.TEXT __linx_v04_fp_unary_body\n"
        "B.IOR [%0, %1, %2],[]\n"
        "B.IOR [%3, %4, %5],[]\n"
        "C.B.DIMI 4, ->lb0\n"
        "C.BSTART\n"
        :
        : "r"((uint64_t)(uintptr_t)&a[0]), "r"((uint64_t)(uintptr_t)&class_src[0]),
          "r"((uint64_t)(uintptr_t)&fsqrtv[0]), "r"((uint64_t)(uintptr_t)&frecipv[0]),
          "r"((uint64_t)(uintptr_t)&fexpv[0]), "r"((uint64_t)(uintptr_t)&fclassv[0])
        : "memory");

    for (unsigned i = 0; i < N; i++) {
        TEST_EQ32(fsqrtv[i], fsqrt_expect[i], 0x1B80u + i);
        TEST_EQ32(frecipv[i], frecip_expect[i], 0x1BA0u + i);
        TEST_EQ32(fexpv[i], fexp_expect[i], 0x1BC0u + i);
        TEST_EQ32(fclassv[i], fclass_expect[i], 0x1BE0u + i);
    }
}

static void test_v_convert_rev_matrix(void)
{
    enum { N = 32 };

    static int32_t ints[N];
    static float floats[N];
    static uint32_t icvtv[N], icvtfv[N], fcvtiv[N], fcvtv[N], revv[N];

    for (unsigned i = 0; i < N; i++) {
        ints[i] = 3 + (int32_t)(i * 5u);
        floats[i] = 0.2f + (float)i + ((i & 1u) ? 0.6f : 0.1f);
        icvtv[i] = icvtfv[i] = fcvtiv[i] = fcvtv[i] = revv[i] = 0u;
    }

    __asm__ volatile(
        "BSTART.MSEQ 0\n"
        "B.TEXT __linx_v04_convert_rev_body\n"
        "B.IOR [%0, %1, %2],[]\n"
        "B.IOR [%3, %4, %5],[]\n"
        "B.IOR [%6],[]\n"
        "C.B.DIMI 32, ->lb0\n"
        "C.BSTART\n"
        :
        : "r"((uint64_t)(uintptr_t)&ints[0]), "r"((uint64_t)(uintptr_t)&floats[0]),
          "r"((uint64_t)(uintptr_t)&icvtv[0]), "r"((uint64_t)(uintptr_t)&icvtfv[0]),
          "r"((uint64_t)(uintptr_t)&fcvtiv[0]), "r"((uint64_t)(uintptr_t)&fcvtv[0]),
          "r"((uint64_t)(uintptr_t)&revv[0])
        : "memory");

    for (unsigned i = 0; i < N; i++) {
        union {
            float f;
            uint32_t u;
        } icvtf_expect, fcvt_expect;

        TEST_EQ32(icvtv[i], (uint32_t)ints[i], 0x1E20u + i);
        icvtf_expect.f = (float)ints[i];
        TEST_EQ32(icvtfv[i], icvtf_expect.u, 0x1E40u + i);
        TEST_EQ32(fcvtiv[i], (uint32_t)(floats[i] + 0.5f), 0x1E60u + i);
        fcvt_expect.f = (float)ints[i];
        TEST_EQ32(fcvtv[i], fcvt_expect.u, 0x1E80u + i);
        TEST_EQ32(revv[i], __builtin_bswap32((uint32_t)ints[i]), 0x1EA0u + i);
    }
}

void run_v04_vector_ops_matrix_tests(void)
{
    test_start(0x1700);
    uart_puts("v0.4 vector logic/imm ... ");
    test_v_logic_imm_matrix();
    test_pass();

    test_start(0x1800);
    uart_puts("v0.4 vector shifts/minmax ... ");
    test_v_shift_minmax_matrix();
    test_pass();

    test_start(0x1900);
    uart_puts("v0.4 vector div/rem/madd/psel ... ");
    test_v_div_madd_psel_matrix();
    test_pass();

    test_start(0x1A00);
    uart_puts("v0.4 vector fp minmax/cmp ... ");
    test_v_fp_cmp_matrix();
    test_pass();

    test_start(0x1B00);
    uart_puts("v0.4 vector fp fma ... ");
    test_v_fp_fma_matrix();
    test_pass();

    test_start(0x1B80);
    uart_puts("v0.4 vector fp unary/class ... ");
    test_v_fp_unary_class_matrix();
    test_pass();

    test_start(0x1C00);
    uart_puts("v0.4 vector cmp misc ... ");
    test_v_cmp_misc_matrix();
    test_pass();

    test_start(0x1D40);
    uart_puts("v0.4 vector bitfield ... ");
    test_v_bitfield_matrix();
    test_pass();

    test_start(0x1E20);
    uart_puts("v0.4 vector convert/rev ... ");
    test_v_convert_rev_matrix();
    test_pass();
}
