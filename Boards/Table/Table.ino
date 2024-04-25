#include <WiFi.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <HTTPClient.h>
#include <WebServer.h>

void centerText(String text, int lineNumber, unsigned int size);
void text_scroll(unsigned long time, const char* text);
void text_blink(unsigned long time, const char* text);

const char* ssid = "IoT_Casino"; // Network name
const char* password = "AceOfSpades"; // Network password

const char* IPServer = "192.168.4.3"; // Central server IP

const unsigned int positions[3] = {1, 2, 3};
bool positions_ready[3] = {false, false, false};
int pots[3] = {500, 500, 500};
int bets[3] = {0, 0, 0};
const unsigned int leftButtons[3] = {14};
const unsigned int centerButtons[3] = {4};
const unsigned int rightButtons[3] = {0};

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

int pot = 500;
const unsigned int step = 10;
int bet = 0;

String startLine = "START";
unsigned int mode = 0; // Part of the hand
unsigned int turn = 0; // Player's turn
bool next;

void manage_first_bet(unsigned int minusButton, unsigned int enterButton, unsigned int plusButton, Adafruit_SSD1306 &display, unsigned int ID)
{

  static bool started = false;

  static unsigned long t0 = 0;
  unsigned long t = millis(); // Timer

  bool minusState = digitalRead(minusButton);
  bool enterState = digitalRead(enterButton);
  bool plusState = digitalRead(plusButton);

  display.clearDisplay();
  display.drawFastHLine(0, 16, 127, WHITE);

  if (enterState == 0 && !started)
  {
    started = true;
    t0 = t; // Start game and reset timer
  }

  if (!started)
  {

    text_scroll(1, "BLACK JACK");

    text_blink(20, "START");
    display.display();
  }

  else
  {
    centerText(String(pots[ID]) + '$', 4, 1);

    display.setTextSize(2);
    centerText(String(bets[ID]) + '$', 40, 1);

    if (plusState == 0 && pots[ID] - step >= 0)
    {     
      bets[ID] += step;
      pots[ID] -= step;
    }
    if (minusState == 0 && bets[ID] - step >= 0)
    {
      bets[ID] -= step;
      pots[ID] += step;
    }

    // Right circle
    int centerX1 = 104;
    int centerY1 = 40;
    int radius1 = 10;
    display.drawCircle(centerX1, centerY1, radius1, WHITE);

    int crossSize1 = 8;
    int crossThickness1 = 1;
    int crossOffset1 = crossSize1 / 2;
    display.drawLine(centerX1 - crossOffset1, centerY1, centerX1 + crossOffset1, centerY1, WHITE);
    display.drawLine(centerX1, centerY1 - crossOffset1, centerX1, centerY1 + crossOffset1, WHITE);

    // Left circle
    int centerX2 = 24;
    int centerY2 = 40;
    int radius2 = 10;
    display.drawCircle(centerX2, centerY2, radius2, WHITE);

    int crossSize2 = 8;
    int crossThickness2 = 1;
    int crossOffset2 = crossSize2 / 2;
    display.drawLine(centerX2 - crossOffset2, centerY2, centerX2 + crossOffset2, centerY2, WHITE);

    if (plusState == 0)
    {
      display.fillCircle(centerX1, centerY1, radius1, WHITE);
      display.drawLine(centerX1 - crossOffset1, centerY1, centerX1 + crossOffset1, centerY1, BLACK);
      display.drawLine(centerX1, centerY1 - crossOffset1, centerX1, centerY1 + crossOffset1, BLACK);

      display.display();
    }
    if (minusState == 0)
    {
      display.fillCircle(centerX2, centerY2, radius2, WHITE);
      display.drawLine(centerX2 - crossOffset2, centerY2, centerX2 + crossOffset2, centerY2, BLACK);

      display.display();
    }
    if (enterState == 0 && t - t0 > 5000)
    {
      positions_ready[ID] = true; // Confirm the bet
      Serial.print("Next"); // Debug
      return;
    }
  }

  display.display();
  delay(1);
}

