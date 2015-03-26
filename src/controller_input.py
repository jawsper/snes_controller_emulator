from nintendo_output import SnesController

class InputDevice:
	pass
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
		11: SnesController.BUTTON_LEFT,
		12: SnesController.BUTTON_RIGHT,
		13: SnesController.BUTTON_UP,
		14: SnesController.BUTTON_DOWN,
	}
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
		5: SnesController.BUTTON_RIGHT,
		6: SnesController.BUTTON_DOWN,
		7: SnesController.BUTTON_LEFT,

		16: -1,
	}

devices = [XBoxController, PS3Controller]