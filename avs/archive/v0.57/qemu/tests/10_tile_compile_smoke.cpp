#include "linx_test.h"

#include <stdint.h>
#include <common/runtime/kernel_api.hpp>

extern "C" void run_tile_tests(void) {
  test_suite_begin(0x0000000A);
  test_start(0x000AFFF0);
  uart_puts("Tile compile smoke ... ");

  alignas(16) static int32_t A[16];
  alignas(16) static int32_t C[16];

  pto::kernels::pto_tload_store(C, A, nullptr);

  test_pass();
}
