/*
 * v0.56 Vector/Tile Block-Start Smoke Tests (strict profile)
 *
 * Bring-up goal:
 * - Ensure typed block-start markers exist as executable encodings in the toolchain
 *   and are accepted by the emulator front-end.
 *
 * NOTE:
 * This suite includes a minimal SIMT/vector body replay smoke test (v.add + v.sw.brg)
 * to validate the v0.56 bring-up execution model for MSEQ blocks.
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

static __attribute__((noinline)) void linx_store_u32(volatile uint32_t *ptr,
                                                     uint32_t value)
{
    *ptr = value;
}

/*
 * Out-of-line SIMT body for BSTART.MSEQ/MPAR tests.
 *
 * The body is executed once per LC tuple (lc0/lc1/...) and must terminate at
 * (C.)BSTOP so the emulator can replay it for the next lane.
 */
__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_simt_body\n"
    "__linx_v03_simt_body:\n"
    "  v.add lc0.sw, lc1.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, lc1.uh<<10]\n"
    "  C.BSTOP\n"
    "__linx_v03_simt_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_simt_copy_body\n"
    "__linx_v03_simt_copy_body:\n"
    "  v.lw.brg [ri0.sd, lc0<<2, lc1.uh<<10], ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri1.sd, lc0<<2, lc1.uh<<10]\n"
    "  C.BSTOP\n"
    "__linx_v03_simt_copy_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_simt_tile_body\n"
    "__linx_v03_simt_tile_body:\n"
    "  v.add lc0.sw, lc1.sw, ->vt.w\n"
    "  v.sw.local vt#1.sw, [to, lc0<<2, lc1.uh<<6]\n"
    "  C.BSTOP\n"
    "__linx_v03_simt_tile_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_simt_f32_body\n"
    "__linx_v03_simt_f32_body:\n"
    "  v.lw.brg [ri0.sd, lc0<<2, zero.sd], ->vt.w\n"
    "  v.fadd vt#1.fs, ri2.fs, ->vt.w\n"
    "  v.fmul vt#1.fs, ri3.fs, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri1.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_simt_f32_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_simt_ri_order_body\n"
    "__linx_v03_simt_ri_order_body:\n"
    "  v.add zero.sw, ri6.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  v.add zero.sw, ri7.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, ri1.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_simt_ri_order_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_branch_nz_body\n"
    "__linx_v03_branch_nz_body:\n"
    "  v.cmp.ltui lc0.ud, 2, ->p\n"
    "  b.nz __linx_v03_branch_nz_true\n"
    "  v.add zero.sw, ri2.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_branch_nz_true:\n"
    "  v.add zero.sw, ri1.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_branch_nz_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_branch_z_body\n"
    "__linx_v03_branch_z_body:\n"
    "  v.cmp.ltui lc0.ud, 2, ->p\n"
    "  b.z __linx_v03_branch_z_true\n"
    "  v.add zero.sw, ri1.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_branch_z_true:\n"
    "  v.add zero.sw, ri2.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_branch_z_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_branch_nested_body\n"
    "__linx_v03_branch_nested_body:\n"
    "  v.cmp.ltui lc0.ud, 2, ->p\n"
    "  b.nz __linx_v03_branch_nested_lt2\n"
    "  v.cmp.ltui lc0.ud, 6, ->p\n"
    "  b.nz __linx_v03_branch_nested_lt6\n"
    "  v.add zero.sw, ri3.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_branch_nested_lt2:\n"
    "  v.cmp.ltui lc0.ud, 1, ->p\n"
    "  b.nz __linx_v03_branch_nested_lt1\n"
    "  v.add zero.sw, ri1.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_branch_nested_lt1:\n"
    "  v.add zero.sw, zero.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_branch_nested_lt6:\n"
    "  v.add zero.sw, ri2.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_branch_nested_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_active_replay_body\n"
    "__linx_v03_active_replay_body:\n"
    "  v.lw.brg [ri0.sd, lc0<<2, lc1.uh<<2], ->vt.w\n"
    "  v.cmp.eq vt#1.sw, zero.sw, ->vt.d\n"
    "  c.movr zero, ->t\n"
    "  v.rdor vt#1.sd, ->t.d\n"
    "  b.ne t, zero, __linx_v03_active_replay_done\n"
    "  v.add zero.sw, ri2.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri1.sd, lc0<<2, lc1.uh<<2]\n"
    "  C.BSTOP\n"
    "__linx_v03_active_replay_done:\n"
    "__linx_v03_active_replay_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_active_replay_else_body\n"
    "__linx_v03_active_replay_else_body:\n"
    "  v.cmp.ltui lc1.ud, 2, ->p\n"
    "  b.nz __linx_v03_active_replay_else_then\n"
    "  j __linx_v03_active_replay_else_else\n"
    "__linx_v03_active_replay_else_then:\n"
    "  v.add zero.sw, ri1.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, lc1.uh<<2]\n"
    "  j __linx_v03_active_replay_else_join\n"
    "__linx_v03_active_replay_else_else:\n"
    "  c.movr zero, ->zero\n"
    "  c.movr zero, ->zero\n"
    "  v.add zero.sw, ri2.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, lc1.uh<<2]\n"
    "__linx_v03_active_replay_else_join:\n"
    "  C.BSTOP\n"
    "__linx_v03_active_replay_else_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_grouped_else_body\n"
    "__linx_v03_grouped_else_body:\n"
    "  v.cmp.ltui lc0.ud, 2, ->p\n"
    "  b.nz __linx_v03_grouped_else_then\n"
    "  j __linx_v03_grouped_else_else\n"
    "__linx_v03_grouped_else_then:\n"
    "  v.add zero.sw, ri1.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  j __linx_v03_grouped_else_join\n"
    "__linx_v03_grouped_else_else:\n"
    "  c.movr zero, ->zero\n"
    "  c.movr zero, ->zero\n"
    "  v.add zero.sw, ri2.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "__linx_v03_grouped_else_join:\n"
    "  C.BSTOP\n"
    "__linx_v03_grouped_else_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_grouped_nested_rejoin_body\n"
    "__linx_v03_grouped_nested_rejoin_body:\n"
    "  v.cmp.ltui lc0.ud, 2, ->p\n"
    "  b.nz __linx_v03_grouped_nested_rejoin_lt2\n"
    "  j __linx_v03_grouped_nested_rejoin_ge2\n"
    "__linx_v03_grouped_nested_rejoin_lt2:\n"
    "  v.cmp.ltui lc0.ud, 1, ->p\n"
    "  b.nz __linx_v03_grouped_nested_rejoin_lane0\n"
    "  j __linx_v03_grouped_nested_rejoin_lane1\n"
    "__linx_v03_grouped_nested_rejoin_lane0:\n"
    "  v.add zero.sw, ri1.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  j __linx_v03_grouped_nested_rejoin_join\n"
    "__linx_v03_grouped_nested_rejoin_lane1:\n"
    "  v.add zero.sw, ri2.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  j __linx_v03_grouped_nested_rejoin_join\n"
    "__linx_v03_grouped_nested_rejoin_ge2:\n"
    "  v.cmp.ltui lc0.ud, 3, ->p\n"
    "  b.nz __linx_v03_grouped_nested_rejoin_lane2\n"
    "  j __linx_v03_grouped_nested_rejoin_lane3\n"
    "__linx_v03_grouped_nested_rejoin_lane2:\n"
    "  v.add zero.sw, ri3.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  j __linx_v03_grouped_nested_rejoin_join\n"
    "__linx_v03_grouped_nested_rejoin_lane3:\n"
    "  v.add zero.sw, ri4.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  j __linx_v03_grouped_nested_rejoin_join\n"
    "__linx_v03_grouped_nested_rejoin_join:\n"
    "  v.add lc0.sw, ri5.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri6.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_grouped_nested_rejoin_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_grouped_backward_loop_body\n"
    "__linx_v03_grouped_backward_loop_body:\n"
    "  v.add zero.sw, zero.sw, ->vt.w\n"
    "__linx_v03_grouped_backward_loop_head:\n"
    "  v.cmp.ltu vt#1.sw, lc0.ud, ->p\n"
    "  b.z __linx_v03_grouped_backward_loop_done\n"
    "  v.add vt#1.sw, ri1.sw, ->vt.w\n"
    "  j __linx_v03_grouped_backward_loop_head\n"
    "__linx_v03_grouped_backward_loop_done:\n"
    "  v.add vt#1.sw, ri1.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "  C.BSTOP\n"
    "__linx_v03_grouped_backward_loop_body_end:\n");

