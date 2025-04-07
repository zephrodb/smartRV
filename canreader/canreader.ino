
/****************************************************/
#include <Arduino.h>
#include <mcp_can.h>
#include <SPI.h>
#include <WiFi.h>
#include <Wire.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"
#include <stdint.h>
#include "time.h"

/************************* WiFi Access Point *********************************/
#define WLAN_SSID       "Rosebud"
#define WLAN_PASS       "Explorer"
WiFiClient client;
/************************* MQTT Server config *********************************/

#define MQTT_SERVER      "192.168.88.250"
#define MQTT_SERVERPORT  1883                   // use 8883 for SSL
#define MQTT_USERNAME    "mqtt_user"
#define MQTT_PW         "mqtt_user"
#define FEED "/holley/canbus"
Adafruit_MQTT_Client mqtt(&client, MQTT_SERVER, MQTT_SERVERPORT, MQTT_USERNAME, MQTT_PW);
Adafruit_MQTT_Publish pub_measurment = Adafruit_MQTT_Publish(&mqtt, FEED);

/************************  NTP setup **************************************/
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 0;
const int   daylightOffset_sec = 3600;
//configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);



//********************* NTP/Time void setup ***********************

const char* ntpServer = "pool.ntp.org";
unsigned long epochTime; 

unsigned long getTime() {
  time_t now;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    //Serial.println("Failed to obtain time");
    return(0);
  }
  time(&now);
  return now;
}

//************************************************************************

//******************* CANBUS Setup  ************************************

const float versionNumber = 1.1; // so you can tell which version is burnt into the chip

// *********************** CAN related variables *****************
unsigned char CANLen = 0;
unsigned char buf[8];
#define CAN0_INT 2 // define CANbus interrupt pin
const int spiChipSelectPin = 05;
MCP_CAN CAN0(spiChipSelectPin); // Set CS pin
unsigned long lastTimeCANgotMsg; // to check for CANBUS timeouts
long unsigned int rxId;

// pins for MCP2515 CAN bus board to arduino nano
// Int D2
// SCK D13
// SI D11
// SO D12
// CS D10
// GND
// VCC

union Data { // overlay CAN payload with Long intgeger
unsigned char payloadArray[4]; // 8 byte payload area to the CAN BUS
unsigned long int payload;
};

int currRpm; // RPM xx,xxx
float currInjPulsewidth; // in milliseconds xx.x
float currTiming; // in degrees xx.x
int currMap; // in kPa xxx.x
float currBattery; // in volts xx.x
int currCoolant; // in F xxx
int lbsPerHourFromHolley; // in lbs/hour x,xxx

void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println(F("CANBus-MQTT-interface"));
  Serial.println(); 
  Serial.println();
  Serial.print(F("Connecting to "));
  Serial.println(WLAN_SSID);
  
  WiFi.begin(WLAN_SSID, WLAN_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(F("."));
  }

  Serial.println();
  Serial.println(F("WiFi connected"));
  Serial.println(F("IP address: ")); Serial.println(WiFi.localIP());
  Serial.print(F("Holley CANbus Ver: ")); Serial.println(versionNumber);
  Serial.println(F("Starting CANbus"));
  while (CAN0.begin(MCP_ANY, CAN_1000KBPS, MCP_8MHZ) != CAN_OK) { // init CAN bus : baudrate = 1000k
    Serial.println(F("CAN BUS Shield init fail"));
    delay(500);
  }

  Serial.println(F("CAN BUS Shield init ok!"));
  pinMode(CAN0_INT, INPUT);
  CAN0.setMode(MCP_NORMAL); // Set operation mode to normal so the MCP2515 sends acks to received data.

  MQTT_connect();
} 


void loop() {
  MQTT_connect();
  check_for_CAN_message(); // checks for next CAN message from Holley
  check_for_CAN_timeout(); // checks for timeout in CAN messages


}
void MQTT_connect() {
  int8_t ret;

  // Stop if already connected.
  if (mqtt.connected()) {
    return;
  }

  Serial.print(F("Connecting to MQTT... "));

  
  while ((ret = mqtt.connect()) != 0) { // connect will return 0 for connected
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println(F("Retrying MQTT connection in 5 seconds..."));
    mqtt.disconnect();
    delay(1000);  
    }
  
  Serial.println(F("MQTT Connected!"));
}

