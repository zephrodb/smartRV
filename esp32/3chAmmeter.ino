
/****************************************************/
#include <WiFi.h>
#include <Wire.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"
#include <Beastdevices_INA3221.h>
#include <stdint.h>
#include "time.h"
#include <MQUnifiedsensor.h>

/************************* WiFi Access Point *********************************/
#define WLAN_SSID       ""
#define WLAN_PASS       ""
WiFiClient client;
/************************* MQTT Server config *********************************/

#define MQTT_SERVER      "192.168.10.1"
#define MQTT_SERVERPORT  1883                   // use 8883 for SSL
#define MQTT_USERNAME    "dale"
#define MQTT_PW         "paleale"
#define FEED "/feeds/stats"
Adafruit_MQTT_Client mqtt(&client, MQTT_SERVER, MQTT_SERVERPORT, MQTT_USERNAME, MQTT_PW);
Adafruit_MQTT_Publish pub_measurment = Adafruit_MQTT_Publish(&mqtt, FEED);

/************************  NTP setup **************************************/
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 0;
const int   daylightOffset_sec = 3600;
//configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);


/************************  ammeter setup  **************************************/

Beastdevices_INA3221 ina3221(INA3221_ADDR40_GND);
//Beastdevices_INA3221 ina3221(INA3221_ADDR41_VCC);
//Beastdevices_INA3221 ina3221(INA3221_ADDR42_SDA);
//Beastdevices_INA3221 ina3221(INA3221_ADDR42_SCL);

//************************  MQ5 setup  *****************************************/

#define placa "Arduino UNO"
#define Voltage_Resolution 5
#define pin A0 //Analog input 0 of your arduino
#define type "MQ-5" //MQ5
#define ADC_Bit_Resolution 12 // For arduino UNO/MEGA/NANO
#define RatioMQ5CleanAir 6.5  //RS / R0 = 6.5 ppm 
MQUnifiedsensor MQ5(placa, Voltage_Resolution, ADC_Bit_Resolution, pin, type);


//********************* NTP/Time void setup ***********************

const char* ntpServer = "192.168.0.1";
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



void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println(F("CurrentSensorSuite-Batteries"));
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
  ina3221.begin();
  ina3221.reset();
  ina3221.setShuntRes(0025, 0025, 0025);

  configTime(0, 0, ntpServer);
} 


void loop() {
  MQTT_connect();
  
  float current0 = ina3221.getCurrent(INA3221_CH1);
  float voltage0 = ina3221.getVoltage(INA3221_CH1);
  String c0 = String(current0, 4);
  String v0 = String(voltage0, 2);
  epochTime = getTime();
  char buffer[1024] = "buffer";
  sprintf(buffer, "battery0,location=chassis0  current="%s" %s", c0, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);
  sprintf(buffer, "battery0,location=chassis0  voltage="%s" %s", v0, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);


  float current1 = ina3221.getCurrent(INA3221_CH2);
  float voltage1 = ina3221.getVoltage(INA3221_CH2);
  String c1 = String(current1, 4);
  String v1 = String(voltage1, 2);
  sprintf(buffer, "battery1,location=coach0  current="%s" %s", c1, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);
  sprintf(buffer, "battery1,location=coach0  voltage="%s" %s", v1, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);

  float current2 = ina3221.getCurrent(INA3221_CH3);
  float voltage2 = ina3221.getVoltage(INA3221_CH3);
  String c2 = String(current2, 4);
  String v2 = String(voltage2, 2);
  sprintf(buffer, "battery2,location=coach1  current="%s" %s", c2, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);
  sprintf(buffer, "battery2,location=coach1  voltage="%s" %s", v2, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);

  MQ5.setRegressionMethod(1); //_PPM =  a*ratio^b
  MQ5.setA(1163.8); MQ5.setB(-3.874); 
  MQ5.init();   
  MQ5.setRL(5);
  MQ5.update(); 
  float h2_t = MQ5.readSensor(); 
  String h2 = String(h2_t, 2);
  //MQ5.serialDebug(); 

  MQ5.setA(491204); MQ5.setB(-5.826); 
  MQ5.init();   
  MQ5.setRL(5);
  MQ5.update(); 
  float co_t = MQ5.readSensor(); 
  String co = String(co_t, 2);
  //MQ5.serialDebug(); 

  MQ5.setA(80.897); MQ5.setB(-2.431); 
  MQ5.init();   
  MQ5.setRL(5);
  MQ5.update(); 
  float lpg_t = MQ5.readSensor(); 
  String lpg = String(lpg_t, 2);
  //MQ5.serialDebug(); 

  MQ5.setA(177.65); MQ5.setB(-2.56); 
  MQ5.init(); 
  MQ5.setRL(5);    
  MQ5.update(); 
  float ch4_t = MQ5.readSensor(); 
  String ch4 = String(ch4_t, 2);
  //MQ5.serialDebug(); 

  MQ5.setA(97124); MQ5.setB(-4.918); 
  MQ5.init();   
  MQ5.setRL(5);  
  MQ5.update(); 
  float alcohol_t = MQ5.readSensor(); 
  String alcohol = String(alcohol_t, 8);
  //MQ5.serialDebug(); 

  epochTime = getTime();

  sprintf(buffer, "aq, location=exterior H2="%s" %s", h2, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);

  sprintf(buffer, "aq, location=exterior LGP="%s"  %s", lpg, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);

  sprintf(buffer, "aq, location=exterior CH4="%s" %s", ch4, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);

  sprintf(buffer, "aq, location=exterior  CO="%s" %s", co, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);

  sprintf(buffer, "aq, location=exterior ALCOHOL="%s" %s", alcohol, epochTime);
  Serial.println(buffer);
  Serial.println("");  
  pub_measurment.publish(buffer);

  delay(1000);

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
