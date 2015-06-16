#!/usr/bin/python

# set SDL to dummy videodriver so it can run fully headless
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
import pyudev
import signal

from controller_input import InputDevice
from nintendo_output import SnesControllerMux

class TeensyDetect:
	def __init__(self, notify_event, vid='16c0', pid='0483'):
		self.devices = [[vid, pid]]
		self.notify_event = notify_event
		context = pyudev.Context()
		monitor = pyudev.Monitor.from_netlink(context)
		monitor.filter_by('tty')
		self.observer = pyudev.MonitorObserver(monitor, self.on_event)
		self.observer.start()

		for device in context.list_devices(subsystem='tty'):
			if self.is_teensy(device):
				self.device = device
				self.notify_event('add', device)
				break
		else:
			self.device = None

	def is_teensy(self, device):
		if device and device.parent and device.parent.parent:
			parent = device.parent.parent
			if 'idVendor' in parent.attributes and 'idProduct' in parent.attributes:
				vid = parent.attributes['idVendor'].decode('ascii')
				pid = parent.attributes['idProduct'].decode('ascii')
				if [vid, pid] in self.devices:
					return True
		return False


	def on_event(self, action, device):
		if action == 'remove':
			if self.device is None:
				return
			if device == self.device:
				self.device = None
				self.notify_event(action, device)
		elif action == 'add':
			if self.device is not None:
				return
			if self.is_teensy(device):
				self.device = device
				self.notify_event(action, device)

class JoystickMonitor:
	def __init__(self, notify_event):
		self.notify_event = notify_event
		context = pyudev.Context()
		monitor = pyudev.Monitor.from_netlink(context)
		monitor.filter_by('input')
		self.observer = pyudev.MonitorObserver(monitor, self.notify_event)
		self.observer.start()

class Main:
	def sigint_handler(self, signo, frame):
		print('sigint')
		self.done = True
		pygame.event.post(pygame.event.Event(pygame.USEREVENT, action='kill'))

	def joystick_loop(self):
		# main loop
		# clock = pygame.time.Clock()
		while not self.done and not self.joystick_changed:
			# for event in pygame.event.get():
			if True:
				event = pygame.event.wait()
				if event.type == pygame.QUIT:
					# print('pygame_quit')
					self.done = True
				elif event.type in (pygame.JOYAXISMOTION, pygame.JOYBALLMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION):
					if event.joy in self.inputs:
						self.inputs[event.joy].event(event)
				elif event.type == pygame.USEREVENT:
					pass # accept it and go on (probably going to exit the loop)
					# print('user_event')
					# if hasattr(event, 'action'):
					# 	print(event.action)
				else:
					print(event.type)
				# clock.tick(60)
		self.joystick_changed = False

	def on_teensy(self, action, device):
		# print('teensy:', action, device)
		if action == 'remove':
			self.output.set_port(None)
		elif action == 'add':
			self.output.set_port('/dev/' + device.sys_name)
	def on_joystick(self, action, device):
		if not device.sys_name.startswith('js'):
			return
		# print('joystick:', action, device)
		if not self.joystick_changed:
			self.joystick_changed = True
			pygame.event.post(pygame.event.Event(pygame.USEREVENT, action='joystick_changed'))

	def main(self):
		import sys
		self.output = SnesControllerMux(sys.argv[1] if len(sys.argv) > 1 else None)

		self.teensy_detect = TeensyDetect(self.on_teensy)
		self.joystick_monitor = JoystickMonitor(self.on_joystick)

		pygame.init()

		signal.signal(signal.SIGINT, self.sigint_handler)

		self.done = False
		self.joystick_changed = False
		while not self.done:
			pygame.joystick.init()

			self.inputs = {}
			for i in range(pygame.joystick.get_count()):
				joystick = pygame.joystick.Joystick(i)
				joystick.init()
				self.inputs[i] = InputDevice.get(joystick.get_name())(i, joystick, self.output)
			print('Inputs:', self.inputs)

			self.output.enable()

			# print('before loop')
			self.joystick_loop()
			# print('after loop')

			self.output.disable()

			pygame.joystick.quit()



if __name__ == '__main__':
	Main().main()