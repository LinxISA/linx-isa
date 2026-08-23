#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/reboot.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>

static const char *const cases[] = {
	"tmatmul_acc_fp32_32x32x32",
	"tmatmul_bias_fp16_32x64x64",
	"tmatmul_bias_fp32_32x32x32",
	"tmatmul_fp16_16x32x32",
	"tmatmul_fp16_32x64x64",
	"tmatmul_fp32_32x32x32",
};

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

static void emit_case_marker(const char *kind, const char *name, int value)
{
	char line[192];
	int length;

	if (value >= 0)
		length = snprintf(line, sizeof(line), "PTO_CUBE_CASE_%s %s value=%d\n",
				  kind, name, value);
	else
		length = snprintf(line, sizeof(line), "PTO_CUBE_CASE_%s %s\n",
				  kind, name);
	if (length > 0)
		(void)syscall(SYS_write, STDOUT_FILENO, line, (size_t)length);
}

static void poweroff_now(void)
{
	sync();
	(void)reboot(RB_POWER_OFF);
	for (;;)
		pause();
}

int main(void)
{
	size_t index;

	setup_console();
	(void)syscall(SYS_write, STDOUT_FILENO, "PTO_CUBE_START count=6\n", 23);

	for (index = 0; index < sizeof(cases) / sizeof(cases[0]); ++index) {
		char path[160];
		pid_t child;
		pid_t waited;
		int status = 0;

		(void)snprintf(path, sizeof(path), "/pto_cube/%s.elf", cases[index]);
		emit_case_marker("START", cases[index], -1);
		child = fork();
		if (child < 0) {
			emit_case_marker("FAIL_FORK", cases[index], errno);
			poweroff_now();
		}
		if (child == 0) {
			char *const argv[] = { path, NULL };
			char *const envp[] = { NULL };

			execve(path, argv, envp);
			emit_case_marker("FAIL_EXEC", cases[index], errno);
			_exit(126);
		}

		waited = waitpid(child, &status, 0);
		if (waited != child) {
			emit_case_marker("FAIL_WAIT", cases[index], errno);
			poweroff_now();
		}
		if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
			int value = WIFEXITED(status) ? WEXITSTATUS(status) :
				    (WIFSIGNALED(status) ? 128 + WTERMSIG(status) : 255);

			emit_case_marker("FAIL_EXIT", cases[index], value);
			poweroff_now();
		}
		emit_case_marker("PASS", cases[index], 0);
	}

	(void)syscall(SYS_write, STDOUT_FILENO, "PTO_CUBE_PASS count=6\n", 22);
	poweroff_now();
}
