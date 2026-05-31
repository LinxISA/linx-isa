typedef unsigned long ulong;
typedef long slong;

enum {
    __NR_write = 64,
    __NR_exit_group = 94,
};

static __attribute__((always_inline)) inline slong
linx_syscall3(long nr, ulong a0, ulong a1, ulong a2)
{
    slong ret;

    __asm__ volatile(
        "c.bstop\n"
        "C.BSTART.SYS\n"
        "c.movr %1, ->a0\n"
        "c.movr %2, ->a1\n"
        "c.movr %3, ->a2\n"
        "c.movr %4, ->a7\n"
        "acrc 1\n"
        "c.bstop\n"
        "C.BSTART.STD\n"
        "c.movr a0, ->%0\n"
        : "=r"(ret)
        : "r"(a0), "r"(a1), "r"(a2), "r"((ulong)nr)
        : "a0", "a1", "a2", "a7", "memory");

    return ret;
}

__attribute__((noreturn)) void _start(void)
{
    char msg[38];
    slong ret;

    msg[0] = 'H';
    msg[1] = 'e';
    msg[2] = 'l';
    msg[3] = 'l';
    msg[4] = 'o';
    msg[5] = ' ';
    msg[6] = 'f';
    msg[7] = 'r';
    msg[8] = 'o';
    msg[9] = 'm';
    msg[10] = ' ';
    msg[11] = 'L';
    msg[12] = 'i';
    msg[13] = 'n';
    msg[14] = 'x';
    msg[15] = ' ';
    msg[16] = 'L';
    msg[17] = 'L';
    msg[18] = 'V';
    msg[19] = 'M';
    msg[20] = ' ';
    msg[21] = '+';
    msg[22] = ' ';
    msg[23] = 'q';
    msg[24] = 'e';
    msg[25] = 'm';
    msg[26] = 'u';
    msg[27] = '-';
    msg[28] = 'u';
    msg[29] = 's';
    msg[30] = 'e';
    msg[31] = 'r';
    msg[32] = 'm';
    msg[33] = 'o';
    msg[34] = 'd';
    msg[35] = 'e';
    msg[36] = '\n';
    msg[37] = 0;

    ret = linx_syscall3(__NR_write, 1, (ulong)msg, 37);
    linx_syscall3(__NR_exit_group, ret == 37 ? 0 : 1, 0, 0);

    for (;;) {
        __asm__ volatile("" ::: "memory");
    }
}
