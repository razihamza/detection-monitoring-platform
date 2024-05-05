#include "DHT.h"
#define DHTPIN D4
#define DHTTYPE DHT11

#include <Arduino.h>
#if defined(ESP32)
  #include <WiFi.h>
#elif defined(ESP8266)
  #include <ESP8266WiFi.h>
#endif
#include <Firebase_ESP_Client.h>

#define MQ_PIN A0 // Define the analog pin for the MQ sensor
#define RO_CLEAN_AIR_FACTOR 9.83 // Define the RO_CLEAN_AIR_FACTOR for MQ-8 sensor

#define WIFI_SSID "Razo"
#define WIFI_PASSWORD "password1"
#define API_KEY "AIzaSyDJyOSVXPr5lruuIYleatmDpfKPhH4rJNs123"
#define DATABASE_URL "https://mainproject-1ebb8-default-rtdb.firebaseio.com/"


DHT dht(DHTPIN, DHTTYPE);
float Ro = 10; // Initial value for Ro

// Firebase configuration
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;
bool signupOK = false;

// Rest of your existing code...

void calibrate() {
  Serial.println("Calibrating MQ-8 sensor...");
  delay(5000); // Allow the sensor to warm up
  
  // Read sensor value multiple times and take an average to calibrate
  int value = 0;
  for (int i = 0; i < 50; i++) {
    value += analogRead(MQ_PIN);
    delay(100);
  }
  value = value / 50;
  
  float sensor_volt = value * (3.3 / 1023.0); // Convert sensor value to voltage
  float RS_air = ((3.3 - sensor_volt) / sensor_volt); // Calculate sensor resistance in clean air
  Ro = RS_air / RO_CLEAN_AIR_FACTOR; // Calibrate Ro value
  Serial.println("Calibration complete.");
}

float readHydrogen() {
  int sensorValue = analogRead(MQ_PIN); // Read sensor value
  float sensor_volt = sensorValue * (3.3 / 1023.0); // Convert sensor value to voltage
  float RS_gas = ((3.3 - sensor_volt) / sensor_volt); // Calculate sensor resistance in gas
  
  float ratio = RS_gas / Ro; // Calculate ratio Rs/Ro
  float ppm_log = (log10(ratio) - 0.4999) / (-0.5794); // Calculate ppm using a logarithmic equation
  
  return pow(10, ppm_log); // Convert ppm_log back to ppm
}

void setup(){
  pinMode(DHTPIN, INPUT);
  dht.begin();
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  /* Assign the api key (required) */
  config.api_key = API_KEY;

  /* Assign the RTDB URL (required) */
  config.database_url = DATABASE_URL;

  /* Sign up */
  if (Firebase.signUp(&config, &auth, "", "")){
    Serial.println("ok");
    signupOK = true;
  }
  else{
    Serial.printf("%s\n", config.signer.signupError.message.c_str());
  }

  /* Assign the callback function for the long running token generation task */
  //config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  // Call calibration function to initialize the sensor
  calibrate();
}

void loop() {
  delay(1000);

  // Read DHT sensor data
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Read hydrogen concentration
  float hydrogen = readHydrogen();

  if (Firebase.ready() && signupOK) {
    // Convert float values to strings
    String humidityStr = String(h);
    String temperatureStr = String(t);
    String hydrogenStr = String(hydrogen);

    if (Firebase.RTDB.setString(&fbdo, "DHT/humidity", humidityStr)) {
      Serial.print("Humidity: ");
      Serial.println(h);
    } else {
      Serial.println("FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    if (Firebase.RTDB.setString(&fbdo, "DHT/temperature", temperatureStr)) {
      Serial.print("Temperature: ");
      Serial.println(t);
    } else {
      Serial.println("FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }

    if (Firebase.RTDB.setString(&fbdo, "Hydrogen/concentration", hydrogenStr)) {
      Serial.print("Hydrogen Concentration: ");
      Serial.println(hydrogen);
    } else {
      Serial.println("FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }
  }
  Serial.println("______________________________");
}