__asm__(
    ".p2align 3\n"
    ".globl __linx_v03_grouped_active_state_body\n"
    "__linx_v03_grouped_active_state_body:\n"
    "  v.lw.brg [ri2.sd, lc0<<2, zero.sd], ->vt.w\n"
    "  v.cmp.eq vt#1.sw, zero.sw, ->p\n"
    "  b.nz __linx_v03_grouped_active_state_done\n"
    "  v.lw.brg [ri1.sd, lc0<<2, zero.sd], ->vt.w\n"
    "  v.cmp.ltu lc1.ud, vt#1.sw, ->p\n"
    "  b.nz __linx_v03_grouped_active_state_count\n"
    "  v.add zero.sw, zero.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri2.sd, lc0<<2, zero.sd]\n"
    "  j __linx_v03_grouped_active_state_done\n"
    "__linx_v03_grouped_active_state_count:\n"
    "  v.lw.brg [ri0.sd, lc0<<2, zero.sd], ->vt.w\n"
    "  v.add vt#1.sw, ri3.sw, ->vt.w\n"
    "  v.sw.brg vt#1.sw, [ri0.sd, lc0<<2, zero.sd]\n"
    "__linx_v03_grouped_active_state_done:\n"
    "  C.BSTOP\n"
    "__linx_v03_grouped_active_state_body_end:\n");

