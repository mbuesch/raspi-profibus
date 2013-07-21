/*
 * Raspberry Pi - Profibus DP communication processor GPIO setup
 *
 * Copyright (c) 2013 Michael Buesch <m@bues.ch>
 *
 * Licensed under the terms of the GNU General Public License version 2
 * or (at your option) any later version.
 */

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/mman.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>


#define GPIO_BASE	0x20200000
#define GPIO_SIZE	4096
#define NR_GPIOS	54

#define GPPUD		(0x94 / 4)
#define  GPPUD_OFF	0
#define  GPPUD_DOWN	1
#define  GPPUD_UP	2
#define GPPUDCLK0	(0x98 / 4)
#define GPPUDCLK1	(0x9C / 4)


volatile uint32_t *gpio_map;


static void msleep(unsigned int msecs)
{
	int err;
	struct timespec time;

	if (!msecs)
		return;
	time.tv_sec = 0;
	while (msecs >= 1000) {
		time.tv_sec++;
		msecs -= 1000;
	}
	time.tv_nsec = msecs;
	time.tv_nsec *= 1000000;
	do {
		err = nanosleep(&time, &time);
	} while (err && errno == EINTR);
	if (err) {
		fprintf(stderr, "nanosleep() failed with: %s\n",
			strerror(errno));
	}
}

static int have_gpio_mapping(void)
{
	int fd;
	char buf[4096] = { 0, };
	ssize_t ret;

	fd = open("/proc/iomem", O_RDONLY);
	if (fd < 0) {
		fprintf(stderr, "Failed to open /proc/iomem: %s\n",
			strerror(errno));
		return 0;
	}

	ret = read(fd, buf, sizeof(buf) - 1);
	if (ret <= 0) {
		fprintf(stderr, "Failed to read /proc/iomem: %s\n",
			strerror(errno));
		return 0;
	}

	return strstr(buf, "20200000-20200fff : bcm2708_gpio") != NULL;
}

static int set_gpio_pull(unsigned int gpio, uint32_t mode)
{
	unsigned int clkreg = (gpio < 32) ? GPPUDCLK0 : GPPUDCLK1;
	unsigned int clkreg_bitnr = gpio % 32;

	if (gpio >= NR_GPIOS)
		return -ENODEV;
	if (mode != GPPUD_OFF && mode != GPPUD_UP && mode != GPPUD_DOWN)
		return -EINVAL;

	gpio_map[GPPUD] = mode;
	msleep(1);
	gpio_map[clkreg] |= (1 << clkreg_bitnr);
	msleep(1);
	gpio_map[GPPUD] = GPPUD_OFF;
	gpio_map[clkreg] = 0;

	return 0;
}

static int map_gpio(void)
{
	int fd;
	void *ptr;

	fd = open("/dev/mem", O_RDWR | O_SYNC);
	if (fd < 0) {
		fprintf(stderr, "Failed to open /dev/mem: %s\n",
			strerror(errno));
		return -ENOMEM;
	}

	ptr = mmap(NULL, GPIO_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, GPIO_BASE);
	close(fd);
	if (ptr == MAP_FAILED) {
		fprintf(stderr, "Failed to map GPIO area: %s\n",
			strerror(errno));
		return -ENOMEM;
	}

	gpio_map = (volatile void *)ptr;

	return 0;
}

static void unmap_gpio(void)
{
	int err;
	void *ptr;

	ptr = (void *)gpio_map;
	if (!ptr)
		return;
	gpio_map = NULL;

	err = munmap(ptr, GPIO_SIZE);
	if (err) {
		fprintf(stderr, "Failed to unmap GPIO area: %s\n",
			strerror(errno));
	}
}

static void usage(FILE *fd, int argc, char **argv)
{
	fprintf(fd, "Usage: %s GPIO_NR MODE\n\n", argv[0]);
	fprintf(fd, "MODE may be one of 'up', 'down' or 'off'\n");
}

int main(int argc, char **argv)
{
	int err;
	unsigned int gpio;
	uint32_t mode;

	if (argc != 3) {
		usage(stderr, argc, argv);
		return EXIT_FAILURE;
	}
	if (sscanf(argv[1], "%u", &gpio) != 1 || gpio >= NR_GPIOS) {
		fprintf(stderr, "Invalid GPIO number.\n");
		return EXIT_FAILURE;
	}
	if (strcasecmp(argv[2], "up") == 0)
		mode = GPPUD_UP;
	else if (strcasecmp(argv[2], "down") == 0)
		mode = GPPUD_DOWN;
	else if (strcasecmp(argv[2], "off") == 0)
		mode = GPPUD_OFF;
	else {
		fprintf(stderr, "Invalid mode\n");
		return EXIT_FAILURE;
	}

	if (!have_gpio_mapping()) {
		fprintf(stderr, "Did not find GPIO mapping.\n"
			"Not running on Raspberry Pi?\n");
		return EXIT_FAILURE;
	}

	err = map_gpio();
	if (err)
		return EXIT_FAILURE;

	err = set_gpio_pull(gpio, mode);
	if (err)
		fprintf(stderr, "Failed to set GPIO pullup/pulldown mode.\n");

	unmap_gpio();

	return EXIT_SUCCESS;
}
