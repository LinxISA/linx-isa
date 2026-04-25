#include <stdint.h>
#include <common/linx_lowp_types.hpp>
#include <common/runtime/kernel_api.hpp>

#if defined(PTO_HOST_SIM)
#include <stdio.h>
#else
#include "linx_test.h"
#endif

using usize = __SIZE_TYPE__;
using pto::float_to_fp16;
using pto::fp16_t;

#ifndef PTO_QEMU_SMOKE
#define PTO_QEMU_SMOKE 0
#endif

#if __has_include("pto_parity_shape_config.generated.hpp")
#include "pto_parity_shape_config.generated.hpp"
#endif

#ifndef PTO_PARITY_GELU_N
#define PTO_PARITY_GELU_N 256
#endif
#ifndef PTO_PARITY_FLASH_CUBE_SEQ
#define PTO_PARITY_FLASH_CUBE_SEQ 16
#endif
#ifndef PTO_PARITY_FLASH_CUBE_MAX_SEQ
#define PTO_PARITY_FLASH_CUBE_MAX_SEQ 64
#endif
#ifndef PTO_PARITY_FLASH_CUBE_DIM
#define PTO_PARITY_FLASH_CUBE_DIM 16
#endif
#ifndef PTO_PARITY_GQA_SEQ
#define PTO_PARITY_GQA_SEQ 16
#endif
#ifndef PTO_PARITY_GQA_Q_HEADS
#define PTO_PARITY_GQA_Q_HEADS 4
#endif
#ifndef PTO_PARITY_GQA_KV_HEADS
#define PTO_PARITY_GQA_KV_HEADS 1
#endif
#ifndef PTO_PARITY_GQA_DIM
#define PTO_PARITY_GQA_DIM 16
#endif
#ifndef PTO_PARITY_SPARSE_SEQ
#define PTO_PARITY_SPARSE_SEQ 16
#endif
#ifndef PTO_PARITY_SPARSE_HEADS
#define PTO_PARITY_SPARSE_HEADS 4
#endif
#ifndef PTO_PARITY_SPARSE_DIM
#define PTO_PARITY_SPARSE_DIM 16
#endif
#ifndef PTO_PARITY_SPARSE_WINDOW
#define PTO_PARITY_SPARSE_WINDOW 16
#endif
#ifndef PTO_PARITY_RMS_TOKENS
#define PTO_PARITY_RMS_TOKENS 16
#endif
#ifndef PTO_PARITY_RMS_CHANNELS
#define PTO_PARITY_RMS_CHANNELS 16
#endif
#ifndef PTO_PARITY_RMS_EPS
#define PTO_PARITY_RMS_EPS 1.0e-5f
#endif
#ifndef PTO_PARITY_ARGMAX_ROWS
#define PTO_PARITY_ARGMAX_ROWS 14
#endif
#ifndef PTO_PARITY_ARGMAX_COLS
#define PTO_PARITY_ARGMAX_COLS 14
#endif
#ifndef PTO_PARITY_GATHER_N
#define PTO_PARITY_GATHER_N 64
#endif
#ifndef PTO_PARITY_GATHER_TABLE
#define PTO_PARITY_GATHER_TABLE 97
#endif
#ifndef PTO_PARITY_CONCAT_NA
#define PTO_PARITY_CONCAT_NA 128
#endif
#ifndef PTO_PARITY_CONCAT_NB
#define PTO_PARITY_CONCAT_NB 128
#endif
#ifndef PTO_PARITY_SCATTER_N
#define PTO_PARITY_SCATTER_N 128
#endif
#ifndef PTO_PARITY_PERMUTE_N
#define PTO_PARITY_PERMUTE_N 1
#endif
#ifndef PTO_PARITY_PERMUTE_H
#define PTO_PARITY_PERMUTE_H 8
#endif
#ifndef PTO_PARITY_PERMUTE_W
#define PTO_PARITY_PERMUTE_W 8
#endif
#ifndef PTO_PARITY_PERMUTE_C
#define PTO_PARITY_PERMUTE_C 8
#endif
#ifndef PTO_PARITY_TRANSPOSE_ROWS
#define PTO_PARITY_TRANSPOSE_ROWS 16
#endif
#ifndef PTO_PARITY_TRANSPOSE_COLS
#define PTO_PARITY_TRANSPOSE_COLS 3
#endif
#ifndef PTO_PARITY_UNSORTED_SEGMENTS
#define PTO_PARITY_UNSORTED_SEGMENTS 152
#endif
#ifndef PTO_PARITY_UNSORTED_N
#define PTO_PARITY_UNSORTED_N 256
#endif
#ifndef PTO_PARITY_UNIQUE_N
#define PTO_PARITY_UNIQUE_N 256
#endif

