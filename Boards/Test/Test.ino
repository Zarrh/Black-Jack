#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "IoT_Casino"; // Network name
const char* password = "AceOfSpades"; // Network password

const String IPServer = "192.168.4.3"; // Central server IP
const String PortServer = "5555";

const unsigned int positions[3] = {1, 2, 3};
bool positions_ready[3] = {false, false, false};
int pots[3] = {0, 0, 0};
int bets[3] = {0, 0, 0};
const unsigned int leftButtons[3] = {21, 21, 21};
const unsigned int centerButtons[3] = {19, 19, 19};
const unsigned int rightButtons[3] = {18, 18, 18};

const unsigned int step = 10;

unsigned int mode = 0; // Part of the hand
unsigned int turn = 0; // Player's turn
bool next;
bool potsReceived = false;

String get_request(String url)
{
  WiFiClient client;
  HTTPClient http;
    
  http.begin(client, url);
    
  int httpResponseCode = http.GET();
  
  String payload = "{}"; 
  
  if (httpResponseCode > 0) 
  {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    payload = http.getString();
  }
  else 
  {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }

  http.end();

  return payload;
}

bool post_request(String url, String payload)
{
  if (WiFi.status() == WL_CONNECTED) 
  {
    HTTPClient http;
    WiFiClient client;

    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) 
    {
      Serial.print("Server's response: ");
      Serial.println(http.getString());
      http.end();
      if (httpResponseCode == 200) 
      {
        return 1;
      }
      return 0;
    } 
    else 
    {
      Serial.print("Error during connection: ");
      Serial.println(httpResponseCode);
      http.end();
      return 0;
    }
  }
}

void fill_from_json(int* a, String jsonString, String objKey)
{
  StaticJsonDocument<256> jsonDocument;

  DeserializationError error = deserializeJson(jsonDocument, jsonString);

  if (error) 
  {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }

  JsonArray Array = jsonDocument[objKey];

  if (Array.size() == 3) 
  {
    for (int i = 0; i < 3; i++) 
    {
      a[i] = Array[i];
    }
  } 
  else 
  {
    Serial.println("Error: array size not correct");
  }
}

int json_to_int(String jsonString, String objKey)
{
  StaticJsonDocument<256> jsonDocument;

  DeserializationError error = deserializeJson(jsonDocument, jsonString);

  if (error) 
  {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return -1;
  }

  return jsonDocument[objKey];
}

void manage_first_bet(unsigned int minusButton, unsigned int enterButton, unsigned int plusButton, unsigned int ID)
{

  static bool started = false;

  static unsigned long t0 = 0;
  unsigned long t = millis(); // Timer

  bool minusState = digitalRead(minusButton);
  bool enterState = digitalRead(enterButton);
  bool plusState = digitalRead(plusButton);
  static bool lastMinusState = 0;
  static bool lastEnterState = 0;
  static bool lastPlusState = 0;
  Serial.println(digitalRead(minusButton));
  Serial.println(digitalRead(enterButton));
  Serial.println(digitalRead(plusButton));

  if (enterState == 1 && lastEnterState == 0 && !started)
  {
    started = true;
    t0 = t; // Start game and reset timer
  }

  if (started)
  {

    if (plusState == 1 && lastPlusState == 0 && pots[ID] - step >= 0)
    {     
      bets[ID] += step;
      pots[ID] -= step;
    }
    if (minusState == 1 && lastMinusState == 0 && bets[ID] - step >= 0)
    {
      bets[ID] -= step;
      pots[ID] += step;
    }
    if (enterState == 1 && lastEnterState == 0 && t - t0 > 5000)
    {
      positions_ready[ID] = true; // Confirm the bet
      Serial.print("Confirm"); // Debug
      return;
    }
    lastMinusState = minusState;
    lastEnterState = enterState;
    lastPlusState = plusState;

    //Serial.println(pots[ID]);
    //Serial.println(bets[ID]);
  }

  delay(1);
}

void manage_game(unsigned int splitButton, unsigned int passButton, unsigned int doubleButton, unsigned int ID)
{

  unsigned long t = millis(); // Timer
  static unsigned long t0 = t;

  bool splitState = digitalRead(splitButton);
  bool passState = digitalRead(passButton);
  bool doubleState = digitalRead(doubleButton);

  if (splitState == 1 && t - t0 > 2000)
  {
    turn += 1;
    return;
  }
  if (passState == 1 && t - t0 > 2000)
  {
    positions_ready[ID] = true; // Pass
    turn += 1;
    Serial.print("Pass"); // Debug
    return; 
  }
  if (doubleState == 1 && t - t0 > 2000)
  {
    positions_ready[ID] = true; // Pass
    turn += 1;
    return;
  }

  delay(1);
}

void setup() 
{
  Serial.begin(115200);

  for (int i = 0; i < 3; i++)
  {
    pinMode(leftButtons[i], INPUT_PULLUP);
    pinMode(centerButtons[i], INPUT_PULLUP);
    pinMode(rightButtons[i], INPUT_PULLUP);
  }

  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to IoT Casino with IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() 
{
  Serial.print(digitalRead(leftButtons[0]));

  delay(100);
}