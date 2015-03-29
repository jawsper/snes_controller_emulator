#!/usr/bin/python

import pygame

from controller_input import InputDevice
from nintendo_output import SnesControllerMux

class Main:
	def joystick_loop(self):
		# main loop
		while not self.done:
			try:
				event = pygame.event.wait()
				if event.type == pygame.QUIT:
					self.done = True
				elif event.type in (pygame.JOYAXISMOTION, pygame.JOYBALLMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION):
					if event.joy in self.inputs:
						self.inputs[event.joy].event(event)
				else:
					print(event.type)
			except KeyboardInterrupt:
				self.done = True


	def main(self):
		import sys
		self.output = SnesControllerMux(sys.argv[1] if len(sys.argv) > 1 else None)

		pygame.init()

		self.done = False
		while not self.done:
			pygame.joystick.init()

			if pygame.joystick.get_count() == 0:
				print('No joysticks found!')
				return
			self.inputs = {}
			for i in range(pygame.joystick.get_count()):
				joystick = pygame.joystick.Joystick(i)
				joystick.init()
				self.inputs[i] = InputDevice.get(joystick.get_name())(i, joystick, self.output)
			print(self.inputs)

			self.output.enable()

			self.joystick_loop()

			self.output.disable()

			pygame.joystick.quit()



if __name__ == '__main__':
	Main().main()