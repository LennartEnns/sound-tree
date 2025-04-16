#include "Arduino.h"
#include <Adafruit_NeoPixel.h>

#define PIN             6
#define NUMPIXELS       44
#define WAIT_MAX_MS     10000

#define CYCLE_SPEED_MS   500
#define SNAKE_SPEED_MS  200

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_BRG + NEO_KHZ800);

void setup() {
    // initialize LED digital pin as an output.
    pinMode(LED_BUILTIN, OUTPUT);

    Serial.begin(1000000);

    pixels.begin();

    Serial.println("<ready>");

}

long lastAnimation = 0;
uint32_t cycle_colors[] = {pixels.Color(255,255,0), pixels.Color(0,255,255), pixels.Color(255,0,255)};
int cycle = 0;
void cycleAnimation() {
    if (millis() - lastAnimation > CYCLE_SPEED_MS) {
        for (int i = 0; i < NUMPIXELS; i++) {
            pixels.setPixelColor(i, cycle_colors[(i + cycle) % 3]);
        }
        pixels.show();

        lastAnimation = millis();
        cycle++;
    }
}

int direction = 0;
int colorSelect = 0;
void snakeAnimation() {
    if (millis() - lastAnimation > SNAKE_SPEED_MS) {
        if (direction == 0) {
            for (int i = 0; i < NUMPIXELS; i++) {
                pixels.setPixelColor(i, pixels.Color(0,0,0));
            }
            direction = 1;
            cycle = 0;
        }

        if (direction > 0) {
            pixels.setPixelColor(cycle, cycle_colors[colorSelect]);
        } else {
            pixels.setPixelColor(cycle, pixels.Color(0,0,0));
        } 

        pixels.show();

        cycle+= direction;
        if (cycle > NUMPIXELS) {
            direction = -1;
        } else if (cycle < 0) {
            direction = 1;
        }

        lastAnimation = millis();
    }
}

int animationSelected = 0;

void playAnimation() {
    switch (animationSelected) {
        case 0: cycleAnimation(); break;
        
        case 1: snakeAnimation(); break;
    }
}

int hex_byte_toint(char* digits) {
    return strtol(digits, NULL, 16);
}
void receiveDataAndShow() {
    uint8_t charBuffer[3 * NUMPIXELS];
    int currentChar = 0;
    long waitStart = millis();
    animationSelected = (animationSelected + 1) % 2;
    while (currentChar < 3 * NUMPIXELS) {
        while (Serial.available() < 1) {
            if (millis() - waitStart > WAIT_MAX_MS) {
                playAnimation(); // play animation if we don't receive anything
            }
        } // wait for serial input
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