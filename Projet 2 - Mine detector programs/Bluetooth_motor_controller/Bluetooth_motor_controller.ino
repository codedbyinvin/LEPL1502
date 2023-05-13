#include <SoftwareSerial.h>


// PINS DEFINITION //
SoftwareSerial BTSerial(10, 11);  // RX | TX
#define ENA 6
#define IN1 2
#define IN2 3
#define IN3 4
#define IN4 5
#define ENB 9

#define INPUT_PIN 12

//VARIABLES//
#define MAX_SPEED 255
float left_speed = 0.0;
float right_speed = 0.0;



void setup() {
  Serial.begin(9600);
  BTSerial.begin(9600);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}

void loop() {
  if (BTSerial.available()) {
    read_data(&left_speed, &right_speed);
  } 
  control_motors(right_speed, left_speed);

  bool state = digitalRead(INPUT_PIN) == 1 ? true : false;
  if(state){
    BTSerial.println("metal detected");
  }
}

void read_data(float* left, float* right) {
  String data = BTSerial.readStringUntil('\n');
  int spaceIndex = data.indexOf(' ');
  if (spaceIndex != -1) {
    String float1String = data.substring(0, spaceIndex);
    String float2String = data.substring(spaceIndex + 1);
    *left = float1String.toFloat();
    *right = float2String.toFloat();
  }
}

void control_motors(float L, float R) {
  //LEFT MOTORS

  //RIGHT MOTORS
  if (R < 0) {
    digitalWrite(IN3, 0);
    digitalWrite(IN4, 1); 
  } else if (R > 0) {
    digitalWrite(IN3, 1);
    digitalWrite(IN4, 0);
  } else {
    digitalWrite(IN3, 0);
    digitalWrite(IN4, 0);
  }
  analogWrite(ENB, map(abs(R), 0, 100, 0, MAX_SPEED));

  if (L < 0) {
    digitalWrite(IN1, 0);
    digitalWrite(IN2, 1);
  } else if (L > 0) {
    digitalWrite(IN1, 1);
    digitalWrite(IN2, 0);
  } else {
    digitalWrite(IN1, 0);
    digitalWrite(IN2, 0);
  }
  analogWrite(ENA, map(abs(L), 0, 100, 0, MAX_SPEED));
}
