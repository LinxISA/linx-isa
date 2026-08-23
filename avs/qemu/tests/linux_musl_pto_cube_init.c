#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdlib.h>
#include <sys/reboot.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>

static void setup_console(void)
{
	int fd = open("/dev/console", O_RDWR);

	if (fd < 0)
		fd = open("/dev/ttyS0", O_RDWR);
	if (fd < 0)
		return;
	(void)dup2(fd, STDIN_FILENO);
	(void)dup2(fd, STDOUT_FILENO);
	(void)dup2(fd, STDERR_FILENO);
	if (fd > STDERR_FILENO)
		(void)close(fd);
}

static void write_text(const char *text)
{
	size_t length = 0;

	while (text[length])
		length++;
	(void)syscall(SYS_write, STDOUT_FILENO, text, length);
}

static void write_decimal(unsigned int value)
{
	char digits[10];
	size_t count = 0;

	do {
		digits[count++] = (char)('0' + value % 10);
		value /= 10;
	} while (value);
	while (count)
		(void)syscall(SYS_write, STDOUT_FILENO, &digits[--count], 1);
}

static void emit_case_marker(const char *kind, const char *name, int value)
{
	write_text("PTO_CUBE_CASE_");
	write_text(kind);
	write_text(" ");
	write_text(name);
	if (value >= 0) {
		write_text(" value=");
		write_decimal((unsigned int)value);
	}
	write_text("\n");
}

static void poweroff_now(void)
{
	sync();
	(void)reboot(RB_POWER_OFF);
	for (;;)
		pause();
}

static void run_case(const char *path, const char *name,
		     const char *start_marker, const char *pass_marker)
{
	pid_t child;
	pid_t waited;
	int status = 0;

	write_text(start_marker);
	child = fork();
	if (child < 0) {
		emit_case_marker("FAIL_FORK", name, errno);
		poweroff_now();
	}
	if (child == 0) {
		char *const argv[] = { (char *)path, NULL };
		char *const envp[] = { NULL };

		execve(path, argv, envp);
		emit_case_marker("FAIL_EXEC", name, errno);
		_exit(126);
	}

	waited = waitpid(child, &status, 0);
	if (waited != child) {
		emit_case_marker("FAIL_WAIT", name, errno);
		poweroff_now();
	}
	if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
		int value = WIFEXITED(status) ? WEXITSTATUS(status) :
			    (WIFSIGNALED(status) ? 128 + WTERMSIG(status) : 255);

		emit_case_marker("FAIL_EXIT", name, value);
		poweroff_now();
	}
	write_text(pass_marker);
}

int main(void)
{
	setup_console();
	write_text("PTO_CUBE_START count=6\n");
	run_case("/pto_cube/tmatmul_acc_fp32_32x32x32.elf",
		 "tmatmul_acc_fp32_32x32x32",
		 "PTO_CUBE_CASE_START tmatmul_acc_fp32_32x32x32\n",
		 "PTO_CUBE_CASE_PASS tmatmul_acc_fp32_32x32x32 value=0\n");
	run_case("/pto_cube/tmatmul_bias_fp16_32x64x64.elf",
		 "tmatmul_bias_fp16_32x64x64",
		 "PTO_CUBE_CASE_START tmatmul_bias_fp16_32x64x64\n",
		 "PTO_CUBE_CASE_PASS tmatmul_bias_fp16_32x64x64 value=0\n");
	run_case("/pto_cube/tmatmul_bias_fp32_32x32x32.elf",
		 "tmatmul_bias_fp32_32x32x32",
		 "PTO_CUBE_CASE_START tmatmul_bias_fp32_32x32x32\n",
		 "PTO_CUBE_CASE_PASS tmatmul_bias_fp32_32x32x32 value=0\n");
	run_case("/pto_cube/tmatmul_fp16_16x32x32.elf",
		 "tmatmul_fp16_16x32x32",
		 "PTO_CUBE_CASE_START tmatmul_fp16_16x32x32\n",
		 "PTO_CUBE_CASE_PASS tmatmul_fp16_16x32x32 value=0\n");
	run_case("/pto_cube/tmatmul_fp16_32x64x64.elf",
		 "tmatmul_fp16_32x64x64",
		 "PTO_CUBE_CASE_START tmatmul_fp16_32x64x64\n",
		 "PTO_CUBE_CASE_PASS tmatmul_fp16_32x64x64 value=0\n");
	run_case("/pto_cube/tmatmul_fp32_32x32x32.elf",
		 "tmatmul_fp32_32x32x32",
		 "PTO_CUBE_CASE_START tmatmul_fp32_32x32x32\n",
		 "PTO_CUBE_CASE_PASS tmatmul_fp32_32x32x32 value=0\n");

	write_text("PTO_CUBE_PASS count=6\n");
	poweroff_now();
}