namespace {

using namespace pto::kernels;

constexpr usize max_usize(usize a, usize b) { return a > b ? a : b; }

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
  const pto_memory_config mem_i32_cfg{
      pto_dtype::i32, static_cast<int>(PTO_QEMU_SMOKE ? 32u * 32u : 1024u * 1024u),
      PTO_QEMU_SMOKE ? 32 : 1024, PTO_QEMU_SMOKE ? 32 : 1024,
      presets::kNoTiling};
  const pto_matmul_config matmul_i32_cfg{
      pto_dtype::i32, pto_dtype::i32, pto_dtype::i32, pto_dtype::i32,
      PTO_QEMU_SMOKE ? 16 : 256, PTO_QEMU_SMOKE ? 16 : 256,
      PTO_QEMU_SMOKE ? 16 : 256, 1, presets::kGemmParityTiling};
  const pto_matmul_config matmul_f32_cfg{
      pto_dtype::f32, pto_dtype::f32, pto_dtype::f32, pto_dtype::f32,
      PTO_QEMU_SMOKE ? 16 : 256, PTO_QEMU_SMOKE ? 16 : 256,
      PTO_QEMU_SMOKE ? 16 : 256, 1, presets::kGemmParityTiling};
  const pto_matmul_config matmul_perf_cfg{
      pto_dtype::f32, pto_dtype::f32, pto_dtype::f32, pto_dtype::f32,
      PTO_QEMU_SMOKE ? 16 : 256, PTO_QEMU_SMOKE ? 16 : 256,
      PTO_QEMU_SMOKE ? 16 : 256, PTO_QEMU_SMOKE ? 1 : 2,
      presets::kGemmParityTiling};
  const pto_elementwise_config add_cfg{
      pto_dtype::f32, pto_dtype::f32, pto_dtype::f32, pto_dtype::f32,
      static_cast<int>(PTO_QEMU_SMOKE ? 32u * 32u : 1024u * 1024u), 0, 0, 0.0f, 0.0f};
  const pto_elementwise_config unary_cfg{
      pto_dtype::f32, pto_dtype::invalid, pto_dtype::f32, pto_dtype::f32,
      PTO_QEMU_SMOKE ? 64 : 256, 0, 0, 0.0f, 0.0f};
  const pto_elementwise_config softmax_cfg{
      pto_dtype::f32, pto_dtype::invalid, pto_dtype::f32, pto_dtype::f32,
      0, PTO_QEMU_SMOKE ? 8 : 32, PTO_QEMU_SMOKE ? 8 : 32, 0.0f, 0.0f};
  const pto_elementwise_config swiglu_cfg{
      pto_dtype::f32, pto_dtype::f32, pto_dtype::f32, pto_dtype::f32,
      PTO_QEMU_SMOKE ? 64 : 256, 0, 0, 0.0f, 0.0f};
  const pto_attention_config flash_cube_cfg{
      pto_dtype::f16, pto_dtype::f16, pto_dtype::f32, PTO_PARITY_FLASH_CUBE_SEQ,
      PTO_PARITY_FLASH_CUBE_DIM, PTO_PARITY_FLASH_CUBE_DIM, 1, 1,
      PTO_PARITY_FLASH_CUBE_MAX_SEQ, PTO_PARITY_FLASH_CUBE_MAX_SEQ,
      0, 0, 0, 0, 1, PTO_ATTN_FLAG_CAUSAL, presets::kFlashCubeParityTiling};
  const pto_attention_config flash_vec_f32_cfg{
      pto_dtype::f32, pto_dtype::f32, pto_dtype::f32, 16, 16, 16, 1, 1, 0, 0,
      0, 0, 0, 0, 1, 0u, presets::kFlashVecParityTiling};
  const pto_attention_config flash_vec_f16_cfg{
      pto_dtype::f16, pto_dtype::f16, pto_dtype::f32, 16, 16, 16, 1, 1, 0, 0,
      0, 0, 0, 0, 1, 0u, presets::kFlashVecParityTiling};
  const pto_attention_config gqa_cfg{
      pto_dtype::f16, pto_dtype::f16, pto_dtype::f32,
      PTO_PARITY_GQA_SEQ, PTO_PARITY_GQA_DIM, PTO_PARITY_GQA_DIM,
      PTO_PARITY_GQA_Q_HEADS, PTO_PARITY_GQA_KV_HEADS, 0, 0, 0, 0, 0, 0, 1, 0u,
      presets::kFlashCubeParityTiling};
  const pto_attention_config sparse_local_cfg{
      pto_dtype::f16, pto_dtype::f16, pto_dtype::f32,
      PTO_PARITY_SPARSE_SEQ, PTO_PARITY_SPARSE_DIM, PTO_PARITY_SPARSE_DIM,
      PTO_PARITY_SPARSE_HEADS, PTO_PARITY_SPARSE_HEADS, 0, 0,
      PTO_PARITY_SPARSE_WINDOW, 0, 0, 0, 1, 0u,
      pto_tiling_config{16, 0, 16, 1, 1, 1, 0}};
  const pto_normalization_config rms_cfg{
      pto_dtype::f16, pto_dtype::f16, pto_dtype::f16, pto_dtype::f32,
      PTO_PARITY_RMS_TOKENS, PTO_PARITY_RMS_CHANNELS, PTO_PARITY_RMS_EPS,
      presets::kRmsnormParityTiling};
  const pto_normalization_config batchnorm_cfg{
      pto_dtype::f32, pto_dtype::f32, pto_dtype::f32, pto_dtype::f32,
      PTO_QEMU_SMOKE ? 8 : 32, PTO_QEMU_SMOKE ? 8 : 16, 1.0e-5f,
      presets::kNoTiling};
  const pto_normalization_config layernorm_cfg{
      pto_dtype::f32, pto_dtype::f32, pto_dtype::f32, pto_dtype::f32,
      PTO_QEMU_SMOKE ? 8 : 32, PTO_QEMU_SMOKE ? 8 : 16, 1.0e-5f,
      presets::kNoTiling};
  const pto_elementwise_config gelu_cfg{
      pto_dtype::f32, pto_dtype::invalid, pto_dtype::f32, pto_dtype::f32,
      PTO_PARITY_GELU_N, 0, 0, 0.0f, 0.0f};
  const pto_indexing_config argmax_cfg{
      pto_dtype::f32, pto_dtype::invalid, pto_dtype::i32, pto_dtype::f32,
      0, PTO_PARITY_ARGMAX_ROWS, PTO_PARITY_ARGMAX_COLS, 0};
  const pto_indexing_config gather_cfg{
      pto_dtype::f32, pto_dtype::i32, pto_dtype::f32, pto_dtype::f32,
      PTO_PARITY_GATHER_N, 0, 0, 0};
  const pto_indexing_config where_cfg{
      pto_dtype::f32, pto_dtype::f32, pto_dtype::f32, pto_dtype::f32,
      PTO_QEMU_SMOKE ? 64 : 256, 0, 0, 0};
  const pto_indexing_config slice_cfg{
      pto_dtype::f32, pto_dtype::invalid, pto_dtype::f32, pto_dtype::f32,
      PTO_QEMU_SMOKE ? 32 : 128, 0, 0, 0, PTO_QEMU_SMOKE ? 5 : 17,
      PTO_QEMU_SMOKE ? 32 : 128, 0};
  const pto_layout_config concat_cfg{
      pto_dtype::f32, 0, 0, 0, 0, 0, 0,
      PTO_PARITY_CONCAT_NA, PTO_PARITY_CONCAT_NB};
  const pto_layout_config unary_layout_cfg{
      pto_dtype::f32, PTO_QEMU_SMOKE ? 64 : 256, 0, 0, 0, 0, 0, 0, 0};
  const pto_layout_config stack_cfg{
      pto_dtype::f32, static_cast<int>((PTO_QEMU_SMOKE ? 64u : 256u) / 2u), 0,
      0, 0, 0, 0,
      static_cast<int>((PTO_QEMU_SMOKE ? 64u : 256u) / 2u),
      static_cast<int>((PTO_QEMU_SMOKE ? 64u : 256u) / 2u)};
  const pto_layout_config split_cfg{
      pto_dtype::f32, 0, 0, 0, 0, 0, 0,
      static_cast<int>((PTO_QEMU_SMOKE ? 64u : 256u) / 2u),
      static_cast<int>((PTO_QEMU_SMOKE ? 64u : 256u) / 2u)};
  const pto_indexing_config scatter_cfg{
      pto_dtype::f32, pto_dtype::i32, pto_dtype::f32, pto_dtype::f32,
      PTO_PARITY_SCATTER_N, 0, 0, 0};
  const pto_layout_config permute_cfg{
      pto_dtype::f32, PTO_PARITY_PERMUTE_N, PTO_PARITY_PERMUTE_H,
      PTO_PARITY_PERMUTE_W, PTO_PARITY_PERMUTE_C, 0, 0, 0, 0};
  const pto_layout_config transpose_cfg{
      pto_dtype::f32, 0, 0, 0, 0, PTO_PARITY_TRANSPOSE_ROWS,
      PTO_PARITY_TRANSPOSE_COLS, 0, 0};
  const pto_indexing_config segment_cfg{
      pto_dtype::f32, pto_dtype::i32, pto_dtype::f32, pto_dtype::f32,
      PTO_PARITY_UNSORTED_N, 0, 0, PTO_PARITY_UNSORTED_SEGMENTS};
  const pto_indexing_config unique_cfg{
      pto_dtype::i32, pto_dtype::invalid, pto_dtype::i32, pto_dtype::i32,
      PTO_PARITY_UNIQUE_N, 0, 0, 0};
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
  constexpr usize kFlashCubeElems =
      static_cast<usize>(PTO_PARITY_FLASH_CUBE_SEQ) *
      static_cast<usize>(PTO_PARITY_FLASH_CUBE_DIM);
  constexpr usize kFlashVecElems = PTO_QEMU_SMOKE ? 16u * 16u : 128u * 16u;
  constexpr usize kGqaQElems =
      static_cast<usize>(PTO_PARITY_GQA_Q_HEADS) *
      static_cast<usize>(PTO_PARITY_GQA_SEQ) *
      static_cast<usize>(PTO_PARITY_GQA_DIM);
  constexpr usize kGqaKVElems =
      static_cast<usize>(PTO_PARITY_GQA_KV_HEADS) *
      static_cast<usize>(PTO_PARITY_GQA_SEQ) *
      static_cast<usize>(PTO_PARITY_GQA_DIM);
  constexpr usize kSparseElems =
      static_cast<usize>(PTO_PARITY_SPARSE_HEADS) *
      static_cast<usize>(PTO_PARITY_SPARSE_SEQ) *
      static_cast<usize>(PTO_PARITY_SPARSE_DIM);
  constexpr usize kRmsElems =
      static_cast<usize>(PTO_PARITY_RMS_TOKENS) *
      static_cast<usize>(PTO_PARITY_RMS_CHANNELS);
  constexpr usize kRmsGammaElems = static_cast<usize>(PTO_PARITY_RMS_CHANNELS);
  constexpr usize kSmallVec = PTO_QEMU_SMOKE ? 512u : 2048u;
  constexpr usize kSmallTable = PTO_QEMU_SMOKE ? 512u : 4096u;
  constexpr usize kSegments = static_cast<usize>(PTO_PARITY_UNSORTED_SEGMENTS);
  constexpr usize kUniqueN = static_cast<usize>(PTO_PARITY_UNIQUE_N);
  constexpr int kGeluN = PTO_PARITY_GELU_N;
  constexpr int kUnaryN = PTO_QEMU_SMOKE ? 64 : 256;
  constexpr int kSoftmaxRows = PTO_QEMU_SMOKE ? 8 : 32;
  constexpr int kSoftmaxCols = PTO_QEMU_SMOKE ? 8 : 32;
  constexpr int kNormTokens = PTO_QEMU_SMOKE ? 8 : 32;
  constexpr int kNormChannels = PTO_QEMU_SMOKE ? 8 : 16;
  constexpr int kSliceStart = PTO_QEMU_SMOKE ? 5 : 17;
  constexpr int kSliceLen = PTO_QEMU_SMOKE ? 32 : 128;
  constexpr int kStackN = PTO_QEMU_SMOKE ? 32 : 128;
  constexpr usize kNormElems =
      static_cast<usize>(kNormTokens) * static_cast<usize>(kNormChannels);
  constexpr int kArgmaxRows = PTO_PARITY_ARGMAX_ROWS;
  constexpr int kArgmaxCols = PTO_PARITY_ARGMAX_COLS;
  constexpr int kPermuteN = PTO_PARITY_PERMUTE_N;
  constexpr int kPermuteH = PTO_PARITY_PERMUTE_H;
  constexpr int kPermuteW = PTO_PARITY_PERMUTE_W;
  constexpr int kPermuteC = PTO_PARITY_PERMUTE_C;
  constexpr int kTransposeRows = PTO_PARITY_TRANSPOSE_ROWS;
  constexpr int kTransposeCols = PTO_PARITY_TRANSPOSE_COLS;

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
  alignas(64) static fp16_t flashCubeQ[kFlashCubeElems];
  alignas(64) static fp16_t flashCubeK[kFlashCubeElems];
  alignas(64) static fp16_t flashCubeV[kFlashCubeElems];
  alignas(64) static fp16_t flashCubeO[kFlashCubeElems];
  alignas(64) static fp16_t flashVecQ[kFlashVecElems];
  alignas(64) static fp16_t flashVecK[kFlashVecElems];
  alignas(64) static fp16_t flashVecV[kFlashVecElems];
  alignas(64) static fp16_t flashVecO[kFlashVecElems];
  alignas(64) static fp16_t gqaQ[kGqaQElems];
  alignas(64) static fp16_t gqaK[kGqaKVElems];
  alignas(64) static fp16_t gqaV[kGqaKVElems];
  alignas(64) static fp16_t gqaO[kGqaQElems];
  alignas(64) static fp16_t sparseQ[kSparseElems];
  alignas(64) static fp16_t sparseK[kSparseElems];
  alignas(64) static fp16_t sparseV[kSparseElems];
  alignas(64) static fp16_t sparseO[kSparseElems];
  alignas(64) static fp16_t rmsX[kRmsElems];
  alignas(64) static fp16_t rmsGamma[kRmsGammaElems];
  alignas(64) static fp16_t rmsO[kRmsElems];
  alignas(64) static float smallIn[kSmallTable];
  alignas(64) static float smallOut[kSmallVec];
  alignas(64) static float smallAux[kSmallVec];
  alignas(64) static float smallOutB[kSmallVec];
  alignas(64) static int smallIdx[kSmallVec];
  alignas(64) static int argmaxOut[kSmallVec];
  alignas(64) static float segData[kSmallVec];
  alignas(64) static int segIds[kSmallVec];
  alignas(64) static float segOut[kSegments];
  alignas(64) static float normIn[kNormElems];
  alignas(64) static float normOut[kNormElems];
  alignas(64) static float normMean[kNormChannels];
  alignas(64) static float normVar[kNormChannels];
  alignas(64) static float normGamma[kNormChannels];
  alignas(64) static float normBeta[kNormChannels];
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
  seed_fp16(flashCubeQ, kFlashCubeElems, 0x7001u);
  seed_fp16(flashCubeK, kFlashCubeElems, 0x7002u);
  seed_fp16(flashCubeV, kFlashCubeElems, 0x7003u);
  zero_fp16(flashCubeO, kFlashCubeElems);
  seed_fp16(flashVecQ, kFlashVecElems, 0x7004u);
  seed_fp16(flashVecK, kFlashVecElems, 0x7005u);
  seed_fp16(flashVecV, kFlashVecElems, 0x7006u);
  zero_fp16(flashVecO, kFlashVecElems);
  seed_fp16(gqaQ, kGqaQElems, 0x7007u);
  seed_fp16(gqaK, kGqaKVElems, 0x7008u);
  seed_fp16(gqaV, kGqaKVElems, 0x7009u);
  zero_fp16(gqaO, kGqaQElems);
  seed_fp16(sparseQ, kSparseElems, 0x700Au);
  seed_fp16(sparseK, kSparseElems, 0x700Bu);
  seed_fp16(sparseV, kSparseElems, 0x700Cu);
  zero_fp16(sparseO, kSparseElems);
  seed_fp16(rmsX, kRmsElems, 0x700Du);
  seed_fp16(rmsGamma, kRmsGammaElems, 0x700Eu);
  zero_fp16(rmsO, kRmsElems);
  seed_f32(smallIn, kSmallTable, 0x700Fu);
  zero_f32(smallOut, kSmallVec);
  seed_f32(smallAux, kSmallVec, 0x7010u);
  zero_f32(smallOutB, kSmallVec);
  seed_index_range(smallIdx, kSmallVec, static_cast<int>(kSmallVec), 0x7011u);
  zero_i32(argmaxOut, kSmallVec);
  seed_f32(segData, kSmallVec, 0x7012u);
  seed_index_range(segIds, kSmallVec, static_cast<int>(kSegments), 0x7013u);
  zero_f32(segOut, kSegments);
  seed_f32(normIn, kNormElems, 0x7014u);
  zero_f32(normOut, kNormElems);
  seed_f32(normMean, kNormChannels, 0x7015u);
  seed_f32(normVar, kNormChannels, 0x7016u);
  seed_f32(normGamma, kNormChannels, 0x7017u);
  seed_f32(normBeta, kNormChannels, 0x7018u);
  for (int i = 0; i < kNormChannels; ++i)
    normVar[i] = normVar[i] * normVar[i] + 0.25f;
  for (usize i = 0; i < kUniqueN; ++i)
    uniqueIn[i] = static_cast<int>((i * 7u) % 23u);
  zero_i32(uniqueOut, kUniqueN);
  uniqueCount[0] = 0;
  emit_stage("seed_done");

