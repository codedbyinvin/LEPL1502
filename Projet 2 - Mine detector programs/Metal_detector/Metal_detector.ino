#include <TimeLib.h>
#include <FastLED.h>


// CONSTANTS //
#define TIMER 500
#define NUM_LEDS_CAR 44
#define CAR_PIN 10
#define BRIGHTNESS 50
#define SENSOR_PIN A0
#define OUPTUT_PIN 2

// VARIABLES //

// LEDs
CRGB car_leds[NUM_LEDS_CAR];

// Other
bool start = true;
long t_high;
float val;
long current_time;
bool state = false;

float color;

void setup() {
  Serial.begin(9600);
  FastLED.addLeds<WS2812B, CAR_PIN, GRB>(car_leds, NUM_LEDS_CAR);
  FastLED.clear();
  FastLED.setBrightness(BRIGHTNESS);
}

void loop() {

  //Detect spikes
  val = analogRead(SENSOR_PIN);
  current_time = millis();
  if (val > 50) {
    state = true;
    t_high = millis();
  } else if (state && val < 50 && current_time - t_high > TIMER) {
    state = false;
  }


  //Indicator : LED animation + digitalWrite
  if (state) {
    digitalWrite(OUPTUT_PIN, state);
    LED_indicator();
  } else {
    fill_solid(car_leds, NUM_LEDS_CAR, CRGB::Green);
    FastLED.show();
  }

  if (start) {
    start = false;
    Serial.println("Starting UP");
    startup_animation();
    delay(100);
  }
}


void startup_animation() {
  fill_solid(car_leds, NUM_LEDS_CAR, CRGB::Red);
  FastLED.show();
  delay(1000);
  int timer = 10;
  for (int i = 0; i < int(NUM_LEDS_CAR / 2); i++) {
    for (int j = int(NUM_LEDS_CAR / 2); j >= i; j--) {
      car_leds[j] = CRGB::Green;
      car_leds[NUM_LEDS_CAR - j - 1] = CRGB::Green;
      FastLED.show();
      car_leds[j] = CRGB::Red;
      car_leds[NUM_LEDS_CAR - j - 1] = CRGB::Red;
      delay(timer);
    }
    fill_solid(car_leds, i + 1, CRGB::Green);
    fill_solid(car_leds + NUM_LEDS_CAR - i - 1, i + 1, CRGB::Green);
    FastLED.show();
    delay(5 * timer);
    if (timer > 5) {
      timer--;
    }
  }
}


//Animation for the LED strip
void LED_indicator() {
  fill_solid(car_leds, NUM_LEDS_CAR, CRGB::Red);
  FastLED.show();
}