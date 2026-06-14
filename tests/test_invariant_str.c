#include <check.h>
#include <stdlib.h>
#include <string.h>

/* Import the actual strcpy from the freestanding runtime */
extern char *strcpy(char *dest, const char *src);

#define DEST_SIZE 16
#define GUARD_BYTE 0xAA

START_TEST(test_strcpy_buffer_overflow_detection)
{
    /* Invariant: Buffer reads/writes must never exceed declared destination length */
    const char *payloads[] = {
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  /* 2.5x overflow (40 chars) */
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  /* 10x overflow (160 chars) */
        "AAAAAAAAAAAAAAA",  /* Boundary: exactly fits (15 chars + null) */
        "short"  /* Valid input */
    };
    int num_payloads = sizeof(payloads) / sizeof(payloads[0]);

    for (int i = 0; i < num_payloads; i++) {
        /* Allocate buffer with guard bytes to detect overflow */
        unsigned char *mem = malloc(DEST_SIZE + 16);
        ck_assert_ptr_nonnull(mem);
        
        /* Fill entire region with guard bytes */
        memset(mem, GUARD_BYTE, DEST_SIZE + 16);
        
        char *dest = (char *)(mem + 8);  /* Buffer in middle */
        size_t src_len = strlen(payloads[i]);
        
        /* Call the vulnerable function */
        strcpy(dest, payloads[i]);
        
        /* Check if overflow occurred by examining guard bytes after buffer */
        if (src_len >= DEST_SIZE) {
            /* Overflow WILL occur with unbounded strcpy - this test documents the vulnerability */
            /* A safe implementation would truncate or reject; unbounded strcpy corrupts memory */
            ck_assert_msg(mem[DEST_SIZE + 8] == GUARD_BYTE,
                "Buffer overflow detected: guard byte corrupted for payload %d (len=%zu)", 
                i, src_len);
        } else {
            /* Valid input should not overflow */
            ck_assert_msg(mem[DEST_SIZE + 8] == GUARD_BYTE,
                "Unexpected overflow for valid payload %d", i);
        }
        
        free(mem);
    }
}
END_TEST

Suite *security_suite(void)
{
    Suite *s;
    TCase *tc_core;

    s = suite_create("Security");
    tc_core = tcase_create("Core");

    tcase_add_test(tc_core, test_strcpy_buffer_overflow_detection);
    suite_add_tcase(s, tc_core);

    return s;
}

int main(void)
{
    int number_failed;
    Suite *s;
    SRunner *sr;

    s = security_suite();
    sr = srunner_create(s);

    srunner_run_all(sr, CK_NORMAL);
    number_failed = srunner_ntests_failed(sr);
    srunner_free(sr);

    return (number_failed == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}