// sudo arduino-cli upload -p *PORT* --fqbn esp32:esp32:esp32 Table.ino

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "IoT_Casino"; // Network name
const char* password = "AceOfSpades"; // Network password

const String IPServer = "192.168.4.11"; // Central server IP
const String PortServer = "5555";

const unsigned int positions[3] = {1, 2, 3};
bool positions_ready[3] = {false, false, false};
int pots[3] = {0, 0, 0};
int bets[3] = {0, 0, 0};
const unsigned int leftButtons[3] = {23, 23, 23};
const unsigned int centerButtons[3] = {19, 19, 19};
const unsigned int rightButtons[3] = {18, 18, 18};

bool lastLeftStates[3] = {1, 1, 1};
bool lastCenterStates[3] = {1, 1, 1};
bool lastRightStates[3] = {1, 1, 1};

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
    //Serial.print("HTTP Response code: ");
    //Serial.println(httpResponseCode);
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
      //Serial.print("Server's response: ");
      //Serial.println(http.getString());
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

  Serial.println(ID);
  Serial.print("1: ");
  Serial.print(minusState);
  Serial.print(" 2: ");
  Serial.print(enterState);
  Serial.print(" 3: ");
  Serial.print(plusState);
  Serial.println();

  if (enterState == 0 && lastCenterStates[ID] == 1 && !started)
  {
    started = true;
    Serial.println("Started"); // Debug
    t0 = t; // Start game and reset timer
  }

  if (started)
  {

    if (plusState == 0 && lastRightStates[ID] == 1 && pots[ID] - step >= 0)
    {     
      bets[ID] += step;
      pots[ID] -= step;
    }
    if (minusState == 0 && lastLeftStates[ID] == 1 && bets[ID] - step >= 0)
    {
      bets[ID] -= step;
      pots[ID] += step;
    }
    if (enterState == 0 && lastCenterStates[ID] == 1 && t - t0 > 5000)
    {
      positions_ready[ID] = true; // Confirm the bet
      Serial.print("Confirm"); // Debug
      return;
    }
    lastLeftStates[ID] = minusState;
    lastCenterStates[ID] = enterState;
    lastRightStates[ID] = plusState;

    Serial.println(pots[ID]);
    Serial.println(bets[ID]);
  }

  delay(1);
}

void manage_game(unsigned int splitButton, unsigned int passButton, unsigned int doubleButton, unsigned int ID)
{

  if (turn == ID)
  {
    unsigned long t = millis(); // Timer
    static unsigned long t0 = t;

    bool splitState = digitalRead(splitButton);
    bool passState = digitalRead(passButton);
    bool doubleState = digitalRead(doubleButton);

    if (splitState == 0 && lastRightStates[ID] == 1 && t - t0 > 2000)
    {
      turn++;
      Serial.println("Split"); // Debug
      return;
    }
    if (passState == 0 && lastCenterStates[ID] == 1 && t - t0 > 2000)
    {
      turn++; // Pass
      Serial.println("Pass"); // Debug
      return; 
    }
    if (doubleState == 0 && lastLeftStates[ID] == 1 && t - t0 > 2000)
    {
      pots[ID] -= bets[ID];
      bets[ID] += bets[ID];
      Serial.println("Double"); // Debug
      turn++; // Pass
      return;
    }
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
  switch (mode)
  {
    case 0:
      Serial.print("1: ");
      Serial.print(digitalRead(leftButtons[0]));
      Serial.print(" 2: ");
      Serial.print(digitalRead(centerButtons[0]));
      Serial.print(" 3: ");
      Serial.print(digitalRead(rightButtons[0]));
      Serial.println();
      next = true;
      if (!potsReceived) 
      {
        potsReceived = true;
        post_request("http://" + IPServer + ":" + PortServer + "/get-mode", "{\"data\": 0}");
        fill_from_json(pots, get_request("http://" + IPServer + ":" + PortServer + "/send-pots"), "pots");
        for (int i = 0; i < 3; i++)
        {
          if (pots[i] == 0)
          {
            potsReceived = false;  
          }
        }
      }
      else 
      {
        for (int i = 0; i < 3; i++)
        {
          manage_first_bet(leftButtons[i], centerButtons[i], rightButtons[i], i);
          if (!positions_ready[i])
          {
            next = false;
          }
        }
        if (next)
        {
          mode = 1; // Start the game
          Serial.println("Start");
          for (int j = 0; j < 3; j++)
          {
            positions_ready[j] = false;
          }
        }
      }
      post_request("http://" + IPServer + ":" + PortServer + "/get-pots", "{\"pots\": {\"1\": " + String(pots[0]) + ", \"2\": " + String(pots[1]) + ", \"3\": " + String(pots[2]) + "}}");
      post_request("http://" + IPServer + ":" + PortServer + "/get-bets", "{\"bets\": {\"1\": " + String(bets[0]) + ", \"2\": " + String(bets[1]) + ", \"3\": " + String(bets[2]) + "}}");
      break;
    case 1:
      post_request("http://" + IPServer + ":" + PortServer + "/get-mode", "{\"data\": 1}");
      for (unsigned int i = 0; i < 3; i++)
      {
        manage_game(leftButtons[i], centerButtons[i], rightButtons[i], i);
      }
      if (turn >= 3)
      {
        if (post_request("http://" + IPServer + ":" + PortServer + "/get-mode", "{\"data\": 2}"))
        {
          mode = 2;
        }
      }
      post_request("http://" + IPServer + ":" + PortServer + "/get-pots", "{\"pots\": {\"1\": " + String(pots[0]) + ", \"2\": " + String(pots[1]) + ", \"3\": " + String(pots[2]) + "}}");
      post_request("http://" + IPServer + ":" + PortServer + "/get-bets", "{\"bets\": {\"1\": " + String(bets[0]) + ", \"2\": " + String(bets[1]) + ", \"3\": " + String(bets[2]) + "}}");
      break;
    case 2:
      mode = json_to_int(get_request("http://" + IPServer + ":" + PortServer + "/send-mode"), "mode");
      Serial.println("Wating for mode 3");
      break;
    case 3:
      mode = json_to_int(get_request("http://" + IPServer + ":" + PortServer + "/send-mode"), "mode");
      Serial.println("Wating for mode 0");
      for (int i = 0; i < 3; i++)
      {
        bets[i] = 0;
      }
      turn = 0;
      potsReceived = false;
      break;
  }

  delay(5);
}