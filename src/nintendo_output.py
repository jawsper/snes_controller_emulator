import serial

class RetroNintendoController(object):
	def __init__(self, port, bit_count):
		self.port = port

		self.bit_count = bit_count

		self.buttons = { 0: [False] * self.bit_count }

		print(self.port)

	def enable(self):
		self.serial = serial.Serial(self.port, 115200)

	def disable(self):
		self.serial.close()

	def button_down(self, button, controller=0):
		self.buttons[controller][button] = True
	def button_up(self, button, controller=0):
		self.buttons[controller][button] = False
	def button(self, button, down, controller=0):
		# if down != self.buttons[controller][button]:
		# 	print('button({}, {}, {})'.format(button, down, controller))
		if down:
			self.button_down(button, controller)
		else:
			self.button_up(button, controller)

		val = 0
		for x in range(len(self.buttons[controller])):
			val |= 1 if self.buttons[controller][x] else 0
			val <<= 1
		val >>= 1
		val = bytearray([controller & 0xFF, (val >> 8) & 0xFF, val & 0xFF])
		print(repr(val))
		self.serial.write(val)


# class NesController(RetroNintendoController):
# 	def __init__(self, port):
# 		super(NesController, self).__init__(port, 8)

class SnesController(RetroNintendoController):
	BUTTON_B = 0
	BUTTON_Y = 1
	BUTTON_SELECT = 2
	BUTTON_START = 3
	BUTTON_UP = 4
	BUTTON_DOWN = 5
	BUTTON_LEFT = 6
	BUTTON_RIGHT = 7
	BUTTON_A = 8
	BUTTON_X = 9
	BUTTON_L = 10
	BUTTON_R = 11

	BIT_COUNT = 16
	def __init__(self, port):
		super(SnesController, self).__init__(port, 16)

class SnesControllerMux:
	def __init__(self, port):
		self.buttons = {}

		self.port = port
		self.multitap = False

	def enable(self):
		self.serial = serial.Serial(self.port, 115200)
	def disable(self):
		self.serial.close()

	controller_add = 0
	def button(self, controller_id, button_id, value):
		controller_id += self.controller_add

		if not controller_id in self.buttons:
			self.buttons[controller_id] = [False] * SnesController.BIT_COUNT

		self.buttons[controller_id][button_id] = value

		# print('button({}, {}, {})'.format(controller_id, button_id, value))

		val = 0
		for x in range(len(self.buttons[controller_id])):
			val |= 1 if self.buttons[controller_id][x] else 0
			val <<= 1
		val >>= 1
		val = bytearray([controller_id & 0xFF, (val >> 8) & 0xFF, val & 0xFF])
		print(repr(val))
		self.serial.write(val)

if __name__ == '__main__':
	#test = SnesMultitap(10, 9, 11, 25, 8)
	test = SnesController('/dev/ttyACM0')
	test.enable()

	for x in range(2):
		test.on_latch(10)
		for i in range(16):
			test.on_clock(9)
		test.button_down(0, controller=0)
		#test.button_down(0, controller=1)

	test.disable()
	GPIO.cleanup()