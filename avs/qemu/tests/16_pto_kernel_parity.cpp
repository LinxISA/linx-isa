#include <stdint.h>
#include <common/linx_lowp_types.hpp>

#if defined(PTO_HOST_SIM)
#include <stdio.h>
#else
#include "linx_test.h"
#endif

using usize = __SIZE_TYPE__;
using pto::float_to_fp16;
using pto::fp16_t;

extern "C" void tload_store_i32(int *src_ptr, int *dst_ptr);
extern "C" void mamulb_i32(int *lhs_ptr, int *rhs_ptr, int *dst_ptr);
extern "C" void tmatmul_acc_i32(int *lhs_ptr, int *rhs_ptr, int *dst_ptr);
extern "C" void gemm_i32(int *lhs_ptr, int *rhs_ptr, int *dst_ptr);
extern "C" void gemm_basic_f32(float *lhs_ptr, float *rhs_ptr, float *dst_ptr);
extern "C" void gemm_demo_f32(float *out_ptr, float *a_ptr, float *b_ptr);
extern "C" void gemm_performance_f32(float *lhs_ptr, float *rhs_ptr,
                                        float *dst_ptr, int repeat_tiles);
extern "C" void add_custom_f32(float *x_ptr, float *y_ptr, float *z_ptr);
extern "C" void flash_attention_i32(int *q_ptr, int *k_ptr, int *v_ptr,
                                       int *out_ptr);
extern "C" void flash_attention_demo_f32(float *out_ptr, float *q_ptr,
                                           float *k_ptr, float *v_ptr);
extern "C" void flash_attention_masked_f32(float *out_ptr, float *q_ptr,
                                             float *k_ptr, float *v_ptr);
extern "C" void fa_performance_f32(float *out_ptr, float *q_ptr,
                                     float *k_ptr, float *v_ptr,
                                     int repeat_passes);
extern "C" void mla_attention_demo_f32(float *out_ptr, float *q_ptr,
                                         float *k_ptr, float *v_ptr,
                                         float *wq_ptr, float *wk_ptr,
                                         float *wv_ptr, float *wo_ptr);
extern "C" void flash_attention_cube_f16(fp16_t *out_ptr, fp16_t *q_ptr,
                                         fp16_t *k_ptr, fp16_t *v_ptr);
extern "C" void flash_attention_vec_f32(float *out_ptr, float *q_ptr,
                                        float *k_ptr, float *v_ptr);
extern "C" void flash_attention_vec_f16(fp16_t *out_ptr, fp16_t *q_ptr,
                                        fp16_t *k_ptr, fp16_t *v_ptr);
extern "C" void gqa_f16(fp16_t *out_ptr, fp16_t *q_ptr, fp16_t *k_ptr,
                        fp16_t *v_ptr);
extern "C" void sparse_attention_local_f16(fp16_t *out_ptr, fp16_t *q_ptr,
                                           fp16_t *k_ptr, fp16_t *v_ptr,
                                           int window);
extern "C" void rmsnorm_f16(fp16_t *out_ptr, fp16_t *x_ptr, fp16_t *gamma_ptr,
                            float eps);
extern "C" void gelu_f32(float *out_ptr, float *x_ptr, int n);
extern "C" void argmax_f32(int *idx_ptr, float *x_ptr, int rows, int cols);
extern "C" void gather_f32(float *out_ptr, float *in_ptr, int *indices_ptr,
                           int n);
extern "C" void concat_f32(float *out_ptr, float *a_ptr, float *b_ptr, int n_a,
                           int n_b);
extern "C" void scatter_f32(float *out_ptr, float *in_ptr, int *indices_ptr,
                            float *updates_ptr, int n);
extern "C" void permute_nhwc_nchw_f32(float *out_ptr, float *in_ptr, int n,
                                      int h, int w, int c);
extern "C" void transpose_large_f32(float *out_ptr, float *in_ptr, int rows,
                                    int cols);
extern "C" void unsorted_segment_sum_f32(float *out_ptr, int *segment_ids_ptr,
                                         float *data_ptr, int n,
                                         int num_segments);
extern "C" void unique_i32(int *out_values_ptr, int *out_count_ptr,
                           int *in_values_ptr, int n);

#ifndef PTO_QEMU_SMOKE
#define PTO_QEMU_SMOKE 0
#endif

