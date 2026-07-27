#include "linx_test.h"

extern "C" {
void run_tile_tma_tests(void);
void run_tile_cube_tests(void);
void run_tile_tepl_tests(void);
void run_tile_tepl_reject_tests(void);
void run_tile_integration_tests(void);
}

extern "C" void run_tile_tests(void)
{
    test_suite_begin(0x0000000A);
    run_tile_cube_tests();
    run_tile_tepl_tests();
    run_tile_tepl_reject_tests();
    run_tile_integration_tests();
    // The TMA ordering smoke intentionally runs last because it leaves a
    // long-lived Tile source while checking scalar/TMA store ordering.
    run_tile_tma_tests();
}