  emit_stage("tload_store");
  pto_tload_store(iY, iX, &mem_i32_cfg);
  emit_digest("tload_store", fnv1a_bytes(iY, sizeof(iY)));

  emit_stage("mamulb");
  pto_mamulb(iC, iA, iB, &matmul_i32_cfg);
  emit_digest("mamulb", fnv1a_bytes(iC, sizeof(iC)));

  zero_i32(iC, kMatElems);
  emit_stage("tmatmul_acc");
  pto_tmatmul_acc(iC, iA, iB, &matmul_i32_cfg);
  emit_digest("tmatmul_acc", fnv1a_bytes(iC, sizeof(iC)));

  zero_i32(iC, kMatElems);
  emit_stage("gemm");
  pto_gemm(iC, iA, iB, &matmul_i32_cfg);
  emit_digest("gemm", fnv1a_bytes(iC, sizeof(iC)));

  zero_f32(fC, kMatElems);
  emit_stage("gemm_basic");
  pto_gemm_basic(fC, fA, fB, &matmul_f32_cfg);
  emit_digest("gemm_basic", fnv1a_bytes(fC, sizeof(fC)));

  zero_f32(fC, kMatElems);
  emit_stage("gemm_scaled");
  pto_gemm_scaled(fC, fA, fB, &matmul_f32_cfg);
  emit_digest("gemm_scaled", fnv1a_bytes(fC, sizeof(fC)));