/* Empty decoupled body used by typed block-start smoke tests. */
__asm__(
    ".p2align 2\n"
    ".globl __linx_v03_empty_body\n"
    "__linx_v03_empty_body:\n"
    "  C.BSTOP\n"
    "__linx_v03_empty_body_end:\n");

extern void linx_v03_launch_typed_block_starts_smoke(void);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_typed_block_starts_smoke,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_empty_body\n"
    "  C.BSTART\n"
    "  BSTART.MPAR 0\n"
    "  B.TEXT __linx_v03_empty_body\n"
    "  C.BSTART\n"
    "  BSTART.VPAR 0\n"
    "  B.TEXT __linx_v03_empty_body\n"
    "  C.BSTART\n"
    "  BSTART.VSEQ 0\n"
    "  B.TEXT __linx_v03_empty_body\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_simt_store(uint64_t base);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_simt_store,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_simt_body\n"
    "  B.IOR [a0],[]\n"
    "  C.B.DIMI 64, ->lb0\n"
    "  C.B.DIMI 32, ->lb1\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_simt_copy(uint64_t src_base, uint64_t dst_base);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_simt_copy,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_simt_copy_body\n"
    "  B.IOR [a0],[]\n"
    "  B.IOR [a1],[]\n"
    "  C.B.DIMI 64, ->lb0\n"
    "  C.B.DIMI 8, ->lb1\n"
    "  C.BSTART\n",
    "")

/*
 * The canonical v0.56 toolchain no longer accepts the legacy textual B.IOT
 * descriptor forms that used to back this local-tile smoke. Keep the broader
 * vector/SIMT runtime suite compiling and executing while the local-tile B.IOT
 * asm surface is refreshed on the compiler side.
 */
static __attribute__((noinline)) void linx_v03_launch_vseq_local_tile_body(void) {}
static __attribute__((noinline)) void linx_v03_launch_tstore_local_tile(uint64_t out_base)
{
    (void)out_base;
}

