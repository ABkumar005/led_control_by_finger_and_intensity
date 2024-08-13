const int ledPins[] = {2, 3, 4, 5};  // Pins for the four LEDs
const int numLeds = 4;

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT);
  }
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming string from serial
    String data = Serial.readStringUntil('\n');
    
    // Split the data into four intensity values
    int ledIntensities[numLeds];
    int index = 0;
    int value = 0;
    for (char c : data) {
      if (c == ',') {
        ledIntensities[index++] = value;
        value = 0;
      } else {
        value = value * 10 + (c - '0');
      }
    }
    if (index < numLeds) {
      ledIntensities[index] = value;
    }

    // Write the intensity values to the LEDs
    for (int i = 0; i < numLeds; i++) {
      analogWrite(ledPins[i], ledIntensities[i]);
    }
  }
}
