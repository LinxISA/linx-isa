#include <fcntl.h>
#include <stdio.h>
#include <sys/reboot.h>
#include <unistd.h>

static void emit_marker(const char *s)
{
	printf("%s\n", s);
	fflush(stdout);
}

int main(void)
{
	int cfd = open("/dev/console", O_RDWR);
	if (cfd >= 0) {
		(void)dup2(cfd, STDIN_FILENO);
		(void)dup2(cfd, STDOUT_FILENO);
		(void)dup2(cfd, STDERR_FILENO);
		if (cfd > STDERR_FILENO)
			(void)close(cfd);
	}

	emit_marker("HELLO_WORLD_START");
	emit_marker("Hello, Linx ISA Linux via QEMU");
	emit_marker("HELLO_WORLD_PASS");

	sync();
	reboot(RB_POWER_OFF);
	return 0;
}