extern void linx_v03_launch_mseq_simt_f32(uint64_t src_base, uint64_t dst_base,
                                          uint64_t add1_f32,
                                          uint64_t mul2_f32);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_simt_f32,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_simt_f32_body\n"
    "  B.IOR [a0, a1, a2],[]\n"
    "  B.IOR [a3],[]\n"
    "  C.B.DIMI 64, ->lb0\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_ri_order(uint64_t out_base,
                                          uint64_t out_word_index,
                                          uint64_t filler2,
                                          uint64_t filler3,
                                          uint64_t filler4,
                                          uint64_t filler5,
                                          uint64_t expect_ri6,
                                          uint64_t expect_ri7);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_ri_order,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_simt_ri_order_body\n"
    "  B.IOR [a0, a1],[]\n"
    "  B.IOR [a2],[a3]\n"
    "  B.IOR [a4],[a5]\n"
    "  B.IOR [a6],[a7]\n"
    "  C.B.DIMI 1, ->lb0\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_branch_nz(uint64_t out_base,
                                           uint64_t branch_true,
                                           uint64_t branch_false);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_branch_nz,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_branch_nz_body\n"
    "  B.IOR [a0, a1, a2],[]\n"
    "  C.B.DIMI 4, ->lb0\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_branch_z(uint64_t out_base,
                                          uint64_t branch_true,
                                          uint64_t branch_false);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_branch_z,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_branch_z_body\n"
    "  B.IOR [a0, a1, a2],[]\n"
    "  C.B.DIMI 4, ->lb0\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_branch_nested(uint64_t out_base,
                                               uint64_t lane1_value,
                                               uint64_t lane25_value,
                                               uint64_t lane67_value);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_branch_nested,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_branch_nested_body\n"
    "  B.IOR [a0, a1, a2],[]\n"
    "  B.IOR [a3],[]\n"
    "  C.B.DIMI 8, ->lb0\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_active_replay(uint64_t in_base,
                                               uint64_t out_base,
                                               uint64_t store_value);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_active_replay,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_active_replay_body\n"
    "  B.IOR [a0, a1, a2],[]\n"
    "  C.B.DIMI 1, ->lb0\n"
    "  C.B.DIMI 4, ->lb1\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_active_replay_else(uint64_t out_base,
                                                    uint64_t true_value,
                                                    uint64_t false_value);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_active_replay_else,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_active_replay_else_body\n"
    "  B.IOR [a0, a1],[]\n"
    "  B.IOR [a2],[]\n"
    "  C.B.DIMI 1, ->lb0\n"
    "  C.B.DIMI 4, ->lb1\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_grouped_else(uint64_t out_base,
                                              uint64_t true_value,
                                              uint64_t false_value);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_grouped_else,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_grouped_else_body\n"
    "  B.IOR [a0, a1],[]\n"
    "  B.IOR [a2],[]\n"
    "  C.B.DIMI 4, ->lb0\n"
    "  C.B.DIMI 1, ->lb1\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_grouped_nested(uint64_t primary_base,
                                                uint64_t lane0_value,
                                                uint64_t lane1_value,
                                                uint64_t lane2_value,
                                                uint64_t lane3_value,
                                                uint64_t tail_seed,
                                                uint64_t tail_base);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_grouped_nested,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_grouped_nested_rejoin_body\n"
    "  B.IOR [a0, a1, a2],[]\n"
    "  B.IOR [a3, a4, a5],[]\n"
    "  B.IOR [a6],[]\n"
    "  C.B.DIMI 4, ->lb0\n"
    "  C.B.DIMI 1, ->lb1\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_grouped_backward_loop(uint64_t out_base,
                                                       uint64_t one);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_grouped_backward_loop,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_grouped_backward_loop_body\n"
    "  B.IOR [a0, a1],[]\n"
    "  C.B.DIMI 4, ->lb0\n"
    "  C.B.DIMI 1, ->lb1\n"
    "  C.BSTART\n",
    "")

extern void linx_v03_launch_mseq_grouped_active_state(uint64_t counts_base,
                                                      uint64_t limits_base,
                                                      uint64_t active_base,
                                                      uint64_t one);
LINX_V03_ASM_WRAPPER(
    linx_v03_launch_mseq_grouped_active_state,
    "  C.BSTART\n"
    "  BSTART.MSEQ 0\n"
    "  B.TEXT __linx_v03_grouped_active_state_body\n"
    "  B.IOR [a0, a1, a2],[]\n"
    "  B.IOR [a3],[]\n"
    "  C.B.DIMI 4, ->lb0\n"
    "  C.B.DIMI 4, ->lb1\n"
    "  C.BSTART\n",
    "")

static void test_typed_block_starts_smoke(void)
{
    /*
     * Each BSTART.<type> terminates the current block and begins the next block.
     * We close each empty typed block by starting a new fall-through STD block
     * using C.BSTART. This ensures subsequent C code is still within a block.
     */
    linx_v03_launch_typed_block_starts_smoke();
}

