const int ledPins[4] = {2, 3, 4, 5};  // Pins where LEDs are connected

void setup() {
  Serial.begin(9600);
  
  // Initialize LED pins as output
  for (int i = 0; i < 4; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }
}

void loop() {
  if (Serial.available() > 0) {
    int fingerCount = Serial.parseInt();
    
    // Debugging output
    Serial.print("Received fingers count: ");
    Serial.println(fingerCount);
    
    // Ensure the finger count is within the range [0, 4]
    fingerCount = constrain(fingerCount, 0, 4);
    
    // Turn LEDs on or off based on the number of fingers
    for (int i = 0; i < 4; i++) {
      if (i < fingerCount) {
        digitalWrite(ledPins[i], HIGH);
      } else {
        digitalWrite(ledPins[i], LOW);
      }
    }
  }
}
