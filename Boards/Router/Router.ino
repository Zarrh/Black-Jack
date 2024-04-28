// sudo arduino-cli upload -p *PORT* --fqbn esp32:esp32:esp32 Router.ino

#include <WiFi.h>
#include "esp_wifi.h"

const char* ssid = "IoT_Casino";
const char* password = "AceOfSpades";

IPAddress local_IP(192, 168, 4, 1);
IPAddress gateway_IP(192, 168, 4, 1);
IPAddress netmask_IP(255, 255, 255, 0);

const int channel = 10;
const bool hide_SSID = false;

void display_connected_devices()
{
    wifi_sta_list_t wifi_sta_list;
    tcpip_adapter_sta_list_t adapter_sta_list;
    esp_wifi_ap_get_sta_list(&wifi_sta_list);
    tcpip_adapter_get_sta_list(&wifi_sta_list, &adapter_sta_list);

    if (adapter_sta_list.num > 0)
    {
        Serial.println("-----------");
    }
    for (uint8_t i = 0; i < adapter_sta_list.num; i++)
    {
        tcpip_adapter_sta_info_t station = adapter_sta_list.sta[i];
        ip4_addr_t ip_addr;
        memcpy(&ip_addr, &station.ip, sizeof(ip4_addr_t));
        Serial.print((String)"[+] Device " + i + " | MAC : ");
        Serial.printf("%02X:%02X:%02X:%02X:%02X:%02X", station.mac[0], station.mac[1], station.mac[2], station.mac[3], station.mac[4], station.mac[5]);
        Serial.print((String) " | IP ");
        Serial.println(ip4addr_ntoa(&ip_addr));
    }
}

void setup()
{
    Serial.begin(115200);
    Serial.println("\n[*] Creating AP");
    
    WiFi.mode(WIFI_AP);
    WiFi.softAPConfig(local_IP, gateway_IP, netmask_IP);
    WiFi.softAP(ssid, password, channel, hide_SSID);

    Serial.print("[+] AP Created with IP Gateway ");
    Serial.println(WiFi.softAPIP());
}

void loop()
{
    display_connected_devices();
    delay(5000);
}