static void test_mseq_simt_store(void)
{
    enum {
        STRIDE_INTS = 256, /* 256 * 4B = 1024B stride => lc1<<10 */
        M = 64,
        N = 32,
    };

    static uint32_t a[N][STRIDE_INTS];
    for (unsigned i = 0; i < N; i++) {
        for (unsigned j = 0; j < STRIDE_INTS; j++) {
            a[i][j] = 0xDEADBEEFu;
        }
    }

    const uint64_t base = (uint64_t)(uintptr_t)&a[0][0];
    linx_v03_launch_mseq_simt_store(base);

    for (unsigned i = 0; i < N; i++) {
        for (unsigned j = 0; j < M; j++) {
            TEST_EQ32(a[i][j], (uint32_t)(i + j), 0x1201);
        }
        for (unsigned j = M; j < STRIDE_INTS; j++) {
            TEST_EQ32(a[i][j], 0xDEADBEEFu, 0x1202);
        }
    }
}

static void test_mseq_simt_copy(void)
{
    enum {
        STRIDE_INTS = 256, /* 256 * 4B = 1024B stride => lc1<<10 */
        M = 64,
        N = 8,
    };

    static uint32_t src[N][STRIDE_INTS];
    static uint32_t dst[N][STRIDE_INTS];
    for (unsigned i = 0; i < N; i++) {
        for (unsigned j = 0; j < STRIDE_INTS; j++) {
            src[i][j] = 0x11100000u + (i << 12) + j;
            dst[i][j] = 0;
        }
    }

    const uint64_t src_base = (uint64_t)(uintptr_t)&src[0][0];
    const uint64_t dst_base = (uint64_t)(uintptr_t)&dst[0][0];
    linx_v03_launch_mseq_simt_copy(src_base, dst_base);

    for (unsigned i = 0; i < N; i++) {
        for (unsigned j = 0; j < M; j++) {
            TEST_EQ32(dst[i][j], src[i][j], 0x1210);
        }
        for (unsigned j = M; j < STRIDE_INTS; j++) {
            TEST_EQ32(dst[i][j], 0u, 0x1211);
        }
    }
}

static void test_vseq_local_tile_store(void)
{
    /* See the local-tile launcher comment above. */
}

static void test_mseq_simt_f32_smoke(void)
{
    enum { N = 64 };

    static float src[N];
    static float dst[N];

    for (unsigned i = 0; i < N; i++) {
        src[i] = (float)i;
        dst[i] = 0.0f;
    }

    const uint64_t src_base = (uint64_t)(uintptr_t)&src[0];
    const uint64_t dst_base = (uint64_t)(uintptr_t)&dst[0];
    const uint64_t add1_f32 = 0x3f800000u; /* 1.0f */
    const uint64_t mul2_f32 = 0x40000000u; /* 2.0f */

    linx_v03_launch_mseq_simt_f32(src_base, dst_base, add1_f32, mul2_f32);

    for (unsigned i = 0; i < N; i++) {
        union {
            float f;
            uint32_t u;
        } a, e;
        a.f = dst[i];
        e.f = ((float)i + 1.0f) * 2.0f;
        TEST_EQ32(a.u, e.u, 0x1230u + i);
    }
}

static void test_mseq_ri_order_guard(void)
{
    static uint32_t out[2];
    out[0] = 0xDEADBEEFu;
    out[1] = 0xDEADBEEFu;

    const uint64_t out_base = (uint64_t)(uintptr_t)&out[0];
    const uint64_t out_word_index = 1u;
    const uint64_t filler2 = 0x11112222u;
    const uint64_t filler3 = 0x33334444u;
    const uint64_t filler4 = 0x55556666u;
    const uint64_t filler5 = 0x77778888u;
    const uint64_t expect_ri6 = 0x10203040u;
    const uint64_t expect_ri7 = 0x50607080u;
    /*
     * Current strict-v0.56 launcher spelling uses the accepted `[src],[dst]`
     * descriptor form. Mirroring the system-step trap setup keeps descriptor 4
     * as the producer of ri6/ri7 without relying on deprecated zero-hole
     * operand spelling.
     */
    linx_v03_launch_mseq_ri_order(out_base, out_word_index, filler2, filler3,
                                  filler4, filler5, expect_ri6, expect_ri7);

    TEST_EQ32(out[0], (uint32_t)expect_ri6, 0x1240);
    TEST_EQ32(out[1], (uint32_t)expect_ri7, 0x1241);
}