  zero_f32(fC, kMatElems);
  emit_stage("gemm_performance");
  pto_gemm_performance(fC, fA, fB, &matmul_perf_cfg);
  emit_digest("gemm_performance", fnv1a_bytes(fC, sizeof(fC)));

  emit_stage("pre_add_zero");
  zero_f32(fZ, kVecElems);
  emit_stage("add_custom");
  pto_add_custom(fZ, fX, fY, &add_cfg);
  emit_digest("add_custom", fnv1a_bytes(fZ, sizeof(fZ)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("relu");
  pto_relu(smallOut, smallAux, &unary_cfg);
  emit_digest("relu",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kUnaryN) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("sigmoid");
  pto_sigmoid(smallOut, smallAux, &unary_cfg);
  emit_digest("sigmoid",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kUnaryN) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("silu");
  pto_silu(smallOut, smallAux, &unary_cfg);
  emit_digest("silu",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kUnaryN) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("tanh");
  pto_tanh(smallOut, smallAux, &unary_cfg);
  emit_digest("tanh",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kUnaryN) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("softmax");
  pto_softmax(smallOut, smallIn, &softmax_cfg);
  emit_digest("softmax",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kSoftmaxRows * kSoftmaxCols) *
                              sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("swiglu");
  pto_swiglu(smallOut, smallIn, smallAux, &swiglu_cfg);
  emit_digest("swiglu",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kUnaryN) * sizeof(float)));

