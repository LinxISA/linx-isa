#include "linx_test.h"

extern "C" {
void run_tile_tlsu_tests(void);
void run_tile_cube_tests(void);
void run_tile_vec_sfu_tests(void);
void run_tile_sfu_reject_tests(void);
void run_tile_integration_tests(void);
}

extern "C" void run_tile_tests(void)
{
    test_suite_begin(0x0000000A);
    run_tile_cube_tests();
    run_tile_vec_sfu_tests();
    run_tile_sfu_reject_tests();
    run_tile_integration_tests();
    // The TLSU ordering smoke intentionally runs last because it leaves a
    // long-lived Tile source while checking scalar/TLSU store ordering.
    run_tile_tlsu_tests();
}