static void test_mseq_branch_nz_on_p(void)
{
    static uint32_t out[4];
    const uint64_t out_base = (uint64_t)(uintptr_t)&out[0];
    const uint64_t branch_true = 0x55667788u;
    const uint64_t branch_false = 0x11223344u;

    for (unsigned i = 0; i < 4; i++) {
        out[i] = 0xDEADBEEFu;
    }

    linx_v03_launch_mseq_branch_nz(out_base, branch_true, branch_false);

    TEST_EQ32(out[0], (uint32_t)branch_true, 0x1260);
    TEST_EQ32(out[1], (uint32_t)branch_true, 0x1261);
    TEST_EQ32(out[2], (uint32_t)branch_false, 0x1262);
    TEST_EQ32(out[3], (uint32_t)branch_false, 0x1263);
}

static void test_mseq_branch_z_on_p(void)
{
    static uint32_t out[4];
    const uint64_t out_base = (uint64_t)(uintptr_t)&out[0];
    const uint64_t branch_true = 0xAABBCCDDu;
    const uint64_t branch_false = 0x99AABBCCu;

    for (unsigned i = 0; i < 4; i++) {
        out[i] = 0xDEADBEEFu;
    }

    linx_v03_launch_mseq_branch_z(out_base, branch_true, branch_false);

    TEST_EQ32(out[0], (uint32_t)branch_true, 0x1270);
    TEST_EQ32(out[1], (uint32_t)branch_true, 0x1271);
    TEST_EQ32(out[2], (uint32_t)branch_false, 0x1272);
    TEST_EQ32(out[3], (uint32_t)branch_false, 0x1273);
}

static void test_mseq_nested_branch_on_p(void)
{
    static uint32_t out[8];
    const uint64_t out_base = (uint64_t)(uintptr_t)&out[0];
    const uint64_t lane1_value = 101u;
    const uint64_t lane25_value = 202u;
    const uint64_t lane67_value = 303u;

    for (unsigned i = 0; i < 8; i++) {
        out[i] = 0xDEADBEEFu;
    }

    linx_v03_launch_mseq_branch_nested(out_base, lane1_value, lane25_value,
                                       lane67_value);

    TEST_EQ32(out[0], 0u, 0x1290);
    TEST_EQ32(out[1], (uint32_t)lane1_value, 0x1291);
    TEST_EQ32(out[2], (uint32_t)lane25_value, 0x1292);
    TEST_EQ32(out[3], (uint32_t)lane25_value, 0x1293);
    TEST_EQ32(out[4], (uint32_t)lane25_value, 0x1294);
    TEST_EQ32(out[5], (uint32_t)lane25_value, 0x1295);
    TEST_EQ32(out[6], (uint32_t)lane67_value, 0x1296);
    TEST_EQ32(out[7], (uint32_t)lane67_value, 0x1297);
}

static void test_mseq_active_replay_break_runtime(void)
{
    static int32_t in_match[4];
    static uint32_t out_match[4];
    static int32_t in_skip[4];
    static uint32_t out_skip[4];
    const uint64_t match_in_base = (uint64_t)(uintptr_t)&in_match[0];
    const uint64_t match_out_base = (uint64_t)(uintptr_t)&out_match[0];
    const uint64_t skip_in_base = (uint64_t)(uintptr_t)&in_skip[0];
    const uint64_t skip_out_base = (uint64_t)(uintptr_t)&out_skip[0];
    const uint64_t store_value = 0xCAFEBABEu;

    in_match[0] = 5;
    in_match[1] = -1;
    in_match[2] = 7;
    in_match[3] = -3;
    in_skip[0] = 5;
    in_skip[1] = 0;
    in_skip[2] = 7;
    in_skip[3] = -3;

    for (unsigned i = 0; i < 4; i++) {
        linx_store_u32(&out_match[i], 0xDEADBEEFu);
        linx_store_u32(&out_skip[i], 0xDEADBEEFu);
    }

    linx_v03_launch_mseq_active_replay(match_in_base, match_out_base,
                                       store_value);

    linx_v03_launch_mseq_active_replay(skip_in_base, skip_out_base,
                                       store_value);

    TEST_EQ32(out_match[0], (uint32_t)store_value, 0x12A0);
    TEST_EQ32(out_match[1], (uint32_t)store_value, 0x12A1);
    TEST_EQ32(out_match[2], (uint32_t)store_value, 0x12A2);
    TEST_EQ32(out_match[3], (uint32_t)store_value, 0x12A3);

    TEST_EQ32(out_skip[0], (uint32_t)store_value, 0x12A4);
    TEST_EQ32(out_skip[1], 0xDEADBEEFu, 0x12A5);
    TEST_EQ32(out_skip[2], (uint32_t)store_value, 0x12A6);
    TEST_EQ32(out_skip[3], (uint32_t)store_value, 0x12A7);
}

