/*
 *
 *  padled - Set leds on xpad/sony controllers
 *
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
#include <libudev.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static struct udev *ctx = NULL;

bool set_xpad_led(struct udev_device *device, int led, bool raw);
bool set_sixaxis_led(struct udev_device *device, int led, bool raw);

int main(int argc, char** argv)
{
	bool mode_raw = false;
	int retval = 0;
	int c;

	while((c = getopt(argc, argv, "r")) != -1)
	{
		switch(c)
		{
			case 'r':
				mode_raw = true;
				break;
		}
	}

	if(argc - optind != 2)
	{
		return -EINVAL;
	}

	char* device_syspath = argv[optind];
	int value = atoi(argv[optind + 1]);

	ctx = udev_new();
	if(!ctx)
		return -EIO;

	struct udev_device *udevice = udev_device_new_from_syspath(ctx, device_syspath);
	if(!udevice)
		return -EIO;

	// look at device driver here and run xpad/sixaxis function

	struct udev_device *parent = udev_device_get_parent(udevice);
	parent = udev_device_get_parent(parent);

	const char* driver = udev_device_get_driver(parent);

	if(strcmp(driver, "sony") == 0)
	{
		set_sixaxis_led(udevice, value, mode_raw);
	}
	else if(strcmp(driver, "steamos-xpad") == 0)
	{
		set_xpad_led(udevice, value, mode_raw);
	}

	udev_unref(ctx);

	return retval;
}