void manage_game(unsigned int splitButton, unsigned int passButton, unsigned int doubleButton, Adafruit_SSD1306 &display, unsigned int ID)
{

  static unsigned long t0 = 0;
  unsigned long t = millis(); // Timer

  bool splitState = digitalRead(splitButton);
  bool passState = digitalRead(passButton);
  bool doubleState = digitalRead(doubleButton);

  display.clearDisplay();
  display.drawFastHLine(0, 16, 127, WHITE);

  centerText(String(pots[ID]) + '$', 4, 1);

  if (splitButton == 0)
  {
    return;
  }
  if (passButton == 0)
  {
    positions_ready[ID] = true; // Pass
    turn += 1;
    Serial.print("Pass"); // Debug
    return; 
  }
  if (doubleButton == 0)
  {
    positions_ready[ID] = true; // Pass
    turn += 1;
    return;
  }

  display.display();
  delay(1);
}

void setup() 
{
  Serial.begin(115200);

  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) 
  {
    Serial.println("Failed to init Oled display");
    for(;;); // Panic halt
  }

  for (int i = 0; i < 3; i++)
  {
    pinMode(leftButtons[i], INPUT);
    pinMode(centerButtons[i], INPUT);
    pinMode(rightButtons[i], INPUT);
  }

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.display();
  delay(2000);
  display.clearDisplay();

  /*
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
  }

  Serial.print("CONNECTED to SSID: ");
  Serial.println(ssid);
  */
}

void loop() 
{
  switch (mode)
  {
    case 0:
      next = true;
      /* For production
      for (int i = 0; i < 3; i++)
      {
        manage_first_bet(leftButtons[i], centerButtons[i], rightButtons[i], display, i);
        if (!positions_ready[i])
        {
          next = false;
        }
      }
      */
      manage_first_bet(leftButtons[0], centerButtons[0], rightButtons[0], display, 0); // TODO: remove
      if (!positions_ready[0])
      {
        next = false;
      }
      if (next)
      {
        mode = 1; // Start the game
        for (int j = 0; j < 3; j++)
        {
          positions_ready[j] = false;
        }
      }
      break;
    case 1:
      /* For production
      for (int i = 0; i < 3; i++)
      {
        if (turn == i)
        {
          manage_game(leftButtons[i], centerButtons[i], rightButtons[i], display, i);
        }
      }
      if (turn == 4)
      {
        mode = 2;
      }
      */
      manage_game(leftButtons[0], centerButtons[0], rightButtons[0], display, 0); // TODO: remove
      break;
    case 2:
      Serial.print("End");
      break;
  }

  delay(5);
}

void centerText(String text, int lineNumber, unsigned int size) 
{
  int16_t x, y;
  uint16_t textWidth, textHeight;

  display.setTextSize(size);
  display.setTextColor(WHITE);
  display.getTextBounds(text, 0, 0, &x, &y, &textWidth, &textHeight);

  int16_t startX = (SCREEN_WIDTH - textWidth) / 2;

  int16_t startY = lineNumber;

  display.setCursor(startX, startY);
  display.println(text);
}

void text_blink(unsigned long time, const char* text) 
{
  static unsigned long t0 = 0;
  static boolean state = false;

  unsigned long t = millis();

  if (t - t0 >= time) 
  {
    t0 = t;

    state = !state;

    if (state) 
    {
      centerText(text, 30, 3);
    } 
  }
}

void text_scroll(unsigned long time, const char* text) 
{
  static unsigned long t0 = 0;
  static boolean state = false;
  static int16_t x = 0;
  static int16_t y = 0;

  unsigned long t = millis();

  if (t - t0 >= time) 
  {
    t0 = t;

    state = !state;

    display.clearDisplay();

    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(x, y);
    display.println(text);

    x++;
    if (x > SCREEN_WIDTH) 
    {
      x = -display.getCursorX();
    }

    display.display();
  }
}

void post(const char* url)
{
  if (WiFi.status() == WL_CONNECTED) 
  {
    HTTPClient http;

    String payload = "";

    http.begin(url);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) 
    {
      Serial.print("Server's response: ");
      Serial.println(http.getString());
    } 
    else 
    {
      Serial.print("Error during connection: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  }
}