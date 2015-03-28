/*
 *
 *  sixled - Set leds on sixaxis controllers
 *
 *  Copyright (C) 2009  Bastien Nocera <hadess@hadess.net>
 *  Copyright (C) 2011  Antonio Ospite <ospite@studenti.unina.it>
 *  Copyright (C) 2013  Szymon Janc <szymon.janc@gmail.com>
 *  Copyright (C) 2015  Jasper Seidel <jawsper@jawsper.nl>
 *
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 */

#include <libudev.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <linux/limits.h>
#include <fcntl.h>
#include <stdlib.h>

static struct udev *ctx = NULL;


struct leds_data {
	char *syspath_prefix;
	uint8_t bitmap;
};

static bool set_leds_sysfs(struct leds_data *data)
{
	int i;

	if (!data->syspath_prefix)
		return false;

	/* start from 1, LED0 is never used */
	for (i = 1; i <= 4; i++) {
		char path[PATH_MAX] = { 0 };
		char buf[2] = { 0 };
		int fd;
		int ret;

		snprintf(path, PATH_MAX, "%s%d/brightness",
						data->syspath_prefix, i);

		fd = open(path, O_WRONLY);
		if (fd < 0) {
			error("sixaxis: cannot open %s (%s)", path,
							strerror(errno));
			return false;
		}

		buf[0] = '0' + !!(data->bitmap & (1 << i));
		ret = write(fd, buf, sizeof(buf));
		close(fd);
		if (ret != sizeof(buf))
			return false;
	}

	return true;
}

static char *get_leds_syspath_prefix(struct udev_device *udevice)
{
	struct udev_list_entry *dev_list_entry;
	struct udev_enumerate *enumerate;
	struct udev_device *hid_parent;
	const char *syspath;
	char *syspath_prefix;

	hid_parent = udev_device_get_parent_with_subsystem_devtype(udevice,
								"hid", NULL);

	enumerate = udev_enumerate_new(udev_device_get_udev(udevice));
	udev_enumerate_add_match_parent(enumerate, hid_parent);
	udev_enumerate_add_match_subsystem(enumerate, "leds");
	udev_enumerate_scan_devices(enumerate);

	dev_list_entry = udev_enumerate_get_list_entry(enumerate);
	if (!dev_list_entry) {
		syspath_prefix = NULL;
		goto out;
	}

	syspath = udev_list_entry_get_name(dev_list_entry);

	/*
	 * All the sysfs paths of the LEDs have the same structure, just the
	 * number changes, so strip it and store only the common prefix.
	 *
	 * Subtracting 1 here means assuming that the LED number is a single
	 * digit, this is safe as the kernel driver only exposes 4 LEDs.
	 */
	syspath_prefix = strndup(syspath, strlen(syspath) - 1);

out:
	udev_enumerate_unref(enumerate);

	return syspath_prefix;
}

static uint8_t calc_leds_bitmap(int number)
{
	uint8_t bitmap = 0;

	/* TODO we could support up to 10 (1 + 2 + 3 + 4) */
	if (number > 7)
		return bitmap;

	if (number > 4) {
		bitmap |= 0x10;
		number -= 4;
	}

	bitmap |= 0x01 << number;

	return bitmap;
}

int main(int argc, char** argv)
{
	if(argc != 3) return -1;

	char* dev = argv[1];
	int leds = atoi(argv[2]);

	ctx = udev_new();
	if(!ctx) return -EIO;

	struct udev_device *udevice = udev_device_new_from_syspath(ctx, dev);
	if(!udevice) return -EIO;

	struct leds_data *data;

	data = malloc(sizeof(*data));
	if (!data)
		return -1;

	data->bitmap = calc_leds_bitmap(leds);
	if (data->bitmap == 0) {
		// leds_data_destroy(data);
		return -1;
	}

	/*
	 * It's OK if this fails, set_leds_hidraw() will be used in
	 * case data->syspath_prefix is NULL.
	 */
	data->syspath_prefix = get_leds_syspath_prefix(udevice);


	set_leds_sysfs(data);


	udev_unref(ctx);

	return 0;
}