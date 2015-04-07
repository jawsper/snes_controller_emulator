/*
 *
 *  xpadled - Set leds on xpad controllers
 *  based on sixled
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

#include <errno.h>
#include <error.h>
#include <fcntl.h>
#include <libudev.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <linux/limits.h>

extern struct udev *ctx;

struct leds_data {
	char *syspath;
	uint8_t brightness;
} led_data;

static bool set_leds_sysfs()
{
	if (!led_data.syspath)
		return false;

	char path[PATH_MAX] = { 0 };
	char buf[3] = { 0 };
	int fd;
	int ret;
	
	snprintf(path, PATH_MAX, "%s/brightness",
					led_data.syspath);

	fd = open(path, O_WRONLY);
	if (fd < 0) {
		error(0, 0, "xpadled: cannot open %s (%s)", path,
						strerror(errno));
		return false;
	}

	snprintf(buf, sizeof(buf), "%d", led_data.brightness);
	ret = write(fd, buf, sizeof(buf));
	close(fd);
	if (ret != sizeof(buf))
		return false;

	return true;
}

static char *get_leds_syspath(struct udev_device *udevice)
{
	struct udev_list_entry *led_list_entry;
	struct udev_enumerate *enumerate_leds;
	struct udev_device *hid_parent, *controller_device;
	const char *syspath, *controller_name;
	char *syspath_prefix;
	int i, controller_id;

	controller_device = udev_device_get_parent_with_subsystem_devtype(udevice, "usb", NULL);
	hid_parent = udev_device_get_parent_with_subsystem_devtype(controller_device, "usb", NULL);

	enumerate_leds = udev_enumerate_new(udev_device_get_udev(udevice));
	udev_enumerate_add_match_parent(enumerate_leds, hid_parent);
	udev_enumerate_add_match_subsystem(enumerate_leds, "leds");
	udev_enumerate_scan_devices(enumerate_leds);

	controller_name = udev_device_get_syspath(controller_device);
	controller_id = atoi(strrchr(controller_name, '.') + 1) / 2;

	led_list_entry = udev_enumerate_get_list_entry(enumerate_leds);
	for(i = 0; led_list_entry != NULL; led_list_entry = udev_list_entry_get_next(led_list_entry), i++)
	{
		if(i == controller_id)
		{
			syspath = udev_list_entry_get_name(led_list_entry);
			break;
		}
	}

	if(syspath == NULL)
		goto out;

	syspath_prefix = strdup(syspath);

out:
	udev_enumerate_unref(enumerate_leds);

	return syspath_prefix;
}

static uint8_t calc_leds_brightness(int number, bool raw)
{
	if(raw)
	{
		if(number < 0 || number > 15) return 0;
		return number;
	}
	if(number > 4) return number;
	if(number < 1) return 0;
	return number + 5;
}

bool set_xpad_led(struct udev_device *device, int led, bool raw)
{
	led_data.brightness = calc_leds_brightness(led, raw);
	led_data.syspath = get_leds_syspath(device);
	
	return set_leds_sysfs();
}