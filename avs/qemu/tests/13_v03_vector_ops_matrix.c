/*
 * v0.56 Vector operation matrix tests (MSEQ body execution path).
 *
 * Coverage intent:
 * - Integer vector ALU + bridged path: v.add / v.sub + v.lw.brg / v.sw.brg
 * - Floating-point vector ALU: v.fadd / v.fmul
 */

#include "linx_test.h"

#define LINX_V03_ASM_WRAPPER(name, body, cont) \
    __asm__(                                   \
        ".p2align 2\n"                         \
        ".globl " #name "\n"                   \
        #name ":\n"                            \
        body                                   \
        "  C.BSTART DIRECT, " #name "_cont\n"  \
        "  C.BSTOP\n"                          \
        #name "_cont:\n"                       \
        "  C.BSTART.STD\n"                     \
        cont                                   \
        "  C.BSTART DIRECT, " #name "_ret\n"   \
        "  C.BSTOP\n"                          \
        #name "_ret:\n"                        \
        "  C.BSTART.STD RET\n"                 \
        "  c.setc.tgt ra\n"                    \
        "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_ops_add_sub_body\n"
    "__linx_v03_ops_add_sub_body:\n"
    "  v.lw.brg [ri0.sd, lc0<<2, zero.sd], ->vt.w\n"
    "  v.lw.brg [ri1.sd, lc0<<2, zero.sd], ->vu.w\n"
    "  v.add vt#1.reuse.sw, vu#1.reuse.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri2.sd, lc0<<2, zero.sd]\n"
    "  v.sub vt#2.sw, vu#1.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri3.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_ops_float_body\n"
    "__linx_v03_ops_float_body:\n"
    "  v.lw.brg [ri0.sd, lc0<<2, zero.sd], ->vt.w\n"
    "  v.fadd vt#1.fs, ri2.fs, ->vt.w\n"
    "  v.fmul vt#1.fs, ri3.fs, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri1.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_ops_mixed_pred_body\n"
    "__linx_v03_ops_mixed_pred_body:\n"
    "  addi a7, 1, ->a7\n"
    "  v.cmp.lt lc0.sw, ri1.sw, ->vt.d\n"
    "  v.sw.brg vt#1.sd, [ri0.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n");

extern void linx_v03_launch_ops_add_sub(uint64_t a_base, uint64_t b_base,
                                        uint64_t sum_base,
                                        uint64_t diff_base);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_ops_add_sub,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_ops_add_sub_body\n"
    "  B.IOR [a0, a1, a2],[]\n"
    "  B.IOR [a3],[]\n"
    "  C.B.DIMI 32, ->lb0\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_ops_float(uint64_t src_base, uint64_t dst_base,
                                      uint64_t add_f32, uint64_t mul_f32);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_ops_float,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_ops_float_body\n"
    "  B.IOR [a0, a1, a2],[]\n"
    "  B.IOR [a3],[]\n"
    "  C.B.DIMI 32, ->lb0\n"
    "  C.BSTART\n",
    "")

extern uint64_t linx_v03_launch_ops_mixed_pred(uint64_t out_base,
                                               uint64_t threshold);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_ops_mixed_pred,
    "  C.BSTART\n"
    "  addi zero, 0, ->a7\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_ops_mixed_pred_body\n"
    "  B.IOR [a0, a1],[]\n"
    "  C.B.DIMI 32, ->lb0\n"
    "  C.BSTART\n",
    "  add a7, zero, ->a0\n")

static void test_v_add_sub_matrix(void)
{
    enum { N = 32 };

    static uint32_t a[N];
    static uint32_t b[N];
    static uint32_t sum[N];
    static uint32_t diff[N];

    for (unsigned i = 0; i < N; i++) {
        a[i] = 100u + i * 3u;
        b[i] = 17u + i;
        sum[i] = 0u;
        diff[i] = 0u;
    }

    const uint64_t a_base = (uint64_t)(uintptr_t)&a[0];
    const uint64_t b_base = (uint64_t)(uintptr_t)&b[0];
    const uint64_t sum_base = (uint64_t)(uintptr_t)&sum[0];
    const uint64_t diff_base = (uint64_t)(uintptr_t)&diff[0];

    linx_v03_launch_ops_add_sub(a_base, b_base, sum_base, diff_base);

    for (unsigned i = 0; i < N; i++) {
        TEST_EQ32(sum[i], a[i] + b[i], 0x1301u + i);
        TEST_EQ32(diff[i], a[i] - b[i], 0x1321u + i);
    }
}

static void test_v_float_matrix(void)
{
    enum { N = 32 };

    static float src[N];
    static float dst[N];

    for (unsigned i = 0; i < N; i++) {
        src[i] = (float)i * 0.25f;
        dst[i] = 0.0f;
    }

    const uint64_t src_base = (uint64_t)(uintptr_t)&src[0];
    const uint64_t dst_base = (uint64_t)(uintptr_t)&dst[0];
    const uint64_t add_f32 = 0x3f800000u; /* +1.0f */
    const uint64_t mul_f32 = 0x40000000u; /* *2.0f */

    linx_v03_launch_ops_float(src_base, dst_base, add_f32, mul_f32);

    for (unsigned i = 0; i < N; i++) {
        union {
            float f;
            uint32_t u;
        } actual, expect;
        actual.f = dst[i];
        expect.f = (src[i] + 1.0f) * 2.0f;
        TEST_EQ32(actual.u, expect.u, 0x1340u + i);
    }
}

static void test_v_mixed_scalar_vector_predicate(void)
{
    enum { N = 32 };

    static uint32_t out[N];
    for (unsigned i = 0; i < N; i++) {
        out[i] = 0u;
    }

    const uint64_t out_base = (uint64_t)(uintptr_t)&out[0];
    const uint64_t threshold = 12u;
    const uint64_t lane_counter =
        linx_v03_launch_ops_mixed_pred(out_base, threshold);

    TEST_EQ64(lane_counter, N, 0x1360);

    for (unsigned i = 0; i < N; i++) {
        const uint32_t expect = (i < threshold) ? 1u : 0u;
        TEST_EQ32(out[i], expect, 0x1361u + i);
    }
}

void run_v03_vector_ops_matrix_tests(void)
{
    test_start(0x1300);
    uart_puts("v0.56 vector add/sub matrix ... ");
    test_v_add_sub_matrix();
    test_pass();

    test_start(0x1310);
    uart_puts("v0.56 vector float matrix ... ");
    test_v_float_matrix();
    test_pass();

    test_start(0x1320);
    uart_puts("v0.56 mixed scalar/vector predicate ... ");
    test_v_mixed_scalar_vector_predicate();
    test_pass();
}
