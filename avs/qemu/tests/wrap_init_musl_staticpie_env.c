typedef unsigned long ulong;
typedef long slong;

enum {
	__NR_openat = 56,
	__NR_close = 57,
	__NR_write = 64,
	__NR_dup = 23,
	__NR_reboot = 142,
	__NR_exit_group = 94,
	__NR_execve = 221,
};

enum {
	AT_FDCWD = -100,
};

enum {
	O_RDONLY = 0,
	O_WRONLY = 1,
	O_RDWR = 2,
	O_CLOEXEC = 02000000,
};

enum {
	LINUX_REBOOT_MAGIC1 = 0xfee1dead,
	LINUX_REBOOT_MAGIC2 = 672274793,
	LINUX_REBOOT_CMD_POWER_OFF = 0x4321fedc,
};

enum {
	LINX_VIRT_UART_BASE = 0x10000000UL,
};

__attribute__((noinline)) static slong sys_call6(int nr, ulong a0, ulong a1,
						 ulong a2, ulong a3, ulong a4,
						 ulong a5)
{
	slong ret;

	__asm__ volatile(
		"c.movr %1, ->a0\n"
		"c.movr %2, ->a1\n"
		"c.movr %3, ->a2\n"
		"c.movr %4, ->a3\n"
		"c.movr %5, ->a4\n"
		"c.movr %6, ->a5\n"
		"c.movr %7, ->a7\n"
		"acrc 1\n"
		"c.bstop\n"
		"C.BSTART\n"
		"c.movr a0, ->%0\n"
		: "=r"(ret)
		: "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(a5),
		  "r"((ulong)nr)
		: "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "x0",
		  "x1", "x2", "x3", "ra", "memory");
	return ret;
}

static inline slong sys_call4(int nr, ulong a0, ulong a1, ulong a2, ulong a3)
{
	return sys_call6(nr, a0, a1, a2, a3, 0, 0);
}

static inline slong sys_call3(int nr, ulong a0, ulong a1, ulong a2)
{
	return sys_call6(nr, a0, a1, a2, 0, 0, 0);
}

static inline slong sys_call1(int nr, ulong a0)
{
	return sys_call6(nr, a0, 0, 0, 0, 0, 0);
}

static inline slong sys_openat(int dirfd, const char *path, int flags, int mode)
{
	return sys_call4(__NR_openat, (ulong)dirfd, (ulong)path, (ulong)flags,
			 (ulong)mode);
}

static inline slong sys_close(int fd)
{
	return sys_call1(__NR_close, (ulong)fd);
}

static inline slong sys_dup(int fd)
{
	return sys_call1(__NR_dup, (ulong)fd);
}

static inline slong sys_write(int fd, const void *buf, ulong count)
{
	return sys_call3(__NR_write, (ulong)fd, (ulong)buf, count);
}

static inline slong sys_reboot(int magic1, int magic2, int cmd, const void *arg)
{
	return sys_call4(__NR_reboot, (ulong)magic1, (ulong)magic2, (ulong)cmd,
			 (ulong)arg);
}

static inline slong sys_execve(const char *path, char *const argv[],
			       char *const envp[])
{
	return sys_call3(__NR_execve, (ulong)path, (ulong)argv, (ulong)envp);
}

__attribute__((noreturn)) static void sys_exit_group(slong code)
{
	(void)sys_call1(__NR_exit_group, (ulong)code);
	for (;;)
		__asm__ volatile("" : : : "memory");
}

static ulong c_strlen(const char *s)
{
	ulong n = 0;
	while (s[n])
		n++;
	return n;
}

static void emit_raw(const char *s)
{
	(void)sys_write(1, s, c_strlen(s));
}

static void emit_line(const char *s)
{
	char nl[1];

	nl[0] = '\n';
	emit_raw(s);
	(void)sys_write(1, nl, 1);
}

static void uart_putc(char c)
{
	*(volatile unsigned char *)(LINX_VIRT_UART_BASE + 0x0) =
		(unsigned char)c;
}

