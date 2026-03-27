#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>

#define TRIG 14
#define ECHO 27
#define RELAY 26
#define CUR_PIN 34

LiquidCrystal_I2C lcd(0x27, 16, 2);

// 🔥 WIFI
const char* ssid = "Kavish's Galaxy S21 FE 5G";
const char* password = "jtlh7880";

// 🔥 Replace IP
const char* serverData = "http://10.24.180.2:5000/api/data";
const char* serverControl = "http://10.24.180.2:5000/api/control";

const int DIST_TH = 10;
const unsigned long AUTO_CUTOFF = 60000;

unsigned long absentStart = 0;
bool loadOn = true;


// ---------------- DISTANCE ----------------
long getDist() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  long duration = pulseIn(ECHO, HIGH, 30000);
  return duration * 0.034 / 2;
}


// ---------------- CURRENT ----------------
float readCurrent() {
  float val = analogRead(CUR_PIN);
  return val / 100.0; // safe approximation
}


// ---------------- SEND DATA ----------------
void sendData(float usage, bool occupied) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(serverData);
    http.addHeader("Content-Type", "application/json");

    String json = "{\"usage\": " + String(usage) +
                  ", \"occupied\": " + (occupied ? "true" : "false") + "}";

    http.POST(json);
    http.end();
  }
}


// ---------------- GET CONTROL ----------------
bool manualCut() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(serverControl);
    int code = http.GET();

    if (code == 200) {
      String payload = http.getString();
      if (payload.indexOf("true") != -1) return true;
    }

    http.end();
  }
  return false;
}


// ---------------- SETUP ----------------
void setup() {
  Serial.begin(115200);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  pinMode(RELAY, OUTPUT);

  digitalWrite(RELAY, HIGH);

  lcd.init();
  lcd.backlight();

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }

  Serial.println("WiFi Connected");
}


// ---------------- LOOP ----------------
void loop() {

  // 🔥 MANUAL OVERRIDE
  if (manualCut()) {
    digitalWrite(RELAY, LOW);
    lcd.clear();
    lcd.print("MANUAL CUT OFF");
    delay(1000);
    return;
  }

  long d = getDist();
  bool occupied = (d > 0 && d <= DIST_TH);

  float usage = readCurrent();
  if (usage < 0.1) usage = 0;

  if (occupied) {
    absentStart = 0;
    digitalWrite(RELAY, HIGH);

    lcd.clear();
    lcd.print("Occupied");
  }
  else {
    if (!absentStart) absentStart = millis();

    unsigned long elapsed = millis() - absentStart;

    lcd.clear();
    lcd.print("Empty: ");
    lcd.print(elapsed / 1000);
    lcd.print("s");

    // 🔥 AUTO CUTOFF (SAFE)
    if (elapsed >= AUTO_CUTOFF) {
      digitalWrite(RELAY, LOW);
      lcd.clear();
      lcd.print("AUTO CUT OFF");
    }
  }

  sendData(usage, occupied);

  delay(1000);
}