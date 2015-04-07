TARGET=padled
INPUT=padled.c xpadled.c sixled.c
PREFIX=/usr/bin

program: $(INPUT)
	gcc -std=gnu99 -Wall -o $(TARGET) -ludev $(INPUT)

install: $(TARGET)
	cp $(TARGET) $(PREFIX)
	chown root:root $(PREFIX)/$(TARGET)
	chmod u+s $(PREFIX)/$(TARGET)

clean:
	rm -f $(TARGET)