  emit_stage("pre_flash_attention");
  emit_stage("flash_attention");
  pto_flash_attention(flashO, flashQ, flashK, flashV, nullptr);
  emit_digest("flash_attention", fnv1a_bytes(flashO, sizeof(flashO)));

  emit_stage("flash_attention_softmax");
  pto_flash_attention_softmax(flashOf, flashQf, flashKf, flashVf, nullptr);
  emit_digest("flash_attention_softmax", fnv1a_bytes(flashOf, sizeof(flashOf)));

  emit_stage("flash_attention_masked");
  pto_flash_attention_masked(flashMaskO, flashMaskQ, flashMaskK, flashMaskV,
                             nullptr);
  emit_digest("flash_attention_masked", fnv1a_bytes(flashMaskO, sizeof(flashMaskO)));

  zero_f32(flashOf, kFlashF32O);
  emit_stage("fa_performance");
  pto_attention_config flash_perf_cfg{
      pto_dtype::f32, pto_dtype::f32, pto_dtype::f32, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, PTO_QEMU_SMOKE ? 1 : 2, 0u, presets::kNoTiling, 0.0f, 0u};
  pto_fa_performance(flashOf, flashQf, flashKf, flashVf, &flash_perf_cfg);
  emit_digest("fa_performance", fnv1a_bytes(flashOf, sizeof(flashOf)));

