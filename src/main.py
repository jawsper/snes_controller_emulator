#!/usr/bin/python2

import pygame

from controller_input import InputDevice
from nintendo_output import SnesControllerMux

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
				if event.type == pygame.QUIT:
					done = True
				elif event.type in (pygame.JOYAXISMOTION, pygame.JOYBALLMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION):
					if event.joy in self.inputs:
						self.inputs[event.joy].event(event)
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

		self.inputs = {}
		self.inputs_old = {}
		if len(self.joystick) == 0:
			print('No joysticks found!')
			return
		for i in range(0, len(self.joystick)):
			self.inputs[i] = InputDevice.get(self.joystick[i].get_name())(i, self.joystick[0], self.output)
		print(self.inputs)

		self.output.enable()

		self.joystick_loop()

		self.output.disable()

if __name__ == '__main__':
	Main().main()