static void emit_uart_line(const char *s)
{
	while (*s)
		uart_putc(*s++);
	uart_putc('\n');
}

__attribute__((noreturn)) void _start(void)
{
	char marker_start[16];
	char marker_fail[22];
	char ldso[13];
	char hello[7];
	char env_ld_path[21];
	char *argv[3];
	char *envp[2];

	marker_start[0] = 'W';
	marker_start[1] = 'R';
	marker_start[2] = 'A';
	marker_start[3] = 'P';
	marker_start[4] = '_';
	marker_start[5] = 'I';
	marker_start[6] = 'N';
	marker_start[7] = 'I';
	marker_start[8] = 'T';
	marker_start[9] = '_';
	marker_start[10] = 'S';
	marker_start[11] = 'T';
	marker_start[12] = 'A';
	marker_start[13] = 'R';
	marker_start[14] = 'T';
	marker_start[15] = 0;

	marker_fail[0] = 'W';
	marker_fail[1] = 'R';
	marker_fail[2] = 'A';
	marker_fail[3] = 'P';
	marker_fail[4] = '_';
	marker_fail[5] = 'I';
	marker_fail[6] = 'N';
	marker_fail[7] = 'I';
	marker_fail[8] = 'T';
	marker_fail[9] = '_';
	marker_fail[10] = 'E';
	marker_fail[11] = 'X';
	marker_fail[12] = 'E';
	marker_fail[13] = 'C';
	marker_fail[14] = 'V';
	marker_fail[15] = 'E';
	marker_fail[16] = '_';
	marker_fail[17] = 'F';
	marker_fail[18] = 'A';
	marker_fail[19] = 'I';
	marker_fail[20] = 'L';
	marker_fail[21] = 0;

	ldso[0] = '/';
	ldso[1] = 'l';
	ldso[2] = 'i';
	ldso[3] = 'b';
	ldso[4] = '/';
	ldso[5] = 'l';
	ldso[6] = 'd';
	ldso[7] = '.';
	ldso[8] = 's';
	ldso[9] = 'o';
	ldso[10] = '.';
	ldso[11] = '1';
	ldso[12] = 0;

	hello[0] = '/';
	hello[1] = 'h';
	hello[2] = 'e';
	hello[3] = 'l';
	hello[4] = 'l';
	hello[5] = 'o';
	hello[6] = 0;

	env_ld_path[0] = 'L';
	env_ld_path[1] = 'D';
	env_ld_path[2] = '_';
	env_ld_path[3] = 'L';
	env_ld_path[4] = 'I';
	env_ld_path[5] = 'B';
	env_ld_path[6] = 'R';
	env_ld_path[7] = 'A';
	env_ld_path[8] = 'R';
	env_ld_path[9] = 'Y';
	env_ld_path[10] = '_';
	env_ld_path[11] = 'P';
	env_ld_path[12] = 'A';
	env_ld_path[13] = 'T';
	env_ld_path[14] = 'H';
	env_ld_path[15] = '=';
	env_ld_path[16] = '/';
	env_ld_path[17] = 'l';
	env_ld_path[18] = 'i';
	env_ld_path[19] = 'b';
	env_ld_path[20] = 0;

	argv[0] = ldso;
	argv[1] = hello;
	argv[2] = 0;
	envp[0] = env_ld_path;
	envp[1] = 0;

	/*
	 * Keep PID1 on the inherited stdio fds instead of reopening
	 * /dev/console. The current Linx runtime can trip kernel return-path
	 * faults in that console-open path for some glibc hello variants.
	 * Mirror markers to the virt UART so the smoke harness still sees them
	 * even before userspace stdio is fully reliable.
	 */
	emit_line(marker_start);
	emit_uart_line(marker_start);
	(void)sys_execve(ldso, argv, envp);
	emit_line(marker_fail);
	emit_uart_line(marker_fail);
	(void)sys_reboot(LINUX_REBOOT_MAGIC1, LINUX_REBOOT_MAGIC2,
			 LINUX_REBOOT_CMD_POWER_OFF, 0);
	sys_exit_group(127);
}