  emit_stage("mla_attention");
  pto_mla_attention(mlaO, mlaQ, mlaK, mlaV, mlaWq, mlaWk, mlaWv, mlaWo, nullptr);
  emit_digest("mla_attention", fnv1a_bytes(mlaO, sizeof(mlaO)));

  emit_stage("flash_attention_cube");
  pto_flash_attention_cube(flashCubeO, flashCubeQ, flashCubeK, flashCubeV,
                           &flash_cube_cfg);
  emit_digest("flash_attention_cube",
              fnv1a_bytes(flashCubeO, sizeof(flashCubeO)));

  zero_f32(flashOf, kFlashF32O);
  emit_stage("flash_attention_vec");
  pto_flash_attention_vec(flashOf, flashQf, flashKf, flashVf,
                          &flash_vec_f32_cfg);
  pto_flash_attention_vec(flashVecO, flashVecQ, flashVecK, flashVecV,
                          &flash_vec_f16_cfg);
  emit_digest("flash_attention_vec",
              fnv1a_bytes(flashOf, sizeof(flashOf)) ^
                  fnv1a_bytes(flashVecO, sizeof(flashVecO)));

  emit_stage("gqa");
  pto_gqa(gqaO, gqaQ, gqaK, gqaV, &gqa_cfg);
  emit_digest("gqa", fnv1a_bytes(gqaO, sizeof(gqaO)));

