from __future__ import print_function

import os
import pygame
# import pyudev
import subprocess

from nintendo_output import SnesController

class InputDevice:
	button_map = {
		0: SnesController.BUTTON_B,
		1: SnesController.BUTTON_A,
		2: SnesController.BUTTON_Y,
		3: SnesController.BUTTON_X,
		4: SnesController.BUTTON_L,
		5: SnesController.BUTTON_R,
		6: SnesController.BUTTON_SELECT,
		7: SnesController.BUTTON_START,
	}
	axis_map = {}
	hat_map = {}

	special_button_down = False
	special_button_released = False

	def __init__(self, device_number, joystick, output):
		self.device_number = device_number
		self.player_number = device_number + 1
		self.joystick = joystick
		self.output = output
	def get_dpad(self):
		pass
	def write_player_num(self):
		pass

	def button(self, button, down):
		self.output.button(self.player_number, button, down)

	def event(self, ev):
		if ev.type == pygame.JOYAXISMOTION:
			if self.special_button_down:
				return
			if ev.axis in self.axis_map:
				val = self.joystick.get_axis(ev.axis)
				neg, pos = self.axis_map[ev.axis]
				negval, posval = False, False
				if val < 0:
					button, thres = neg
					negval = val < thres
				elif val > 0:
					button, thres = pos
					posval = val > thres
				self.button(neg[0], negval)
				self.button(pos[0], posval)
		elif ev.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
			if ev.button in self.button_map:
				button = self.button_map[ev.button]
				down = ev.type == pygame.JOYBUTTONDOWN
				if button < 0:
					self.special_button(button, down)
					self.special_button_down = down
					self.special_button_released = not down
				elif self.special_button_down:
					self.special_button(-1, True)
				elif self.special_button_released:
					self.special_button_released = False
				elif not self.special_button_released:
					self.button(button, down)
			# else:
			# 	print('Unknown button {}: {}'.format(ev.button, 'down' if ev.type == pygame.JOYBUTTONDOWN else 'up'))
			# if ev.type == pygame.JOYBUTTONDOWN:
			# 	print('JOYBUTTONDOWN: {} {}'.format(ev.joy, ev.button))
			# elif ev.type == pygame.JOYBUTTONUP:
			# 	print('JOYBUTTONUP: {} {}'.format(ev.joy, ev.button))
		elif ev.type == pygame.JOYHATMOTION:
			if self.special_button_down:
				return
			if self.special_button_released:
				self.special_button_released = False
				return
			# print('JOYHATMOTION: {} {}: {}'.format(ev.joy, ev.hat, (x, y)))
			if ev.hat in self.hat_map:
				x, y = self.joystick.get_hat(ev.hat)

				state = [y > 0, y < 0, x < 0, x > 0]
				for i in range(4):
					self.button(self.hat_map[ev.hat][i], state[i])

	def special_button(self, button_id, down):
		if button_id == -1:
			if not down:
				dpad = self.get_dpad()
				# UDLR -> 1, 4, 2, 3
				dpad_map = {0: 1, 1: 4, 2: 2, 3: 3}
				for button, player_number in dpad_map.iteritems():
					if dpad[button]:
						self.player_number = player_number
						break
				self.write_player_num()

	def __repr__(self):
		return '{}({}, {})'.format(self.__class__.__name__, self.device_number, self.joystick.get_name())

	@staticmethod
	def get(name):
		for device in devices:
			if name in device.names:
				return device
		# return InputDevice

