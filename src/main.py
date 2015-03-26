#!/usr/bin/python2

import pygame

from controller_input import devices as JoystickMappings
from nintendo_output import SnesControllerMux, SnesController

class InputMapping:
	# key: input, val: output
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

	def __init__(self, num, joystick, controller):
		self.num = num
		self.joystick = joystick
		self.controller = controller
		for dev in JoystickMappings:
			if self.joystick.get_name() in dev.names:
				print('Mapping {} on "{}"'.format(dev.__name__, self.joystick.get_name()))
				self.button_map = dev.button_map
				break
		else:
			print('Default mapping used for "{}"'.format(self.joystick.get_name()))
	def event(self, ev):
		if ev.type == pygame.JOYAXISMOTION:
			val = self.joystick.get_axis(ev.axis)
			#print('JOYAXISMOTION: {} {}: {}'.format(ev.joy, ev.axis, val))
		elif ev.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
			if ev.button in self.button_map:
				button = self.button_map[ev.button]
				down = ev.type == pygame.JOYBUTTONDOWN
				if button == -1 and down:
					self.controller.controller_add = 2 if self.controller.controller_add == 0 else 0
				else:
					self.controller.button(self.num, button, down)
			# else:
			# 	print('Unknown button {}: {}'.format(ev.button, 'down' if ev.type == pygame.JOYBUTTONDOWN else 'up'))
			# if ev.type == pygame.JOYBUTTONDOWN:
			# 	print('JOYBUTTONDOWN: {} {}'.format(ev.joy, ev.button))
			# elif ev.type == pygame.JOYBUTTONUP:
			# 	print('JOYBUTTONUP: {} {}'.format(ev.joy, ev.button))
		elif ev.type == pygame.JOYHATMOTION:
			x, y = self.joystick.get_hat(ev.hat)
			#print('JOYHATMOTION: {} {}: {}'.format(ev.joy, ev.hat, (x, y)))

			btn_up = y > 0
			btn_down = y < 0
			btn_left = x < 0
			btn_right = x > 0

			self.controller.button(self.num, SnesController.BUTTON_UP, btn_up)
			self.controller.button(self.num, SnesController.BUTTON_DOWN, btn_down)
			self.controller.button(self.num, SnesController.BUTTON_LEFT, btn_left)
			self.controller.button(self.num, SnesController.BUTTON_RIGHT, btn_right)

		# elif ev.type == pygame.JOYBALLMOTION:
		# 	print('JOYBALLMOTION: {} {}'.format(ev.joy, ev.hat))

	def __repr__(self):
		return 'InputMapping({}, {})'.format(self.num, self.joystick.get_name())

class Main:
	def joystick_detect(self):
		self.joystick = {}
		for i in range(pygame.joystick.get_count()):
			self.joystick[i] = pygame.joystick.Joystick(i)
			self.joystick[i].init()

	def joystick_loop(self):
		# main loop
		try:
			done = False
			while not done:
				event = pygame.event.wait()
				# for event in pygame.event.get():
				if event.type == pygame.QUIT:
					done = True
				elif event.type in (pygame.JOYAXISMOTION, pygame.JOYBALLMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION):
					if event.joy in self.mappings:
						self.mappings[event.joy].event(event)
		except KeyboardInterrupt:
			pass
		finally:
			for stick in self.joystick.itervalues():
				stick.quit()
			pygame.joystick.quit()


	def main(self):
		import sys
		self.output = SnesControllerMux(sys.argv[1] if len(sys.argv) > 1 else None)

		pygame.init()
		self.joystick_detect()

		self.mappings = {}
		if len(self.joystick) == 0:
			print('No joysticks found!')
			return
		if len(self.joystick) >= 1:
			print('One joystick found!')
			self.mappings[0] = InputMapping(0, self.joystick[0], self.output)
		if len(self.joystick) >= 2:
			print('Two or more joysticks found!')
			# if len(self.joystick) > 2:
			# 	print('Enabling multitap')
			# 	self.output.enable_multitap()
			# else:
			# 	print('Disabling multitap')
			# 	self.output.disable_multitap()
			for i in range(1, len(self.joystick)):
				self.mappings[i] = InputMapping(i, self.joystick[i], self.output)

		self.output.enable()

		print(self.mappings)

		self.joystick_loop()

		self.output.disable()

if __name__ == '__main__':
	Main().main()