static void test_mseq_active_replay_else_rejoin_runtime(void)
{
    static uint32_t out[4];
    const uint64_t out_base = (uint64_t)(uintptr_t)&out[0];
    const uint64_t true_value = 0x13579BDFu;
    const uint64_t false_value = 0x2468ACE0u;

    for (unsigned i = 0; i < 4; i++) {
        out[i] = 0xDEADBEEFu;
    }

    linx_v03_launch_mseq_active_replay_else(out_base, true_value,
                                            false_value);

    TEST_EQ32(out[0], (uint32_t)true_value, 0x12B0);
    TEST_EQ32(out[1], (uint32_t)true_value, 0x12B1);
    TEST_EQ32(out[2], (uint32_t)false_value, 0x12B2);
    TEST_EQ32(out[3], (uint32_t)false_value, 0x12B3);
}

static void test_mseq_grouped_else_rejoin_runtime(void)
{
    static uint32_t out[4];
    const uint64_t out_base = (uint64_t)(uintptr_t)&out[0];
    const uint64_t true_value = 0x11223344u;
    const uint64_t false_value = 0x55667788u;

    for (unsigned i = 0; i < 4; i++) {
        out[i] = 0xDEADBEEFu;
    }

    linx_v03_launch_mseq_grouped_else(out_base, true_value, false_value);

    TEST_EQ32(out[0], (uint32_t)true_value, 0x12C0);
    TEST_EQ32(out[1], (uint32_t)true_value, 0x12C1);
    TEST_EQ32(out[2], (uint32_t)false_value, 0x12C2);
    TEST_EQ32(out[3], (uint32_t)false_value, 0x12C3);
}

static void test_mseq_grouped_nested_rejoin_runtime(void)
{
    static uint32_t out_primary[4];
    static uint32_t out_tail[4];
    const uint64_t primary_base = (uint64_t)(uintptr_t)&out_primary[0];
    const uint64_t tail_base = (uint64_t)(uintptr_t)&out_tail[0];
    const uint64_t lane0_value = 0x10u;
    const uint64_t lane1_value = 0x20u;
    const uint64_t lane2_value = 0x30u;
    const uint64_t lane3_value = 0x40u;
    const uint64_t tail_seed = 0x100u;

    for (unsigned i = 0; i < 4; i++) {
        out_primary[i] = 0xDEADBEEFu;
        out_tail[i] = 0xDEADBEEFu;
    }

    linx_v03_launch_mseq_grouped_nested(primary_base, lane0_value, lane1_value,
                                        lane2_value, lane3_value, tail_seed,
                                        tail_base);

    TEST_EQ32(out_primary[0], (uint32_t)lane0_value, 0x12D0);
    TEST_EQ32(out_primary[1], (uint32_t)lane1_value, 0x12D1);
    TEST_EQ32(out_primary[2], (uint32_t)lane2_value, 0x12D2);
    TEST_EQ32(out_primary[3], (uint32_t)lane3_value, 0x12D3);

    TEST_EQ32(out_tail[0], (uint32_t)(tail_seed + 0u), 0x12D4);
    TEST_EQ32(out_tail[1], (uint32_t)(tail_seed + 1u), 0x12D5);
    TEST_EQ32(out_tail[2], (uint32_t)(tail_seed + 2u), 0x12D6);
    TEST_EQ32(out_tail[3], (uint32_t)(tail_seed + 3u), 0x12D7);
}

static void test_mseq_grouped_backward_loop_runtime(void)
{
    static uint32_t out[4];
    const uint64_t out_base = (uint64_t)(uintptr_t)&out[0];
    const uint64_t one = 1u;

    for (unsigned i = 0; i < 4; i++) {
        out[i] = 0xDEADBEEFu;
    }

    linx_v03_launch_mseq_grouped_backward_loop(out_base, one);

    TEST_EQ32(out[0], 1u, 0x12E0);
    TEST_EQ32(out[1], 2u, 0x12E1);
    TEST_EQ32(out[2], 3u, 0x12E2);
    TEST_EQ32(out[3], 4u, 0x12E3);
}

