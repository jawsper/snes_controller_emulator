import serial


# class NesController(RetroNintendoController):
# 	def __init__(self, port):
# 		super(NesController, self).__init__(port, 8)

class SnesController:
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

class SnesControllerMux:
	def __init__(self, port):
		self.buttons = {}

		self.port = port
		self.multitap = False
		self.serial = None

	def set_port(self, port):
		print('set_port:', port)
		self.port = port
		if self.serial:
			self.disable()
			self.enable()

	def enable(self):
		if self.port:
			if self.serial:
				self.disable()
			self.serial = serial.Serial(self.port, 115200)
			self.write(0xFF, 0x00, 3)
	def disable(self):
		if self.serial:
			self.serial.close()
			self.serial = None

	def button(self, controller_id, button_id, value):
		if not controller_id in self.buttons:
			self.buttons[controller_id] = [False] * SnesController.BIT_COUNT

		if self.buttons[controller_id][button_id] == value:
			return
		self.buttons[controller_id][button_id] = value

		# print('button({}, {}, {})'.format(controller_id, button_id, value))

		val = 0
		for x in range(len(self.buttons[controller_id])):
			val |= 1 if self.buttons[controller_id][x] else 0
			val <<= 1
		val >>= 1
		self.write(controller_id, val >> 8, val)

	def is_button(self, controller_id, button_id):
		if not controller_id in self.buttons:
			return False
		if not button_id in self.buttons[controller_id]:
			return False
		return self.buttons[controller_id][button_id]

	def write(self, command, h, l):
		val = bytearray([command & 0xFF, h & 0xFF, l & 0xFF])
		# print(repr(val))
		if self.serial and self.serial.isOpen():
			self.serial.write(val)

	def toggle_multitap(self):
		self.multitap = not self.multitap
		self.write(0xFF, 0x01, 1 if self.multitap else 0)

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