  emit_stage("sparse_attention_local");
  pto_sparse_attention_local(sparseO, sparseQ, sparseK, sparseV,
                             &sparse_local_cfg);
  emit_digest("sparse_attention_local",
              fnv1a_bytes(sparseO, sizeof(sparseO)));

  emit_stage("rmsnorm");
  pto_rmsnorm(rmsO, rmsX, rmsGamma, &rms_cfg);
  emit_digest("rmsnorm", fnv1a_bytes(rmsO, sizeof(rmsO)));

  zero_f32(normOut, kNormElems);
  emit_stage("batchnorm");
  pto_batchnorm(normOut, normIn, normMean, normVar, normGamma, normBeta,
                &batchnorm_cfg);
  emit_digest("batchnorm",
              fnv1a_bytes(normOut,
                          static_cast<usize>(kNormElems) * sizeof(float)));

  zero_f32(normOut, kNormElems);
  emit_stage("layernorm");
  pto_layernorm(normOut, normIn, normGamma, normBeta, &layernorm_cfg);
  emit_digest("layernorm",
              fnv1a_bytes(normOut,
                          static_cast<usize>(kNormElems) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("gelu");
  pto_gelu(smallOut, smallAux, &gelu_cfg);
  emit_digest("gelu",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kGeluN) * sizeof(float)));

