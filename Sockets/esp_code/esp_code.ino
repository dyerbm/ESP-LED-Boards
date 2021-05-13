#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

const char* ssid = "Dyer Dilemma";
const char* password = "thunder123";


WiFiUDP Udp;
unsigned int localUdpPort = 42069;  // local port to listen on
char incomingPacket[255];  // buffer for incoming packets
const char* identityNumber = "48";

#define PIN 13
#define NUMLEDS 300

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUMLEDS, PIN, NEO_GRB + NEO_KHZ800);

void setup()
{
  Serial.begin(115200);
  Serial.println();

  strip.begin();
  for (int i=0;i<NUMLEDS;i++){
      strip.setPixelColor(i, strip.Color(0,0,0));
  }
  strip.show();

  Serial.println("LEDs ready");

  Serial.printf("Connecting to %s ", ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected");

  Udp.begin(localUdpPort);
  Serial.printf("Now listening at IP %s, UDP port %d\n", WiFi.localIP().toString().c_str(), localUdpPort);

  ESP.wdtDisable();
}


void loop()
{
  ESP.wdtFeed();
  int packetSize = Udp.parsePacket(); //"R1,G1,B1"
  
  if (packetSize==1){ //send ESP info out to server
      char cstr[16];
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write(WiFi.localIP().toString().c_str());
      Udp.write(",");
      Udp.write(identityNumber);
      Udp.endPacket();
  }
  else if (packetSize>0) //otherwise expect RGB data
  {
    // receive incoming UDP packets
    //Serial.printf("Received %d bytes from %s, port %d\n", packetSize, Udp.remoteIP().toString().c_str(), Udp.remotePort());
    int len = Udp.read(incomingPacket, 255);
      if (len > 0)
      {
        incomingPacket[len] = 0;
      }
    //Serial.printf("UDP packet contents: %s\n", incomingPacket);
       
    uint32_t times=micros(); //Time the function
    setLEDs(incomingPacket);
      
    Serial.println(micros()-times);
  }
}

void setLEDs(char* str){

  char *end = str;
    int color[3];
    int i=0;
    for(int i=0;i<3;i++){
      int n = strtol(str, &end, 10);
      color[i]=n;
      while (*end == ',') {
        end++;
      }
      str = end;
    }

  for (int i=0;i<NUMLEDS;i++){
      strip.setPixelColor(i, strip.Color(color[0],color[1],color[2]));
    }
    strip.show();
    
}