class XBoxController(InputDevice):
	#         xpad                       xboxdrv
	names = ("Microsoft X-Box 360 pad", "Xbox Gamepad (userspace driver)", "Xbox 360 Wireless Receiver")
	button_map = {
		0: SnesController.BUTTON_B,
		1: SnesController.BUTTON_A,
		2: SnesController.BUTTON_Y,
		3: SnesController.BUTTON_X,

		4: SnesController.BUTTON_L,
		5: SnesController.BUTTON_R,
		
		6: SnesController.BUTTON_SELECT,
		7: SnesController.BUTTON_START,
		# wireless...?
		13: SnesController.BUTTON_UP,
		14: SnesController.BUTTON_DOWN,
		11: SnesController.BUTTON_LEFT,
		12: SnesController.BUTTON_RIGHT,

		# guide button
		8: -1,

	}
	axis_map = {
		0: [[SnesController.BUTTON_LEFT, -0.5], [SnesController.BUTTON_RIGHT, 0.5]], # neg left, pos right
		1: [[SnesController.BUTTON_UP, -0.5], [SnesController.BUTTON_DOWN, 0.5]], # neg up, pos down
		# 2: 2,
		# 3: 3
	}
	hat_map = {
		0: [SnesController.BUTTON_UP, SnesController.BUTTON_DOWN, SnesController.BUTTON_LEFT, SnesController.BUTTON_RIGHT]
	}
	def get_dpad(self):
		# todo: check for wireless, does it have a hat? if yes then fix code
		if self.joystick.get_numhats() > 0:
			x, y = self.joystick.get_hat(0)
			up = y > 0
			down = y < 0
			left = x < 0
			right = x > 0
			return [up, down, left, right]
		else:
			buttons = [13, 14, 11, 12]
			return [bool(self.joystick.get_button(btn)) for btn in buttons]

class PS3Controller(InputDevice):
	#         USB                                Bluetooth
	names = ("Sony PLAYSTATION(R)3 Controller", "PLAYSTATION(R)3 Controller")
	button_map = {
		14: SnesController.BUTTON_B,
		13: SnesController.BUTTON_A,
		15: SnesController.BUTTON_Y,
		12: SnesController.BUTTON_X,

		10: SnesController.BUTTON_L,
		11: SnesController.BUTTON_R,

		0: SnesController.BUTTON_SELECT,
		3: SnesController.BUTTON_START,

		4: SnesController.BUTTON_UP,
		6: SnesController.BUTTON_DOWN,
		7: SnesController.BUTTON_LEFT,
		5: SnesController.BUTTON_RIGHT,

		# PS button
		16: -1,
	}
	axis_map = {
		0: [[SnesController.BUTTON_LEFT, -0.5], [SnesController.BUTTON_RIGHT, 0.5]], # neg left, pos right
		1: [[SnesController.BUTTON_UP, -0.5], [SnesController.BUTTON_DOWN, 0.5]], # neg up, pos down
		# 2: 2,
		# 3: 3
	}

	def get_dpad(self):
		buttons = [4, 6, 7, 5]
		return [bool(self.joystick.get_button(btn)) for btn in buttons]

	def write_player_num(self):
		subprocess.Popen(['sixled', '/sys/class/input/js{}'.format(self.device_number), str(self.player_number)])
		# if 0 < self.player_number <= 4:
		# 	mask = 1 << (self.player_number - 1)
		# else:
		# 	mask = self.player_number
		# c = pyudev.Context()
		# d = pyudev.Device.from_name(c, 'input', 'js{}'.format(self.device_number))
		# hid_parent = d.find_parent('hid')
		# leds = pyudev.list_devices(parent=hid_parent, subsystem='leds')
		# for led in leds:
		# 	i = int(led.sys_name[-1])
		# 	with open(os.path.join(led.sys_path, 'brightness'), 'w') as f:
		# 		f.write('1' if (1 << i) & mask else '0')
		# device_dir = '/sys/class/input/js{}/device/device'.format(self.device_number)
		# device_id = os.path.basename(os.path.realpath(device_dir))
		# leds_dir = os.path.join(device_dir, 'leds')
		# for i in range(0, 4):
		# 	led_path = os.path.join(leds_dir, '{}::sony{}'.format(device_id, i + 1), 'brightness')
		# 	with open(led_path, 'w') as f:
		# 		f.write('1' if (1 << i) & mask else '0')

devices = [XBoxController, PS3Controller]