/* ++++++++++++++++++++++++++++++++++++++++++++++++++++*/
void check_for_CAN_message() {

      if(!digitalRead(CAN0_INT)) { // If CAN0_INT pin is low, read receive buffer

      CAN0.readMsgBuf(&rxId, &CANLen, buf); // Read data: len = data length, buf = data byte(s)
      union Data data; // overlay 4 char buffer for conversion to unsigned long int
      rxId = rxId & 0x7FFFF000; // filter out serial number .
      switch ( rxId ) {
      case 0x1E005000: // 0x1E005000 fuel packet
      data.payloadArray[0] = buf[7]; // shift the data from CAN buffer to unsigned long
      data.payloadArray[1] = buf[6];
      data.payloadArray[2] = buf[5];
      data.payloadArray[3] = buf[4];
      lbsPerHourFromHolley = (int)(data.payload / 256); // remove Holley 256 multiplier
      sprintf(buffer, "lbsPerHourFromHolley="%s" %s", lbsPerHourFromHolley, epochTime);
      Serial.println(buffer);
      Serial.println("");  
      pub_measurment.publish(buffer);

      data.payloadArray[0] = buf[3]; // shift the data from CAN buffer to unsigned long
      data.payloadArray[1] = buf[2];
      data.payloadArray[2] = buf[1];
      data.payloadArray[3] = buf[0];
      currInjPulsewidth = (float)data.payload / 256.0;
      sprintf(buffer, "currInjPulsewidth="%s" %s", currInjPulsewidth, epochTime);
      Serial.println(buffer);
      Serial.println("");  
      pub_measurment.publish(buffer);

      break;

      case 0x1E001000: //rpm packet
      data.payloadArray[0] = buf[7]; // shift the data from CAN buffer to unsigned long
      data.payloadArray[1] = buf[6];
      data.payloadArray[2] = buf[5];
      data.payloadArray[3] = buf[4];
      currRpm = (int)(data.payload / 256);
      sprintf(buffer, "currRpm="%s" %s", currRpm, epochTime);
      Serial.println(buffer);
      Serial.println("");  
      pub_measurment.publish(buffer);

      break;

      case 0x1E015000: //Timing packet
      data.payloadArray[0] = buf[3]; // shift the data from CAN buffer to unsigned long
      data.payloadArray[1] = buf[2];
      data.payloadArray[2] = buf[1];
      data.payloadArray[3] = buf[0];
      currTiming = (float)data.payload / 256.0;
      sprintf(buffer, "currTiming="%s" %s", currTiming, epochTime);
      Serial.println(buffer);
      Serial.println("");  
      pub_measurment.publish(buffer);
      break;

      case 0x1E019000: //MAP packet
      data.payloadArray[0] = buf[3]; // shift the data from CAN buffer to unsigned long
      data.payloadArray[1] = buf[2];
      data.payloadArray[2] = buf[1];
      data.payloadArray[3] = buf[0];
      currMap = (int)(data.payload / 256);
      sprintf(buffer, "currMap="%s" %s", currMap, epochTime);
      Serial.println(buffer);
      Serial.println("");  
      pub_measurment.publish(buffer);
      break;

      case 0x1E021000: //coolant packet
      data.payloadArray[0] = buf[7]; // shift the data from CAN buffer to unsigned long
      data.payloadArray[1] = buf[6];
      data.payloadArray[2] = buf[5];
      data.payloadArray[3] = buf[4];
      currCoolant = (int)(data.payload / 256);
      sprintf(buffer, "currCoolant="%s" %s", currCoolant, epochTime);
      Serial.println(buffer);
      Serial.println("");  
      pub_measurment.publish(buffer);
      break;

      case 0x1E025000: //Battery
      data.payloadArray[0] = buf[7]; // shift the data from CAN buffer to unsigned long
      data.payloadArray[1] = buf[6];
      data.payloadArray[2] = buf[5];
      data.payloadArray[3] = buf[4];
      currBattery = (float)data.payload / 256.0;
      sprintf(buffer, "currBattery="%s" %s", currBattery, epochTime);
      Serial.println(buffer);
      Serial.println("");  
      pub_measurment.publish(buffer);
      break;

      default: // debug printing to serial
      return;
      break;

      lastTimeCANgotMsg = millis();
        }// end switch
      } // end CAN msg avail
    } // end check_for_CAN_message

/* ++++++++++++++++++++++++++++++++++++++++++++++++++++*/
void check_for_CAN_timeout() { // if a CAN failure occurs
if ( millis() - lastTimeCANgotMsg > 500 ) {
Serial.println(F("Canbus Timeout"));
lastTimeCANgotMsg = millis();
}
} // end check_for_CAN_timeout
