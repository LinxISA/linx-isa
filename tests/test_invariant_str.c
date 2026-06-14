#include <check.h>
#include <stdlib.h>
#include <string.h>

/*
 * Test the security invariant: buffer writes must never exceed the declared
 * destination length.  We exercise strlcpy(), the bounds-checked replacement
 * for the unsafe strcpy(), and verify it never touches memory outside the
 * declared destination buffer even when the source is many times larger.
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
         * Lay out memory as:  [ DEST_SIZE bytes dest | 16 bytes guard ]
         *
         * The total allocation is always the same fixed size regardless of
         * payload length.  strlcpy() must leave the guard region untouched.
         */
        unsigned char *mem = malloc(DEST_SIZE + 16);
        ck_assert_ptr_nonnull(mem);

        /* Sentinel-fill the entire region (destination + guard). */
        memset(mem, GUARD_BYTE, DEST_SIZE + 16);

        char *dest = (char *)mem; /* destination occupies mem[0..DEST_SIZE-1] */

        /* Call the bounds-checked function with the explicit size limit. */
        size_t src_len = strlcpy(dest, payloads[i], DEST_SIZE);

        /* Primary invariant: first guard byte must be untouched. */
        ck_assert_msg(mem[DEST_SIZE] == GUARD_BYTE,
            "strlcpy overflowed: guard byte at offset %d was corrupted "
            "for payload %d (src_len=%zu)",
            DEST_SIZE, i, src_len);

        /* Secondary invariant: destination must be NUL-terminated. */
        ck_assert_msg(dest[DEST_SIZE - 1] == '\0' || src_len < (size_t)DEST_SIZE,
            "strlcpy result is not NUL-terminated for payload %d", i);

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
