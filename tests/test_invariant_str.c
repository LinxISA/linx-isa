#include <check.h>
#include <stdlib.h>
#include <string.h>

/*
 * Test the security invariant: buffer writes must never exceed the declared
 * destination length.  We exercise strlcpy(), the bounds-checked replacement
 * for the unsafe strcpy(), and verify it never touches memory outside the
 * declared destination buffer even when the source is many times larger.
 *
 * A second test documents the vulnerability in strcpy(): it DOES overflow
 * and corrupts the guard byte, confirming the fix (strlcpy) is necessary.
 */
extern size_t strlcpy(char *dest, const char *src, size_t size);

#define DEST_SIZE  16
#define GUARD_BYTE 0xAA

START_TEST(test_strlcpy_no_buffer_overflow)
{
    /* Invariant: strlcpy() must never write past dest[0..DEST_SIZE-1]. */
    const char *payloads[] = {
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  /* 2.5x overflow (40 chars)  */
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  /* 10x overflow (160 chars) */
        "AAAAAAAAAAAAAAA",  /* Boundary: exactly fills buffer (15 chars + NUL)    */
        "short"             /* Valid input well within the buffer                 */
    };
    int num_payloads = sizeof(payloads) / sizeof(payloads[0]);

    for (int i = 0; i < num_payloads; i++) {
        /*
         * Lay out memory as:  [ 8-byte pre-guard | DEST_SIZE bytes dest | post-guard ]
         *
         * Allocate enough space to hold the full source payload so that
         * strlcpy() itself never causes heap corruption — the bounds check
         * (DEST_SIZE argument) is what we are testing, not malloc().
         *
         * alloc_size = 8 (pre-guard) + max(src_len, DEST_SIZE) + 8 (post-guard)
         *
         * strlcpy() must leave the guard regions untouched.
         */
        size_t src_len = strlen(payloads[i]);
        size_t max_len = (src_len > DEST_SIZE) ? src_len : DEST_SIZE;
        size_t alloc_size = 8 + max_len + 8;
        unsigned char *mem = malloc(alloc_size);
        ck_assert_ptr_nonnull(mem);

        /* Sentinel-fill the entire region (pre-guard + destination + post-guard). */
        memset(mem, GUARD_BYTE, alloc_size);

        char *dest = (char *)(mem + 8); /* destination occupies mem[8..8+DEST_SIZE-1] */

        /* Call the bounds-checked function with the explicit size limit. */
        strlcpy(dest, payloads[i], DEST_SIZE);

        /* Primary invariant: first post-guard byte must be untouched. */
        ck_assert_msg(mem[8 + DEST_SIZE] == GUARD_BYTE,
            "strlcpy overflowed: guard byte at offset %d was corrupted "
            "for payload %d (src_len=%zu)",
            8 + DEST_SIZE, i, src_len);

        /* Secondary invariant: destination must be NUL-terminated. */
        ck_assert_msg(dest[DEST_SIZE - 1] == '\0' || src_len < (size_t)DEST_SIZE,
            "strlcpy result is not NUL-terminated for payload %d", i);

        free(mem);
    }
}
END_TEST

START_TEST(test_strcpy_buffer_overflow_documented)
{
    /*
     * Document the vulnerability: strcpy() has NO bounds checking and WILL
     * write past the end of dest.  For each payload longer than DEST_SIZE the
     * guard byte immediately following the destination buffer must be corrupted,
     * proving the overflow occurs.
     *
     * To prevent heap-allocator corruption (and a crash before the assertion),
     * we allocate 8 (pre-guard) + src_len+1 (room for the full copy) + 8
     * (post-guard) bytes.  Only the guard byte at offset 8+DEST_SIZE is
     * examined — it sits inside the allocation so the write is not
     * out-of-bounds from the allocator's perspective, but it is past the
     * logical destination buffer of DEST_SIZE bytes.
     */
    const char *overflow_payloads[] = {
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",  /* 2.5x overflow (40 chars)  */
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"   /* 10x overflow (160 chars) */
    };
    int num_overflow = (int)(sizeof(overflow_payloads) / sizeof(overflow_payloads[0]));

    for (int i = 0; i < num_overflow; i++) {
        size_t src_len = strlen(overflow_payloads[i]);

        /* Allocate enough that strcpy() does not escape the heap allocation. */
        size_t alloc_size = 8 + src_len + 1 + 8;
        unsigned char *mem = malloc(alloc_size);
        ck_assert_ptr_nonnull(mem);

        /* Sentinel-fill the entire region. */
        memset(mem, GUARD_BYTE, alloc_size);

        char *dest = (char *)(mem + 8); /* destination occupies mem[8..8+DEST_SIZE-1] */

        /* Call the unbounded (unsafe) function. */
        strcpy(dest, overflow_payloads[i]);

        /* Vulnerability confirmed: strcpy() corrupts the post-dest guard byte. */
        ck_assert_msg(mem[8 + DEST_SIZE] != GUARD_BYTE,
            "strcpy should have overflowed past dest[%d] for payload %d "
            "(src_len=%zu) but guard byte was not corrupted",
            DEST_SIZE, i, src_len);

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

    tcase_add_test(tc_core, test_strlcpy_no_buffer_overflow);
    tcase_add_test(tc_core, test_strcpy_buffer_overflow_documented);
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