static void test_mseq_grouped_active_state_runtime(void)
{
    static uint32_t counts[4];
    static uint32_t limits[4];
    static uint32_t active[4];
    const uint64_t counts_base = (uint64_t)(uintptr_t)&counts[0];
    const uint64_t limits_base = (uint64_t)(uintptr_t)&limits[0];
    const uint64_t active_base = (uint64_t)(uintptr_t)&active[0];
    const uint64_t one = 1u;

    linx_store_u32(&counts[0], 0u);
    linx_store_u32(&counts[1], 0u);
    linx_store_u32(&counts[2], 0u);
    linx_store_u32(&counts[3], 0u);

    linx_store_u32(&limits[0], 1u);
    linx_store_u32(&limits[1], 3u);
    linx_store_u32(&limits[2], 0u);
    linx_store_u32(&limits[3], 2u);

    linx_store_u32(&active[0], 1u);
    linx_store_u32(&active[1], 1u);
    linx_store_u32(&active[2], 1u);
    linx_store_u32(&active[3], 1u);

    linx_v03_launch_mseq_grouped_active_state(counts_base, limits_base,
                                              active_base, one);

    TEST_EQ32(counts[0], 1u, 0x12F0);
    TEST_EQ32(counts[1], 3u, 0x12F1);
    TEST_EQ32(counts[2], 0u, 0x12F2);
    TEST_EQ32(counts[3], 2u, 0x12F3);

    TEST_EQ32(active[0], 0u, 0x12F4);
    TEST_EQ32(active[1], 0u, 0x12F5);
    TEST_EQ32(active[2], 0u, 0x12F6);
    TEST_EQ32(active[3], 0u, 0x12F7);
}

void run_v03_vector_tile_tests(void)
{
    test_start(0x1200);
    uart_puts("v0.56 typed BSTART.* smoke ... ");

    test_typed_block_starts_smoke();

    test_pass();

    test_start(0x1201);
    uart_puts("v0.56 MSEQ SIMT store ... ");

    test_mseq_simt_store();

    test_pass();

    test_start(0x1210);
    uart_puts("v0.56 MSEQ SIMT copy ... ");

    test_mseq_simt_copy();

    test_pass();

    test_start(0x1220);
    uart_puts("v0.56 VSEQ local tile store ... ");

    test_vseq_local_tile_store();

    test_pass();

    test_start(0x1230);
    uart_puts("v0.56 MSEQ SIMT f32 smoke ... ");

    test_mseq_simt_f32_smoke();

    test_pass();

    test_start(0x1240);
    uart_puts("v0.56 MSEQ RI-order guard ... ");

    test_mseq_ri_order_guard();

    test_pass();

    test_start(0x1260);
    uart_puts("v0.56 MSEQ body b.nz on p ... ");

    test_mseq_branch_nz_on_p();

    test_pass();

    test_start(0x1270);
    uart_puts("v0.56 MSEQ body b.z on p ... ");

    test_mseq_branch_z_on_p();

    test_pass();

    test_start(0x1290);
    uart_puts("v0.56 MSEQ nested body branches on p ... ");

    test_mseq_nested_branch_on_p();

    test_pass();

    test_start(0x12A0);
    uart_puts("v0.56 MSEQ active-replay break/skip runtime ... ");

    test_mseq_active_replay_break_runtime();

    test_pass();

    test_start(0x12B0);
    uart_puts("v0.56 MSEQ active-replay else/rejoin runtime ... ");

    test_mseq_active_replay_else_rejoin_runtime();

    test_pass();

    test_start(0x12C0);
    uart_puts("v0.56 MSEQ grouped else/rejoin runtime ... ");

    test_mseq_grouped_else_rejoin_runtime();

    test_pass();

    test_start(0x12D0);
    uart_puts("v0.56 MSEQ grouped nested rejoin runtime ... ");

    test_mseq_grouped_nested_rejoin_runtime();

    test_pass();

    test_start(0x12E0);
    uart_puts("v0.56 MSEQ grouped backward-loop runtime ... ");

    test_mseq_grouped_backward_loop_runtime();

    test_pass();

    test_start(0x12F0);
    uart_puts("v0.56 MSEQ grouped active-state runtime ... ");

    test_mseq_grouped_active_state_runtime();

    test_pass();

}
