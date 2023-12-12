// 12/9に動作確認済みのただモーターを動かすだけのやつ
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <VL53L0X.h>
#include "SSD1306.h"  //ディスプレイ用ライブラリを読み込み

#define LED_BUILTIN 2

VL53L0X sensor;

String incomingStrings;  // for incoming serial data

unsigned long startTime, stopTime;

int serialLoopCount = 0;

int temp = 0;

int every50thExecution=0;

const char* ssid = "明志-2g";
const char* password = "nitttttc";
const char* python_ip = "192.168.160.68";
const int python_port = 12346;

//本体裏側　0x78に接続→0x3C 0x7A→0x3A
SSD1306 display(0x3c, 21, 22);  //SSD1306インスタンスの作成（I2Cアドレス,SDA,SCL）

WiFiUDP udp;

typedef struct {
  int PWM_channels;
  int PWM;
  int INA;
  int INB;
} dataDictionary;

const dataDictionary PIN_array[]{
  { 0, 25, 32, 33 },
  { 1, 26, 14, 27 },
  { 2, 13, 16, 17 },
};

float battery_voltage = 0;
int battery_voltage_PIN = 35;
bool low_battery_voltage = false;
float ultrasonic_sensor_right_front = 0;
const int ultrasonic_sensor_right_front_PIN = 18;
float ultrasonic_sensor_right_back = 0;
const int ultrasonic_sensor_right_back_PIN = 19;
float ultrasonic_sensor_left_back = 0;
const int ultrasonic_sensor_left_back_PIN = 23;
int tof_sensor = 0;

String jsonString = "{}"

void setup(){
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(battery_voltage_PIN, INPUT);

  Serial.begin(921600);

  display.init();                     //ディスプレイを初期化
  display.setFont(ArialMT_Plain_16);  //フォントを設定

  // Wire.begin();

  // sensor.init();
  // sensor.setTimeout(100);
  // sensor.startContinuous(10);

  delay(1000);

  connectToWiFi();

  for (int i = 0; i < 3; i++) {
    //INA,INBの設定
    pinMode(PIN_array[i].INA, OUTPUT);
    pinMode(PIN_array[i].INB, OUTPUT);
    //PWM初期化
    ledcSetup(PIN_array[i].PWM_channels, 10000, 8);  // PWM 周波数: 10kHz 8bit
    ledcAttachPin(PIN_array[i].PWM, PIN_array[i].PWM_channels);
  }
}

void connectToWiFi() {
  Serial.println("Connecting to WiFi");
  display.drawString(15, 0, "Connect WiFi");
  display.display();  //指定された情報を描画
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP address:");
  Serial.println(WiFi.localIP());
  udp.begin(12345);  // Choose any available local port
  display.setFont(ArialMT_Plain_24);
  display.drawString(25, 40, String(WiFi.localIP()[2]) + "." + String(WiFi.localIP()[3]));
  display.display();  //指定された情報を描画
}


