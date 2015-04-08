# snes_controller_emulator
Emulate a SNES controller and multitap using a Teensy 3.1.

Initial version supports 3 controllers perfectly, and the 4th (and probably 5th) have a kinda functioning B button.

## Hooking it up
Requires a Teensy 3.1 (do not use 3.0, the PP pin is NOT open-collector).

Hook up from Teensy pin 2 up to pin 9 in this order:
* Port 1:
  * 2 (Clock)
  * 3 (Latch)
  * 4 (Data0)
* Port2:
  * 2 (Clock)
  * 3 (Latch)
  * 4 (Data0)
  * 5 (Data1)
  * 6 (PP)

Make sure either controller has the ground connected too.

How I recommend connecting it: 

Buy 2 extension cables. In port 1 leave the pins how they are.
On port 2 move the 5V and GND pin (1 and 7) to Data1 and PP (5 and 6).
Due to the ground of port 1 being connected you don't have to connect it and thus only have to do a minor modification on the cable.

Everything else is handled by the Teensy itself, including the required pull-ups.

## PC Side
This requires python (2 or 3).

Dependencies are: pygame, pyserial, pyudev

Run:
```
python main.py
```
Teensy and joysticks will be auto-detected.

When you press the centre button on the controller, you switch to "control mode", after which you can switch player with the DPAD (1, 2, 3, 4 -> U L D R); and toggle multitap on/off with SNES B.

It supports Dualshock 3 and Xbox 360 controllers currently.
