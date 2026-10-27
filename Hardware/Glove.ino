#define BLYNK_TEMPLATE_ID "Template id"
#define BLYNK_TEMPLATE_NAME "Sign Language Home Automation"
#define BLYNK_AUTH_TOKEN "Blynk Token"

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <LiquidCrystal_I2C.h>

char ssid[] = " Hostspot Name";
char pass[] = "Your Password";

// ---------- Hardware ----------
Adafruit_MPU6050 mpu;
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Thumb, Index, Middle, Ring, Little
const int flexPins[5] = {34, 35, 33, 32, 36};

// ---------- Virtual Appliance States ----------
bool lightState = false;
bool fanState = false;

// ---------- Sensor Timing ----------
unsigned long lastSensorRead = 0;
const unsigned long sensorInterval = 100;

// ---------- Serial Communication ----------
String serialCommand = "";

// ==========================================
// BLYNK STATUS UPDATE
// V0 = Light ON/OFF
// V1 = Fan ON/OFF
// ==========================================
void updateBlynkStatus() {

  if (!Blynk.connected()) return;

  Blynk.virtualWrite(V0, lightState ? 1 : 0);
  Blynk.virtualWrite(V1, fanState ? 1 : 0);
}

// ==========================================
// BLYNK MANUAL LIGHT SWITCH
// ==========================================
BLYNK_WRITE(V0) {
  lightState = (param.asInt() != 0);
}

// ==========================================
// BLYNK MANUAL FAN SWITCH
// ==========================================
BLYNK_WRITE(V1) {
  fanState = (param.asInt() != 0);
}

// ==========================================
// LCD STARTUP SCREEN
// ==========================================
void showStartupScreen() {

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SMART SIGN GLOVE");

  lcd.setCursor(0, 1);
  lcd.print("AI SYSTEM READY");

  delay(1500);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Waiting for sign");

  lcd.setCursor(0, 1);
  lcd.print("ML + IoT ACTIVE");
}

// ==========================================
// DISPLAY PREDICTED GESTURE
// ==========================================
void showGesture(String gesture) {

  gesture.trim();
  gesture.toLowerCase();

  if (gesture.length() == 0) return;

  // ----- Virtual Home Automation -----

  if (gesture == "light on") {
    lightState = true;
  }
  else if (gesture == "light off") {
    lightState = false;
  }
  else if (gesture == "fan on") {
    fanState = true;
  }
  else if (gesture == "fan off") {
    fanState = false;
  }

  // ----- LCD Output -----

  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("SIGN DETECTED:");

  lcd.setCursor(0, 1);

  String displayGesture = gesture;
  displayGesture.toUpperCase();

  if (displayGesture.length() > 16) {
    displayGesture = displayGesture.substring(0, 16);
  }

  lcd.print(displayGesture);

  // ----- Blynk Output -----

  if (Blynk.connected()) {

    // V2 = Predicted Gesture
    Blynk.virtualWrite(V2, gesture);

    // Update V0 and V1
    updateBlynkStatus();
  }
}

// ==========================================
// RECEIVE ML PREDICTION FROM PYTHON
// ==========================================
void readPythonCommand() {

  while (Serial.available()) {

    char c = Serial.read();

    if (c == '\n') {

      serialCommand.trim();

      if (serialCommand.length() > 0) {
        showGesture(serialCommand);
      }

      serialCommand = "";
    }

    else if (c != '\r') {

      if (serialCommand.length() < 40) {
        serialCommand += c;
      }
      else {
        serialCommand = "";
      }
    }
  }
}

// ==========================================
// SEND SENSOR READINGS TO PYTHON
// ==========================================
void sendSensorData() {

  int flexValues[5];

  // Read all five flex sensors
  for (int i = 0; i < 5; i++) {
    flexValues[i] = analogRead(flexPins[i]);
  }

  // Read MPU6050
  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  // Send exactly 11 CSV values
  Serial.print(flexValues[0]); Serial.print(",");
  Serial.print(flexValues[1]); Serial.print(",");
  Serial.print(flexValues[2]); Serial.print(",");
  Serial.print(flexValues[3]); Serial.print(",");
  Serial.print(flexValues[4]); Serial.print(",");

  Serial.print(accel.acceleration.x); Serial.print(",");
  Serial.print(accel.acceleration.y); Serial.print(",");
  Serial.print(accel.acceleration.z); Serial.print(",");

  Serial.print(gyro.gyro.x); Serial.print(",");
  Serial.print(gyro.gyro.y); Serial.print(",");
  Serial.println(gyro.gyro.z);
}

// ==========================================
// SETUP
// ==========================================
void setup() {

  Serial.begin(115200);

  analogReadResolution(12);

  // Initialize I2C
  Wire.begin(21, 22);

  // Initialize LCD
  lcd.init();
  lcd.backlight();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SMART SIGN GLOVE");

  lcd.setCursor(0, 1);
  lcd.print("Initializing...");

  // Initialize MPU6050
  if (!mpu.begin()) {

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("MPU6050 ERROR");

    lcd.setCursor(0, 1);
    lcd.print("Check wiring");

    while (true) {
      delay(100);
    }
  }

  // MPU6050 Configuration
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  showStartupScreen();

  // Connect to Wi-Fi and Blynk
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  // Initialize virtual states
  updateBlynkStatus();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SYSTEM ONLINE");

  lcd.setCursor(0, 1);
  lcd.print("Show your sign");

  delay(1000);
}

// ==========================================
// MAIN LOOP
// ==========================================
void loop() {

  Blynk.run();

  // Receive predicted gesture from Python
  readPythonCommand();

  // Read sensors every 100 milliseconds
  unsigned long now = millis();

  if (now - lastSensorRead >= sensorInterval) {

    lastSensorRead = now;

    sendSensorData();
  }
}