void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char packetData[255];
    udp.read(packetData, sizeof(packetData));
    packetData[packetSize] = '\0';  // 文字列の終端を追加

    // 受信したデータを変数に保存
    String json = String(packetData);

    Serial.print("Received data: ");
    Serial.print(json);

    // udp.beginPacket(python_ip, python_port);
    // udp.print(json);
    // udp.endPacket();

    startTime = micros();

    // json = "{'motor1':{'speed':-128},'motor2':{'speed':-128},'motor3':{'speed':-128},'motor4':{'speed':-128}}";

    // JSON用の固定バッファを確保。
    StaticJsonDocument<300> doc;  // deserializeJson() failed: NoMemory とSerialで流れたらここの値を大きくする

    // Deserialize the JSON document
    DeserializationError error = deserializeJson(doc, json);

    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.f_str());
      return;
    }
    if (doc.containsKey("motor1")) {
      // Serial.println(String(doc["motor1"]["speed"].as<float>()));
      PWM(1, doc["motor1"]["speed"]);
      analogWrite(LED_BUILTIN, abs(int(doc["motor1"]["speed"])));
    }
    if (doc.containsKey("motor2")) {
      // Serial.println(String(doc["motor2"]["speed"].as<float>()));
      PWM(2, doc["motor2"]["speed"]);
    }
    if (doc.containsKey("motor3")) {
      // Serial.println(String(doc["motor3"]["speed"].as<float>()));
      PWM(3, doc["motor3"]["speed"]);
    }
    if (doc.containsKey("motor4")) {
      // Serial.println(String(doc["motor4"]["speed"].as<float>()));
      PWM(4, doc["motor4"]["speed"]);
    }

    // const char* motor1 = doc["motor1"];

    stopTime = micros();
    // Serial.print(stopTime - startTime);
    // Serial.println("us");
  }

  every50thExecution += 1;
  if (every50thExecution > 47){
      every50thExecution = 0;
    // 電圧監視
    battery_voltage = analogRead(35) * 4.034 * 3.3 / 4096;
    if (battery_voltage < 9) {
      low_battery_voltage = true;
      // digitalWrite(23, HIGH);
    } else if (battery_voltage < 10) {
      low_battery_voltage = false;
      // ブザーを鳴らす
      // digitalWrite(23, HIGH);
    } else {
      low_battery_voltage = false;
      // digitalWrite(23, LOW);
    }

    udp.beginPacket(python_ip, python_port);
    jsonString = "{\"battery_voltage\":" + String(battery_voltage, 2) + "}";
    udp.print(jsonString);
    udp.endPacket();

    // WiFiが途切れたら再接続する
    if (WiFi.status() != WL_CONNECTED) {
      connectToWiFi();
    }
  }

  if (low_battery_voltage == true) {
    if (temp > 100) {
      for (int i = 0; i < 4; i++) {
        digitalWrite(PIN_array[i].INA, HIGH);
        digitalWrite(PIN_array[i].INB, HIGH);
      }
    }
  }

  float duration;
  pinMode(ultrasonic_sensor_right_front_PIN, OUTPUT);
  digitalWrite(ultrasonic_sensor_right_front_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ultrasonic_sensor_right_front_PIN, HIGH);
  delayMicroseconds(5);
  digitalWrite(ultrasonic_sensor_right_front_PIN, LOW);
  pinMode(ultrasonic_sensor_right_front_PIN, INPUT);
  duration = pulseIn(ultrasonic_sensor_right_front_PIN, HIGH);
  ultrasonic_sensor_right_front = duration / 58.2;
  Serial.println(ultrasonic_sensor_right_front);

  delay(1);

  pinMode(ultrasonic_sensor_right_back_PIN, OUTPUT);
  digitalWrite(ultrasonic_sensor_right_back_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ultrasonic_sensor_right_back_PIN, HIGH);
  delayMicroseconds(5);
  digitalWrite(ultrasonic_sensor_right_back_PIN, LOW);
  pinMode(ultrasonic_sensor_right_back_PIN, INPUT);
  duration = pulseIn(ultrasonic_sensor_right_back_PIN, HIGH);
  ultrasonic_sensor_right_back = duration / 58.2;
  Serial.println(ultrasonic_sensor_right_back);

  delay(1);

  pinMode(ultrasonic_sensor_left_back_PIN, OUTPUT);
  digitalWrite(ultrasonic_sensor_left_back_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ultrasonic_sensor_left_back_PIN, HIGH);
  delayMicroseconds(5);
  digitalWrite(ultrasonic_sensor_left_back_PIN, LOW);
  pinMode(ultrasonic_sensor_left_back_PIN, INPUT);
  duration = pulseIn(ultrasonic_sensor_left_back_PIN, HIGH);
  ultrasonic_sensor_left_back = duration / 58.2;
  Serial.println(ultrasonic_sensor_left_back);

  udp.beginPacket(python_ip, python_port);
  jsonString = "{\"ultrasonic_sensor_right_front\":" + String(ultrasonic_sensor_right_front, 2) + ",\"ultrasonic_sensor_right_back_PIN\":" + String(ultrasonic_sensor_right_back_PIN, 2) +",\"ultrasonic_sensor_left_back_PIN\":" + String(ultrasonic_sensor_left_back,2)+"}";
  udp.print(jsonString);
  udp.endPacket();

  delay(1);
}

void PWM(int motor_id, int duty) {
  if (low_battery_voltage == false) {
    temp = 0;
    if (duty == 0) {
      //VCCブレーキ
      digitalWrite(PIN_array[motor_id - 1].INA, HIGH);
      digitalWrite(PIN_array[motor_id - 1].INB, HIGH);
    } else if (duty > 0) {
      // 正転
      digitalWrite(PIN_array[motor_id - 1].INA, HIGH);
      digitalWrite(PIN_array[motor_id - 1].INB, LOW);
    } else if (duty < 0) {
      // 逆転
      digitalWrite(PIN_array[motor_id - 1].INA, LOW);
      digitalWrite(PIN_array[motor_id - 1].INB, HIGH);
    }
    ledcWrite(PIN_array[motor_id - 1].PWM_channels, abs(duty));
  } else {
    temp = temp +1;
    if (temp > 100) {
      for (int i = 0; i < 4; i++) {
        digitalWrite(PIN_array[i].INA, HIGH);
        digitalWrite(PIN_array[i].INB, HIGH);
      }
    }
  }
}