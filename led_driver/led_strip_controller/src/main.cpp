#include "Arduino.h"
#include <Adafruit_NeoPixel.h>

#define PIN            6
#define NUMPIXELS      44

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_BRG + NEO_KHZ800);

void setup() {
    // initialize LED digital pin as an output.
    pinMode(LED_BUILTIN, OUTPUT);

    Serial.begin(1000000);

    pixels.begin();

    Serial.println("<ready>");
}

int hex_byte_toint(char* digits) {
    return strtol(digits, NULL, 16);
}
void receiveDataAndShow() {
    uint8_t charBuffer[3 * NUMPIXELS];
    int currentChar = 0;
    while (currentChar < 3 * NUMPIXELS) {
        while (Serial.available() < 1) {} // wait for serial input
        charBuffer[currentChar] = Serial.read();
        currentChar++;
    } // buffer the right amount of chars

    for (int pixel = 0; pixel < NUMPIXELS; pixel++) {
        pixels.setPixelColor(pixel, pixels.Color(
            charBuffer[3 * pixel + 0],
            charBuffer[3 * pixel + 1],
            charBuffer[3 * pixel + 2])
        );
    }

    pixels.show();
    //Serial.println("OK"); // messes up speed
}

void loop() {
    receiveDataAndShow();    
}