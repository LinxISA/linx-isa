#include <fcntl.h>
#include <stdio.h>
#include <sys/reboot.h>
#include <unistd.h>

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

	printf("HELLO_WORLD_START\n");
	printf("Hello, Linx ISA Linux via QEMU\n");
	printf("HELLO_WORLD_PASS\n");
	fflush(stdout);

	sync();
	reboot(RB_POWER_OFF);
	return 0;
}
