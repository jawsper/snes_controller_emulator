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

volatile uint16_t buttons[5] = { 0, 0, 0, 0, 0 };//~BUTTON_MASK;
volatile uint16_t bits[5] = { 0, 0, 0, 0, 0 };

#define MULTITAP 1
#ifdef MULTITAP
volatile bool multitap = true;
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

	// enable interrupts for port 1
	attachInterrupt(PIN_2_LATCH, isr_on_1_latch, CHANGE);
	// attachInterrupt(PIN_1_LATCH, isr_on_1_latch_falling, FALLING);
	attachInterrupt(PIN_2_CLOCK, isr_on_1_clock, RISING);

#ifdef MULTITAP
	attachInterrupt(PIN_2_PP, isr_on_pp, FALLING);
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
		uint8_t controller = Serial.read();
		uint8_t high = Serial.read();
		uint8_t low = Serial.read();
		// special command
#ifdef MULTITAP
		if(controller == 0xFF)
		{
			multitap = low == 1 ? true : false;
		}
		else //if(controller < 5)
#endif
		{
			buttons[controller] = ((high << 8) | low) & BUTTON_MASK;			
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
	bits[0] = 0x8000;
	bits[1] = 0x8000;
#ifdef MULTITAP
	bits[2] = 0x8000;
	// if(multitap)
	// {
	// 	digitalWrite(PIN_2_DATA1, LOW);
	// }
#endif
	on_1_clock();
}
// void isr_on_2_latch()
// {
// 	// if(digitalRead(PIN_2_LATCH) == HIGH)
// 	// {
// 		bits[1] = 0x8000;
// 	// 	if(multitap)
// 	// 	{
// 	// 		digitalWrite(PIN_2_DATA1, LOW);
// 	// 		for(int i = 2; i < 5; i++) bits[i] = 0x8000;
// 	// 	}
// 	// }
// 	// else
// 	// {
// 	// 	if(multitap) digitalWrite(PIN_2_DATA1, HIGH);
// 		on_2_clock();
// 	// }
// }

void isr_on_1_latch_rising()
{
	if(!multitap) return;
	digitalWrite(PIN_2_DATA1, LOW);
}

#ifdef MULTITAP
// pp functions as latch for 3 + 4
void isr_on_pp()
{
	if(!multitap) return;
	bits[3] = 0x8000;
	set_output(PIN_2_DATA0, 3);
	bits[4] = 0x8000;
	on_1_clock();
}
#endif

void isr_on_1_clock()
{
	if(digitalRead(PIN_1_LATCH) == HIGH) return;
	on_1_clock();
}
// void isr_on_2_clock()
// {
// 	if(digitalRead(PIN_2_LATCH) == HIGH) return;
// 	on_2_clock();
// }

inline void on_1_clock()
{
	set_output(PIN_1_DATA0, 0);
	bits[0] >>= 1;

#ifdef MULTITAP
	uint8_t data0, data1;
	if(!multitap || digitalRead(PIN_2_PP) == HIGH)
	{
		data0 = 1;
		data1 = 2;
	}
	else
	{
		data0 = 3;
		data1 = 4;
	}

	set_output(PIN_2_DATA0, data0);
	bits[data0] >>= 1;
	// if(multitap && data0 == 1 && bits[data0] == 0)
	// {
	// 	bits[3] = 0x8000;
	// 	set_output(PIN_2_DATA0, 3);
	// }
	if(data1 != 2 || digitalRead(PIN_1_LATCH) == LOW)
	{
		set_output(PIN_2_DATA1, data1);
		bits[data1] >>= 1;
	}

#else
	set_output(PIN_2_DATA0, 1);
	bits[1] >>= 1;
#endif
}

// inline void on_2_clock()
// {
// 	// if(multitap) digitalWrite(PIN_2_DATA1, HIGH);
// 	// if(multitap)
// 	// {
// 	// 	uint8_t data0, data1;
// 	// 	if(digitalRead(PIN_2_PP) == HIGH)
// 	// 	{
// 	// 		data0 = 1;
// 	// 		data1 = 2;
// 	// 	}
// 	// 	else
// 	// 	{
// 	// 		data0 = 3;
// 	// 		data1 = 4;
// 	// 	}
// 	// 	if(bits[data0] == 0 || bits[data1] == 0) return;
// 	// 	set_output(PIN_2_DATA0, data0);
// 	// 	set_output(PIN_2_DATA1, data1);
// 	// 	bits[data0] >>= 1;
// 	// 	bits[data1] >>= 1;
// 	// }
// 	// else
// 	// {
// 		if(bits[1] == 0) return;
// 		set_output(PIN_2_DATA0, 1);
// 		bits[1] >>= 1;
// 	// }
// 	// on_clock(1);
// }

inline void set_output(uint8_t pin, uint8_t port)
{
	uint16_t output = buttons[port] & bits[port];
	digitalWrite(pin, output != 0 ? LOW : HIGH);
}