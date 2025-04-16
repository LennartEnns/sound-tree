#include "Arduino.h"
#include <Adafruit_NeoPixel.h>

#define PIN            6
#define NUMPIXELS      44

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_BRG + NEO_KHZ800);

void setup() {
    // initialize LED digital pin as an output.
    pinMode(LED_BUILTIN, OUTPUT);

    Serial.begin(115200);

    pixels.begin();

    Serial.println("<ready>");
}

int hex_byte_toint(char* digits) {
    return strtol(digits, NULL, 16);
}
void receiveDataAndShow() {
    char charBuffer[6 * NUMPIXELS];
    int currentChar = 0;
    while (currentChar < 6 * NUMPIXELS) {
        while (Serial.available() < 1) {} // wait for serial input
        charBuffer[currentChar] = Serial.read();
        currentChar++;
    } // buffer the right amount of chars

    char tempData[3];
    int nextData[3];
    for (int pixel = 0; pixel < NUMPIXELS; pixel++) {
        for (int i = 0; i < 3; i++) {
            tempData[0] = charBuffer[2 * i + pixel * 6];
            tempData[1] = charBuffer[2 * i + 1 + pixel * 6];
            tempData[2] = '\0'; // just a random invalid hex character, causes strtol to cancel
        
            nextData[i] = hex_byte_toint(tempData);
        }
        
        pixels.setPixelColor(pixel, pixels.Color(nextData[0], nextData[1], nextData[2]));
    }

    pixels.show();
    //Serial.println("OK"); // messes up speed
    
}

void loop() {
    receiveDataAndShow();    
}