  zero_i32(argmaxOut, kSmallVec);
  emit_stage("argmax");
  pto_argmax(argmaxOut, smallIn, &argmax_cfg);
  emit_digest("argmax",
              fnv1a_bytes(argmaxOut,
                          static_cast<usize>(kArgmaxRows) * sizeof(int)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("gather");
  pto_gather(smallOut, smallIn, smallIdx, &gather_cfg);
  emit_digest("gather",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(gather_cfg.n) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("where");
  pto_where(smallOut, smallAux, smallIn, fX, &where_cfg);
  emit_digest("where",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(where_cfg.n) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("slice");
  pto_slice(smallOut, smallIn, &slice_cfg);
  emit_digest("slice",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kSliceLen) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("concat");
  pto_concat(smallOut, smallIn, smallAux, &concat_cfg);
  emit_digest("concat",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(concat_cfg.n_a + concat_cfg.n_b) *
                              sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("flatten");
  pto_flatten(smallOut, smallIn, &unary_layout_cfg);
  emit_digest("flatten",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(unary_layout_cfg.n) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("reshape");
  pto_reshape(smallOut, smallIn, &unary_layout_cfg);
  emit_digest("reshape",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(unary_layout_cfg.n) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("scatter");
  pto_scatter(smallOut, smallAux, smallIdx, smallIn, &scatter_cfg);
  emit_digest("scatter",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(scatter_cfg.n) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("squeeze");
  pto_squeeze(smallOut, smallIn, &unary_layout_cfg);
  emit_digest("squeeze",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(unary_layout_cfg.n) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("unsqueeze");
  pto_unsqueeze(smallOut, smallIn, &unary_layout_cfg);
  emit_digest("unsqueeze",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(unary_layout_cfg.n) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("stack");
  pto_stack(smallOut, smallIn, smallAux, &stack_cfg);
  emit_digest("stack",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kStackN * 2) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  zero_f32(smallOutB, kSmallVec);
  emit_stage("split");
  pto_split(smallOut, smallOutB, smallIn, &split_cfg);
  emit_digest("split",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(split_cfg.n_a) * sizeof(float)) ^
                  fnv1a_bytes(smallOutB,
                              static_cast<usize>(split_cfg.n_b) * sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("permute_nhwc_nchw");
  pto_permute_nhwc_nchw(smallOut, smallIn, &permute_cfg);
  emit_digest("permute_nhwc_nchw",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kPermuteN * kPermuteH * kPermuteW *
                                             kPermuteC) *
                              sizeof(float)));

  zero_f32(smallOut, kSmallVec);
  emit_stage("transpose");
  pto_transpose(smallOut, smallIn, &transpose_cfg);
  emit_digest("transpose",
              fnv1a_bytes(smallOut,
                          static_cast<usize>(kTransposeRows * kTransposeCols) *
                              sizeof(float)));

  zero_f32(segOut, kSegments);
  emit_stage("unsorted_segment_sum");
  pto_unsorted_segment_sum(segOut, segIds, segData, &segment_cfg);
  emit_digest("unsorted_segment_sum",
              fnv1a_bytes(segOut,
                          static_cast<usize>(segment_cfg.num_segments) *
                              sizeof(float)));

  zero_i32(uniqueOut, kUniqueN);
  uniqueCount[0] = 0;
  emit_stage("unique");
  pto_unique(uniqueOut, uniqueCount, uniqueIn, &unique_cfg);
  emit_digest("unique",
              fnv1a_bytes(uniqueOut,
                          static_cast<usize>(unique_cfg.n) * sizeof(int)) ^
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
