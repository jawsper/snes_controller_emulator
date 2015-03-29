//snes_controller_emu.ino

#define PIN_1_CLOCK 2
#define PIN_1_LATCH 3
#define PIN_1_DATA0 4

#define PIN_2_CLOCK 5
#define PIN_2_LATCH 6
#define PIN_2_DATA0 7
#define PIN_2_DATA1 8
#define PIN_2_PP    9

#define PIN_LED 13

#define BUTTON_MASK 0xFFF0
#define CLOCK_MAX 16

volatile int8_t clock_pulses[2] = { -1, -1 };

volatile uint32_t buttons[5] = { 0, 0, 0, 0, 0 };//~BUTTON_MASK;
volatile uint32_t bits[5] = { 0, 0, 0, 0, 0 };

#define MULTITAP
#ifdef MULTITAP
volatile bool multitap = false;
#endif

void setup() {
	pinMode(PIN_LED, OUTPUT);
	digitalWrite(PIN_LED, HIGH);

	// setup pins for port 1
	pinMode(PIN_1_CLOCK, INPUT_PULLUP);
	pinMode(PIN_1_LATCH, INPUT_PULLUP);
	pinMode(PIN_1_DATA0, OUTPUT);
	digitalWrite(PIN_1_CLOCK, HIGH);
	digitalWrite(PIN_1_LATCH, HIGH);
	digitalWrite(PIN_1_DATA0, HIGH);

	// setup pins for port 2
	pinMode(PIN_2_CLOCK, INPUT_PULLUP);
	pinMode(PIN_2_LATCH, INPUT_PULLUP);
	pinMode(PIN_2_DATA0, OUTPUT);
	digitalWrite(PIN_2_CLOCK, HIGH);
	digitalWrite(PIN_2_LATCH, HIGH);
	digitalWrite(PIN_2_DATA0, HIGH);

#ifdef MULTITAP
	pinMode(PIN_2_DATA1, OUTPUT);
	pinMode(PIN_2_PP, INPUT);
	digitalWrite(PIN_2_DATA1, HIGH);
	// digitalWrite(PIN_2_PP, HIGH);
#endif

#ifdef MULTITAP
	attachInterrupt(PIN_2_LATCH, isr_on_1_latch, CHANGE);
	attachInterrupt(PIN_2_CLOCK, isr_on_clock, RISING);

	attachInterrupt(PIN_2_PP, isr_on_pp, FALLING);
#else
	// enable interrupts for port 1
	attachInterrupt(PIN_1_LATCH, isr_on_1_latch, CHANGE);
	attachInterrupt(PIN_1_CLOCK, isr_on_clock, RISING);
#endif

	// enable interrupts for port 2
	// attachInterrupt(PIN_2_LATCH, isr_on_2_latch, CHANGE);
	// attachInterrupt(PIN_2_CLOCK, isr_on_2_clock, RISING);

	Serial.begin(115200);
}

void loop()
{
	if(Serial.available() > 2)
	{
		uint8_t command = Serial.read();
		uint8_t high = Serial.read();
		uint8_t low = Serial.read();
#ifdef MULTITAP
		// special command
		if(command == 0xFF)
		{
			switch(high)
			{
				case 1: // multitap
					multitap = low == 1 ? true : false;
					break;
				case 2:
					switch(low)
					{
						case 1:
							// one only
							break;
						case 2:
							// two only
							break;
						case 3:
							// more than 2
							break;
					}
					break;
			}
		}
		else
#endif
		if(command >= 0 && command <= 5)
		{
			buttons[command - 1] = ((high << 8) | low) & BUTTON_MASK;			
		}
	}
}

void isr_on_1_latch()
{
	if(digitalRead(PIN_1_LATCH) == HIGH)
	{
		isr_on_1_latch_rising();
	}
	else
	{
		isr_on_1_latch_falling();
	}
}

void isr_on_1_latch_falling()
{
	clock_pulses[0] = 0;
	clock_pulses[1] = 0;

	bits[0] = 0x8000;
	bits[1] = 0x8000;
#ifdef MULTITAP
	bits[2] = 0x8000;
	bits[3] = 0x8000;
	bits[4] = 0x8000;
#endif
	on_clock();
}

void isr_on_1_latch_rising()
{
	set_output(PIN_1_DATA0, 0, 0x8000);
	set_output(PIN_2_DATA0, 1, 0x8000);
#ifdef MULTITAP
	if(multitap) digitalWrite(PIN_2_DATA1, LOW);
#endif
}

#ifdef MULTITAP
// pp functions as latch for 3 + 4
void isr_on_pp()
{
	if(!multitap) return;
	bits[3] = 0x8000;
	bits[4] = 0x8000;
	clock_pulses[1] = 0;
	on_clock();
}
#endif

void isr_on_clock()
{
	if(digitalRead(PIN_1_LATCH) == HIGH) return;

	bool more1 = clock_finish(PIN_1_DATA0, 0);
	bool more2 = clock_finish(PIN_2_DATA0, 1);
	if(more1 || more2)
		on_clock();
}

inline bool clock_finish(uint8_t pin, uint8_t port)
{
	if(clock_pulses[port] >= 0 && clock_pulses[port] >= CLOCK_MAX)
	{
		digitalWrite(pin, LOW);
		return false;
	}
	return true;
}

inline void on_clock()
{
	set_output(PIN_1_DATA0, 0);
	bits[0] >>= 1;

#ifdef MULTITAP
	if(multitap)
	{
		uint8_t data0, data1;

		bool pp_low = digitalRead(PIN_2_PP) == LOW;
		bool pp = multitap && pp_low;

		if(pp)
		{
			data0 = 3;
			data1 = 4;
		}
		else
		{
			data0 = 1;
			data1 = 2;
		}

		set_output(PIN_2_DATA0, data0);
		bits[data0] >>= 1;
		if(digitalRead(PIN_1_LATCH) == LOW)
		{
			set_output(PIN_2_DATA1, data1);
			bits[data1] >>= 1;
		}
	}
	else
#endif
	{
		set_output(PIN_2_DATA0, 1);
		bits[1] >>= 1;
	}

	clock_pulses[0]++;
	clock_pulses[1]++;
}

inline void set_output(uint8_t pin, uint8_t port)
{
	set_output(pin, port, bits[port]);
}
inline void set_output(uint8_t pin, uint8_t port, uint32_t bits)
{
	uint16_t output = buttons[port] & bits;
	digitalWrite(pin, output != 0 ? LOW : HIGH);
}