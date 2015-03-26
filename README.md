# snes_controller_emulator
Emulate a SNES controller and multitap.

Initial version supports 3 controller perfectly, and the 4th (and probably 5th) have a kinda functioning B button.

=== Hooking it up ===
Requires a Teensy 3.1 (3.0 is not recommended because it's not 5V tolerant, but it might work since all the outputs seem to be open collector).

Hook up from pin 2 in this order:
Port 1:
	2 (Clock)
	3 (Latch)
	4 (Data0)
Port2:
	2 (Clock)
	3 (Latch)
	4 (Data0)
	5 (Data1)
	6 (PP)

Make sure either controller has the ground connected too.

How I did it is: I bought 2 extension cables. In port 1 i just left the pins how they are.
On port 2 I moved the 5V and GND pin (1 and 7) to Data1 and PP (5 and 6). Due to the ground of port 1 being connected you don't have to connect it and thus only have to do a minor modification on the cable.

Everything else is handled by the Teensy itself, including the required pull-ups.

=== PC Side ===
This requires python 2 with pygame.
Run:
    python2 main.py /dev/ttyACM[0-9]
where you add the number your Teensy is connected to at the end.

Currently there's a nasty trick in there where pressing the PS button on a Sixaxis will toggle joysticks 0 and 1 to 2 and 3. This is only for testing purposes.

It supports Sixaxis and Xbox 360 controllers currently.