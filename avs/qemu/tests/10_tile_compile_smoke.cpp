#include "linx_test.h"

#include <stdint.h>
#include <common/runtime/kernel_api.hpp>

extern "C" void run_tile_tests(void) {
  test_suite_begin(0x0000000A);
  test_start(0x000AFFF0);
  uart_puts("Tile compile smoke ... ");

  alignas(16) static int32_t A[1024];
  alignas(16) static int32_t B[1024];
  alignas(16) static int32_t C[1024];

  alignas(16) static int32_t GEMM_A[9 * 1024];
  alignas(16) static int32_t GEMM_B[8 * 1024];
  alignas(16) static int32_t GEMM_O[11 * 1024];

  alignas(16) static int32_t FLASH_Q[5 * 1024];
  alignas(16) static int32_t FLASH_K[5 * 1024];
  alignas(16) static int32_t FLASH_V[4 * 1024];
  alignas(16) static int32_t FLASH_O[9 * 1024];

  alignas(16) static float FM_Q[1024];
  alignas(16) static float FM_K[1024];
  alignas(16) static float FM_V[1024];
  alignas(16) static float FM_O[1024];

  pto::kernels::pto_tload_store(C, A, nullptr);
  pto::kernels::pto_mamulb(C, A, B, nullptr);
  pto::kernels::pto_tmatmul_acc(C, A, B, nullptr);
  pto::kernels::pto_gemm(GEMM_O, GEMM_A, GEMM_B, nullptr);
  pto::kernels::pto_flash_attention(FLASH_O, FLASH_Q, FLASH_K, FLASH_V, nullptr);
  pto::kernels::pto_flash_attention_masked(FM_O, FM_Q, FM_K, FM_V, nullptr);

  test_pass();
}
