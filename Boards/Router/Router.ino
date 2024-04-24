// sudo arduino-cli upload -p *PORT* --fqbn esp32:esp32:esp32 Router.ino

#include <WiFi.h>
#include "esp_wifi.h"

const char* ssid = "IoT_Casino";
const char* password = "AceOfSpades";
const char* local_ip = "192.168.4.10";
const char* gateway_ip = "192.168.4.10";
const int channel = 10;
const bool hide_SSID = false;
const int max_connection = 3;

// MAC address of the device to assign a fixed IP address
//uint8_t mac_to_assign_ip[] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};
// IP address to assign to the device
//IPAddress fixed_ip(192, 168, 4, 10);

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

    IPAddress local;
    local.fromString(local_ip);
    IPAddress gateway;
    gateway.fromString(gateway_ip);
    
    WiFi.mode(WIFI_AP);
    WiFi.softAPConfig(local, gateway, IPAddress(255, 255, 255, 0));
    WiFi.softAP(ssid, password, channel, hide_SSID, max_connection);

    Serial.print("[+] AP Created with IP Gateway ");
    Serial.println(WiFi.softAPIP());
}

void loop()
{
    display_connected_devices();
    delay(5000);
}