namespace {

static inline uint64_t fnv1a_bytes(const void *ptr, usize bytes) {
  const uint8_t *p = static_cast<const uint8_t *>(ptr);
  uint64_t h = 1469598103934665603ull;
  for (usize i = 0; i < bytes; ++i) {
    h ^= static_cast<uint64_t>(p[i]);
    h *= 1099511628211ull;
  }
  return h;
}

static inline uint32_t lcg32(uint32_t &state) {
  state = state * 1664525u + 1013904223u;
  return state;
}

static void seed_i32(int *buf, usize n, uint32_t seed) {
  uint32_t s = seed;
  for (usize i = 0; i < n; ++i) {
    uint32_t v = lcg32(s);
    buf[i] = static_cast<int32_t>((v & 0x7fffu) - 0x3fffu);
  }
}

static void seed_f32(float *buf, usize n, uint32_t seed) {
  uint32_t s = seed;
  for (usize i = 0; i < n; ++i) {
    uint32_t v = lcg32(s);
    uint32_t m = (v & 0xffffu);
    buf[i] = static_cast<float>(static_cast<int32_t>(m) - 32768) / 8192.0f;
  }
}

static void zero_i32(int *buf, usize n) {
  for (usize i = 0; i < n; ++i)
    buf[i] = 0;
}

static void zero_f32(float *buf, usize n) {
  for (usize i = 0; i < n; ++i)
    buf[i] = 0.0f;
}

static void seed_fp16(fp16_t *buf, usize n, uint32_t seed) {
  uint32_t s = seed;
  for (usize i = 0; i < n; ++i) {
    uint32_t v = lcg32(s);
    uint32_t m = (v & 0xffffu);
    float f = static_cast<float>(static_cast<int32_t>(m) - 32768) / 8192.0f;
    buf[i] = float_to_fp16(f);
  }
}

static void zero_fp16(fp16_t *buf, usize n) {
  for (usize i = 0; i < n; ++i)
    buf[i] = fp16_t{0u};
}

static void seed_index_range(int *buf, usize n, int mod, uint32_t seed) {
  uint32_t s = seed;
  const int safe_mod = mod < 1 ? 1 : mod;
  for (usize i = 0; i < n; ++i) {
    buf[i] = static_cast<int>(lcg32(s) % static_cast<uint32_t>(safe_mod));
  }
}

#if defined(PTO_HOST_SIM)
static void emit_digest(const char *name, uint64_t digest) {
  printf("PTO_DIGEST %s 0x%016llX\n", name,
         static_cast<unsigned long long>(digest));
}
static void emit_stage(const char *name) { printf("PTO_STAGE %s\n", name); }
#else
static void emit_digest(const char *name, uint64_t digest) {
  uart_puts("PTO_DIGEST ");
  uart_puts(name);
  uart_puts(" 0x");
  uart_puthex64(digest);
  uart_puts("\r\n");
}
static void emit_stage(const char *name) {
  uart_puts("PTO_STAGE ");
  uart_puts(name);
  uart_puts("\r\n");
}
#endif

static void run_all_kernels_emit_digest() {
  emit_stage("begin");
  constexpr usize kMatElems = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 256u;
  constexpr usize kVecElems = PTO_QEMU_SMOKE ? 32u * 32u : 1024u * 1024u;
  constexpr usize kFlashI32Q = PTO_QEMU_SMOKE ? 16u * 4u : 256u * 4u;
  constexpr usize kFlashI32K = PTO_QEMU_SMOKE ? 4u * 16u : 4u * 256u;
  constexpr usize kFlashI32V = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 16u;
  constexpr usize kFlashI32O = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 16u;
  constexpr usize kFlashF32Q = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 16u;
  constexpr usize kFlashF32K = PTO_QEMU_SMOKE ? 16u * 16u : 16u * 256u;
  constexpr usize kFlashF32V = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 16u;
  constexpr usize kFlashF32O = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 16u;
  constexpr usize kFlashMaskQ = PTO_QEMU_SMOKE ? 18u * 16u : 130u * 16u;
  constexpr usize kFlashMaskK = PTO_QEMU_SMOKE ? 16u * 18u : 16u * 130u;
  constexpr usize kFlashMaskV = PTO_QEMU_SMOKE ? 18u * 16u : 130u * 16u;
  constexpr usize kFlashMaskO = PTO_QEMU_SMOKE ? 18u * 16u : 130u * 16u;
  constexpr usize kMlaQ = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 16u;
  constexpr usize kMlaW = 16u * 4u;
  constexpr usize kMlaWo = 4u * 16u;
  constexpr usize kMlaO = PTO_QEMU_SMOKE ? 16u * 16u : 256u * 16u;
  constexpr usize kLowpFlashElems = PTO_QEMU_SMOKE ? 16u * 16u : 128u * 16u;
  constexpr usize kGqaQElems = PTO_QEMU_SMOKE ? 2u * 16u * 16u : 4u * 128u * 16u;
  constexpr usize kGqaKVElems = PTO_QEMU_SMOKE ? 1u * 16u * 16u : 2u * 128u * 16u;
  constexpr usize kRmsElems = PTO_QEMU_SMOKE ? 16u * 16u : 128u * 16u;
  constexpr usize kRmsGammaElems = 16u;
  constexpr usize kSmallVec = PTO_QEMU_SMOKE ? 64u : 1024u;
  constexpr usize kSmallTable = PTO_QEMU_SMOKE ? 97u : 2048u;
  constexpr usize kSegments = PTO_QEMU_SMOKE ? 8u : 64u;
  constexpr usize kUniqueN = PTO_QEMU_SMOKE ? 64u : 1024u;
  constexpr int kGeluN = PTO_QEMU_SMOKE ? 64 : 256;
  constexpr int kArgmaxRows = PTO_QEMU_SMOKE ? 8 : 32;
  constexpr int kArgmaxCols = PTO_QEMU_SMOKE ? 8 : 32;
  constexpr int kPermuteN = PTO_QEMU_SMOKE ? 1 : 2;
  constexpr int kPermuteH = PTO_QEMU_SMOKE ? 4 : 8;
  constexpr int kPermuteW = PTO_QEMU_SMOKE ? 4 : 8;
  constexpr int kPermuteC = PTO_QEMU_SMOKE ? 4 : 8;
  constexpr int kTransposeRows = PTO_QEMU_SMOKE ? 8 : 32;
  constexpr int kTransposeCols = PTO_QEMU_SMOKE ? 8 : 32;

  alignas(64) static int iA[kMatElems];
  alignas(64) static int iB[kMatElems];
  alignas(64) static int iC[kMatElems];
  alignas(64) static int iX[kVecElems];
  alignas(64) static int iY[kVecElems];

  alignas(64) static float fA[kMatElems];
  alignas(64) static float fB[kMatElems];
  alignas(64) static float fC[kMatElems];
  alignas(64) static float fX[kVecElems];
  alignas(64) static float fY[kVecElems];
  alignas(64) static float fZ[kVecElems];

  alignas(64) static int flashQ[kFlashI32Q];
  alignas(64) static int flashK[kFlashI32K];
  alignas(64) static int flashV[kFlashI32V];
  alignas(64) static int flashO[kFlashI32O];

  alignas(64) static float flashQf[kFlashF32Q];
  alignas(64) static float flashKf[kFlashF32K];
  alignas(64) static float flashVf[kFlashF32V];
  alignas(64) static float flashOf[kFlashF32O];

  alignas(64) static float flashMaskQ[kFlashMaskQ];
  alignas(64) static float flashMaskK[kFlashMaskK];
  alignas(64) static float flashMaskV[kFlashMaskV];
  alignas(64) static float flashMaskO[kFlashMaskO];

  alignas(64) static float mlaQ[kMlaQ];
  alignas(64) static float mlaK[kMlaQ];
  alignas(64) static float mlaV[kMlaQ];
  alignas(64) static float mlaWq[kMlaW];
  alignas(64) static float mlaWk[kMlaW];
  alignas(64) static float mlaWv[kMlaW];
  alignas(64) static float mlaWo[kMlaWo];
  alignas(64) static float mlaO[kMlaO];
  alignas(64) static fp16_t flashCubeQ[kLowpFlashElems];
  alignas(64) static fp16_t flashCubeK[kLowpFlashElems];
  alignas(64) static fp16_t flashCubeV[kLowpFlashElems];
  alignas(64) static fp16_t flashCubeO[kLowpFlashElems];
  alignas(64) static fp16_t flashVecQ[kLowpFlashElems];
  alignas(64) static fp16_t flashVecK[kLowpFlashElems];
  alignas(64) static fp16_t flashVecV[kLowpFlashElems];
  alignas(64) static fp16_t flashVecO[kLowpFlashElems];
  alignas(64) static fp16_t gqaQ[kGqaQElems];
  alignas(64) static fp16_t gqaK[kGqaKVElems];
  alignas(64) static fp16_t gqaV[kGqaKVElems];
  alignas(64) static fp16_t gqaO[kGqaQElems];
  alignas(64) static fp16_t sparseQ[kLowpFlashElems];
  alignas(64) static fp16_t sparseK[kLowpFlashElems];
  alignas(64) static fp16_t sparseV[kLowpFlashElems];
  alignas(64) static fp16_t sparseO[kLowpFlashElems];
  alignas(64) static fp16_t rmsX[kRmsElems];
  alignas(64) static fp16_t rmsGamma[kRmsGammaElems];
  alignas(64) static fp16_t rmsO[kRmsElems];
  alignas(64) static float smallIn[kSmallTable];
  alignas(64) static float smallOut[kSmallVec];
  alignas(64) static float smallAux[kSmallVec];
  alignas(64) static int smallIdx[kSmallVec];
  alignas(64) static int argmaxOut[kSmallVec];
  alignas(64) static float segData[kSmallVec];
  alignas(64) static int segIds[kSmallVec];
  alignas(64) static float segOut[kSegments];
  alignas(64) static int uniqueIn[kUniqueN];
  alignas(64) static int uniqueOut[kUniqueN];
  alignas(64) static int uniqueCount[1];

  seed_i32(iA, kMatElems, 0x1001u);
  seed_i32(iB, kMatElems, 0x1002u);
  zero_i32(iC, kMatElems);

  seed_i32(iX, kVecElems, 0x1003u);
  zero_i32(iY, kVecElems);

  seed_f32(fA, kMatElems, 0x2001u);
  seed_f32(fB, kMatElems, 0x2002u);
  zero_f32(fC, kMatElems);

  seed_f32(fX, kVecElems, 0x2003u);
  seed_f32(fY, kVecElems, 0x2004u);
  zero_f32(fZ, kVecElems);

  seed_i32(flashQ, kFlashI32Q, 0x3001u);
  seed_i32(flashK, kFlashI32K, 0x3002u);
  seed_i32(flashV, kFlashI32V, 0x3003u);
  zero_i32(flashO, kFlashI32O);

  seed_f32(flashQf, kFlashF32Q, 0x4001u);
  seed_f32(flashKf, kFlashF32K, 0x4002u);
  seed_f32(flashVf, kFlashF32V, 0x4003u);
  zero_f32(flashOf, kFlashF32O);

  seed_f32(flashMaskQ, kFlashMaskQ, 0x5001u);
  seed_f32(flashMaskK, kFlashMaskK, 0x5002u);
  seed_f32(flashMaskV, kFlashMaskV, 0x5003u);
  zero_f32(flashMaskO, kFlashMaskO);

  seed_f32(mlaQ, kMlaQ, 0x6001u);
  seed_f32(mlaK, kMlaQ, 0x6002u);
  seed_f32(mlaV, kMlaQ, 0x6003u);
  seed_f32(mlaWq, kMlaW, 0x6004u);
  seed_f32(mlaWk, kMlaW, 0x6005u);
  seed_f32(mlaWv, kMlaW, 0x6006u);
  seed_f32(mlaWo, kMlaWo, 0x6007u);
  zero_f32(mlaO, kMlaO);
  seed_fp16(flashCubeQ, kLowpFlashElems, 0x7001u);
  seed_fp16(flashCubeK, kLowpFlashElems, 0x7002u);
  seed_fp16(flashCubeV, kLowpFlashElems, 0x7003u);
  zero_fp16(flashCubeO, kLowpFlashElems);
  seed_fp16(flashVecQ, kLowpFlashElems, 0x7004u);
  seed_fp16(flashVecK, kLowpFlashElems, 0x7005u);
  seed_fp16(flashVecV, kLowpFlashElems, 0x7006u);
  zero_fp16(flashVecO, kLowpFlashElems);
  seed_fp16(gqaQ, kGqaQElems, 0x7007u);
  seed_fp16(gqaK, kGqaKVElems, 0x7008u);
  seed_fp16(gqaV, kGqaKVElems, 0x7009u);
  zero_fp16(gqaO, kGqaQElems);
  seed_fp16(sparseQ, kLowpFlashElems, 0x700Au);
  seed_fp16(sparseK, kLowpFlashElems, 0x700Bu);
  seed_fp16(sparseV, kLowpFlashElems, 0x700Cu);
  zero_fp16(sparseO, kLowpFlashElems);
  seed_fp16(rmsX, kRmsElems, 0x700Du);
  seed_fp16(rmsGamma, kRmsGammaElems, 0x700Eu);
  zero_fp16(rmsO, kRmsElems);
  seed_f32(smallIn, kSmallTable, 0x700Fu);
  zero_f32(smallOut, kSmallVec);
  seed_f32(smallAux, kSmallVec, 0x7010u);
  seed_index_range(smallIdx, kSmallVec, static_cast<int>(kSmallVec), 0x7011u);
  zero_i32(argmaxOut, kSmallVec);
  seed_f32(segData, kSmallVec, 0x7012u);
  seed_index_range(segIds, kSmallVec, static_cast<int>(kSegments), 0x7013u);
  zero_f32(segOut, kSegments);
  for (usize i = 0; i < kUniqueN; ++i)
    uniqueIn[i] = static_cast<int>((i * 7u) % 23u);
  zero_i32(uniqueOut, kUniqueN);
  uniqueCount[0] = 0;
  emit_stage("seed_done");

  emit_stage("tload_store");
  tload_store_i32(iX, iY);
  emit_digest("tload_store", fnv1a_bytes(iY, sizeof(iY)));

  emit_stage("mamulb");
  mamulb_i32(iA, iB, iC);
  emit_digest("mamulb", fnv1a_bytes(iC, sizeof(iC)));

  zero_i32(iC, kMatElems);
  emit_stage("tmatmul_acc");
  tmatmul_acc_i32(iA, iB, iC);
  emit_digest("tmatmul_acc", fnv1a_bytes(iC, sizeof(iC)));

  zero_i32(iC, kMatElems);
  emit_stage("gemm");
  gemm_i32(iA, iB, iC);
  emit_digest("gemm", fnv1a_bytes(iC, sizeof(iC)));

  zero_f32(fC, kMatElems);
  emit_stage("gemm_basic");
  gemm_basic_f32(fA, fB, fC);
  emit_digest("gemm_basic", fnv1a_bytes(fC, sizeof(fC)));

  zero_f32(fC, kMatElems);
  emit_stage("gemm_demo");
  gemm_demo_f32(fC, fA, fB);
  emit_digest("gemm_demo", fnv1a_bytes(fC, sizeof(fC)));

  zero_f32(fC, kMatElems);
  emit_stage("gemm_performance");
  gemm_performance_f32(fA, fB, fC, PTO_QEMU_SMOKE ? 1 : 2);
  emit_digest("gemm_performance", fnv1a_bytes(fC, sizeof(fC)));

  emit_stage("pre_add_zero");
  zero_f32(fZ, kVecElems);
  emit_stage("add_custom");
  add_custom_f32(fX, fY, fZ);
  emit_digest("add_custom", fnv1a_bytes(fZ, sizeof(fZ)));

  emit_stage("pre_flash_attention");
  emit_stage("flash_attention");
  flash_attention_i32(flashQ, flashK, flashV, flashO);
  emit_digest("flash_attention", fnv1a_bytes(flashO, sizeof(flashO)));

  emit_stage("flash_attention_demo");
  flash_attention_demo_f32(flashOf, flashQf, flashKf, flashVf);
  emit_digest("flash_attention_demo", fnv1a_bytes(flashOf, sizeof(flashOf)));

  emit_stage("flash_attention_masked");
  flash_attention_masked_f32(flashMaskO, flashMaskQ, flashMaskK, flashMaskV);
  emit_digest("flash_attention_masked", fnv1a_bytes(flashMaskO, sizeof(flashMaskO)));

  zero_f32(flashOf, kFlashF32O);
  emit_stage("fa_performance");
  fa_performance_f32(flashOf, flashQf, flashKf, flashVf, PTO_QEMU_SMOKE ? 1 : 2);
  emit_digest("fa_performance", fnv1a_bytes(flashOf, sizeof(flashOf)));

  emit_stage("mla_attention_demo");
  mla_attention_demo_f32(mlaO, mlaQ, mlaK, mlaV, mlaWq, mlaWk, mlaWv, mlaWo);
  emit_digest("mla_attention_demo", fnv1a_bytes(mlaO, sizeof(mlaO)));

  emit_stage("flash_attention_cube_fp16");
  flash_attention_cube_f16(flashCubeO, flashCubeQ, flashCubeK, flashCubeV);
  emit_digest("flash_attention_cube_fp16",
              fnv1a_bytes(flashCubeO, sizeof(flashCubeO)));

  zero_f32(flashOf, kFlashF32O);
  emit_stage("flash_attention_vec_fp32");
  flash_attention_vec_f32(flashOf, flashQf, flashKf, flashVf);
  emit_digest("flash_attention_vec_fp32",
              fnv1a_bytes(flashOf, sizeof(flashOf)));

  emit_stage("flash_attention_vec_fp16");
  flash_attention_vec_f16(flashVecO, flashVecQ, flashVecK, flashVecV);
  emit_digest("flash_attention_vec_fp16",
              fnv1a_bytes(flashVecO, sizeof(flashVecO)));

  emit_stage("gqa_fp16");
  gqa_f16(gqaO, gqaQ, gqaK, gqaV);
  emit_digest("gqa_fp16", fnv1a_bytes(gqaO, sizeof(gqaO)));

  emit_stage("sparse_attention_local_fp16");
  sparse_attention_local_f16(sparseO, sparseQ, sparseK, sparseV,
                             PTO_QEMU_SMOKE ? 4 : 32);
  emit_digest("sparse_attention_local_fp16",
              fnv1a_bytes(sparseO, sizeof(sparseO)));

  emit_stage("rmsnorm_fp16");
  rmsnorm_f16(rmsO, rmsX, rmsGamma, 1e-5f);
  emit_digest("rmsnorm_fp16", fnv1a_bytes(rmsO, sizeof(rmsO)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("gelu_fp32");
  gelu_f32(smallOut, smallAux, kGeluN);
  emit_digest("gelu_fp32",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kGeluN) * sizeof(float)));

  zero_i32(argmaxOut, kSmallVec);
  emit_stage("argmax_fp32");
  argmax_f32(argmaxOut, smallIn, kArgmaxRows, kArgmaxCols);
  emit_digest("argmax_fp32",
              fnv1a_bytes(argmaxOut,
                          static_cast<usize>(kArgmaxRows) * sizeof(int)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("gather_fp32");
  gather_f32(smallOut, smallIn, smallIdx, static_cast<int>(kSmallVec));
  emit_digest("gather_fp32", fnv1a_bytes(smallOut, sizeof(smallOut)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("concat_fp32");
  concat_f32(smallOut, smallIn, smallAux, static_cast<int>(kSmallVec / 2u),
             static_cast<int>(kSmallVec / 2u));
  emit_digest("concat_fp32", fnv1a_bytes(smallOut, sizeof(smallOut)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("scatter_fp32");
  scatter_f32(smallOut, smallAux, smallIdx, smallIn, static_cast<int>(kSmallVec));
  emit_digest("scatter_fp32", fnv1a_bytes(smallOut, sizeof(smallOut)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("permute_nhwc_nchw_fp32");
  permute_nhwc_nchw_f32(smallOut, smallIn, kPermuteN, kPermuteH, kPermuteW,
                        kPermuteC);
  emit_digest("permute_nhwc_nchw_fp32",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kPermuteN * kPermuteH * kPermuteW *
                                             kPermuteC) *
                              sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("transpose_large_fp32");
  transpose_large_f32(smallOut, smallIn, kTransposeRows, kTransposeCols);
  emit_digest("transpose_large_fp32",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kTransposeRows * kTransposeCols) *
                              sizeof(float)));

  zero_f32(segOut, kSegments);
  emit_stage("unsorted_segment_sum_fp32");
  unsorted_segment_sum_f32(segOut, segIds, segData, static_cast<int>(kSmallVec),
                           static_cast<int>(kSegments));
  emit_digest("unsorted_segment_sum_fp32",
              fnv1a_bytes(segOut, sizeof(segOut)));

  zero_i32(uniqueOut, kUniqueN);
  uniqueCount[0] = 0;
  emit_stage("unique_i32");
  unique_i32(uniqueOut, uniqueCount, uniqueIn, static_cast<int>(kUniqueN));
  emit_digest("unique_i32",
              fnv1a_bytes(uniqueOut, sizeof(uniqueOut)) ^
                  fnv1a_bytes(uniqueCount, sizeof(uniqueCount)));
  emit_stage("done");
}

} // namespace

#if defined(PTO_HOST_SIM)
int main() {
  run_all_kernels_emit_digest();
  return 0;
}
#else
extern "C" void run_pto_parity_tests(void) {
  test_suite_begin(0x00000010);
  test_start(0x00100001);
  uart_puts("PTO kernel parity digest emission ... ");
  run_all_kernels_emit_digest();
  test_pass();
}
#endif
