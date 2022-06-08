#include <WiFi.h>
#include <Wire.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"
#include <stdint.h>
#include <MQUnifiedsensor.h>
#include <ErriezINA219.h>
#include "DHT.h" 

/************************** DHT11 setup **************************************/

#define DHT11PIN 4

DHT dht(DHT11PIN, DHT11);

/************************* i2c setup *****************************************/

#define I2C_SDA_0 33
#define I2C_SCL_0 32

#define I2C_SDA_1 21
#define I2C_SCL_1 22

/************************* WiFi Access Point *********************************/

#define WLAN_SSID       "RosebudExplorer"
#define WLAN_PASS       "exploreuranus"
WiFiClient client;

/************************* MQTT Server config *********************************/

#define MQTT_SERVER      "192.168.10.1"
#define MQTT_SERVERPORT  1883                   // use 8883 for SSL
#define MQTT_USERNAME    "dale"
#define MQTT_PW         "paleale"
#define FEED "/feeds/stats"
Adafruit_MQTT_Client mqtt(&client, MQTT_SERVER, MQTT_SERVERPORT, MQTT_USERNAME, MQTT_PW);
Adafruit_MQTT_Publish pub_measurment = Adafruit_MQTT_Publish(&mqtt, FEED);

/************************  ammeter setup  **************************************/

INA219 ina219_A = INA219(0x40, 0.00025);
INA219 ina219_B = INA219(0x45, 0.00025);
INA219 ina219_C = INA219(0x44, 0.00025);
INA219 ina219_D = INA219(0x45, 0.00025);

//************************  MQ5 setup  *****************************************/

#define board ("ESP-32")
#define Voltage_Resolution 3.3
#define pin (35) //Analog input 0 of your arduino
#define type "MQ-5" //MQ5
#define ADC_Bit_Resolution 12 
#define RatioMQ5CleanAir 6.5  //RS / R0 = 6.5 ppm 
MQUnifiedsensor MQ5(board, Voltage_Resolution, ADC_Bit_Resolution, pin, type);

//************************** Boom goes the dynamite ***************************/

char buffer[1024] = "";

void setup(void) 
{
  Serial.begin(115200);
  Serial.println("Hello!");
  Serial.println(F("CurrentSensorSuite With DHT11"));
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

  Wire.begin();
  Wire1.begin(I2C_SDA_0,I2C_SCL_0);

  dht.begin();

}
void loop(void) 
{
  MQTT_connect();

  if (! dht.readHumidity()) {
    Serial.println("Failed to get a reading from DHT");
  }
  else {
    float humi = dht.readHumidity();
    float temp = dht.readTemperature(true);
    float hi = dht.computeHeatIndex();
    String humi_t = String(humi, 1);
    String temp_t = String(temp, 1);
    String hi_t = String(hi, 1);
    sprintf(buffer, "t_0,location=interior temp_F=%s ", temp_t);
    Serial.println(buffer);
    pub_measurment.publish(buffer);
    sprintf(buffer, "t_0,location=interior RH=%s ", humi_t);
    Serial.println(buffer);
    pub_measurment.publish(buffer);
    sprintf(buffer, "t_0,location=interior HI=%s ", hi_t);
    Serial.println(buffer);
    pub_measurment.publish(buffer);
  }
  if (! ina219_A.read()) {
    Serial.println("Failed to find INA219 chip 0x40");
  }
    else {
      float shuntvoltage_0 = 0;
      float busvoltage_0 = 0;
      float current_0 = 0;
      float loadvoltage_0 = 0;
      float power_0 = 0;
      shuntvoltage_0 = ina219_A.shuntVoltage;
      busvoltage_0 = ina219_A.busVoltage;
      current_0 = (ina219_A.current / 1000 );
      power_0 = (ina219_A.power / 1000 );
      loadvoltage_0 = busvoltage_0 + (shuntvoltage_0 / 1000);
      String bv_0 = String(busvoltage_0, 5);
      String sv_0 = String(shuntvoltage_0, 5);
      String lv_0 = String(loadvoltage_0, 5);
      String c_0 = String(current_0, 5);
      String p_0 = String(power_0, 5);
      sprintf(buffer, "battery0,location=coach1 bus_voltage=%s ", bv_0);
      Serial.println(buffer);
      pub_measurment.publish(buffer);
      sprintf(buffer, "battery0,location=coach1 shunt_voltage=%s ", sv_0);
      Serial.println(buffer);
      pub_measurment.publish(buffer);
      sprintf(buffer, "battery0,location=coach1 load_voltage=%s ", lv_0);
      Serial.println(buffer);
      pub_measurment.publish(buffer);
      sprintf(buffer, "battery0,location=coach1 current=%s ", c_0);
      Serial.println(buffer);
      pub_measurment.publish(buffer);
      sprintf(buffer, "battery0,location=coach1 power=%s ", p_0);
      Serial.println(buffer);
      pub_measurment.publish(buffer);
    }
  if (! ina219_B.read()) {
    Serial.println("Failed to find INA219 chip 0x45");
  }
    else {
      float shuntvoltage_1 = 1;
      float busvoltage_1 = 1;
      float current_1 = 1;
      float loadvoltage_1 = 1;
      float power_1 = 1;
      shuntvoltage_1 = ina219_B.shuntVoltage;
      busvoltage_1 = ina219_B.busVoltage;
      current_1 = (ina219_B.current / 1111 );
      power_1 = (ina219_B.power / 1111 );
      loadvoltage_1 = busvoltage_1 + (shuntvoltage_1 / 1111);
      String bv_1 = String(busvoltage_1, 5);
      String sv_1 = String(shuntvoltage_1, 5);
      String lv_1 = String(loadvoltage_1, 5);
      String c_1 = String(current_1, 5);
      String p_1 = String(power_1, 5);
      sprintf(buffer, "battery1,location=chassis1 bus_voltage=%s ", bv_1);
      Serial.println(buffer);
      pub_measurment.publish(buffer);
      sprintf(buffer, "battery1,location=chassis1 shunt_voltage=%s ", sv_1);
      Serial.println(buffer);
      pub_measurment.publish(buffer);
      sprintf(buffer, "battery1,location=chassis1 load_voltage=%s ", lv_1);
      Serial.println(buffer);
      pub_measurment.publish(buffer);
      sprintf(buffer, "battery1,location=chassis1 current=%s ", c_1);
      Serial.println(buffer);
      pub_measurment.publish(buffer);
      sprintf(buffer, "battery1,location=chassis1 power=%s ", p_1);
      Serial.println(buffer);
      pub_measurment.publish(buffer);

    }
  // if (! ina219_C.read()) {
  //   Serial.println("Failed to find INA219 chip 0x40");
  // }
  //   else {
  //     float shuntvoltage_2 = 0;
  //     float busvoltage_2 = 0;
  //     float current_2 = 0;
  //     float loadvoltage_2 = 0;
  //     float power_2 = 0;
  //     shuntvoltage_2 = ina219_C.shuntVoltage;
  //     busvoltage_2 = ina219_C.busVoltage;
  //     current_2 = (ina219_C.current / 1000 );
  //     power_2 = (ina219_C.power / 1000 );
  //     loadvoltage_2 = busvoltage_2 + (shuntvoltage_2 / 1000);
  //     String bv_2 = String(busvoltage_2, 5);
  //     String sv_2 = String(shuntvoltage_2, 5);
  //     String lv_2 = String(loadvoltage_2, 5);
  //     String c_2 = String(current_2, 5);
  //     String p_2 = String(power_2, 5);
  //     sprintf(buffer, "battery2,location=blank1 bus_voltage=%s ", bv_2);
  //     Serial.println(buffer);
  //     pub_measurment.publish(buffer);
  //     sprintf(buffer, "battery2,location=blank1 shunt_voltage=%s ", sv_2);
  //     Serial.println(buffer);
  //     pub_measurment.publish(buffer);
  //     sprintf(buffer, "battery2,location=blank1 load_voltage=%s ", lv_2);
  //     Serial.println(buffer);
  //     pub_measurment.publish(buffer);
  //     sprintf(buffer, "battery2,location=blank1 current=%s ", c_2);
  //     Serial.println(buffer);
  //     pub_measurment.publish(buffer);
  //     sprintf(buffer, "battery2,location=blank1 power=%s ", p_2);
  //     Serial.println(buffer);
  //     pub_measurment.publish(buffer);
  //   }
  // if (! ina219_C.read()) {
  //   Serial.println("Failed to find INA219 chip 0x44");
  // }
  //   else {
  //     float shuntvoltage_3 = 0;
  //     float busvoltage_3 = 0;
  //     float current_3 = 0;
  //     float loadvoltage_3 = 0;
  //     float power_3 = 0;
  //     shuntvoltage_3 = ina219_C.shuntVoltage;
  //     busvoltage_3 = ina219_C.busVoltage;
  //     current_3 = (ina219_C.current / 1000 );
  //     power_3 = (ina219_C.power / 1000 );
  //     loadvoltage_3 = busvoltage_3 + (shuntvoltage_3 / 1000);
  //     String bv_3 = String(busvoltage_3, 5);
  //     String sv_3 = String(shuntvoltage_3, 5);
  //     String lv_3 = String(loadvoltage_3, 5);
  //     String c_3 = String(current_3, 5);
  //     String p_3 = String(power_3, 5);
  //     sprintf(buffer, "battery3,location=blank2 bus_voltage=%s ", bv_3);
  //     Serial.println(buffer);
  //     pub_measurment.publish(buffer);
  //     sprintf(buffer, "battery3,location=blank2 shunt_voltage=%s ", sv_3);
  //     Serial.println(buffer);
  //     pub_measurment.publish(buffer);
  //     sprintf(buffer, "battery3,location=blank2 load_voltage=%s ", lv_3);
  //     Serial.println(buffer);
  //     pub_measurment.publish(buffer);
  //     sprintf(buffer, "battery3,location=blank2 current=%s ", c_3);
  //     Serial.println(buffer);
  //     pub_measurment.publish(buffer);
  //     sprintf(buffer, "battery3,location=blank2 power=%s ", p_3);
  //     Serial.println(buffer);
  //     pub_measurment.publish(buffer);
  //   }
  MQ5.setRegressionMethod(1); //_PPM =  a*ratio^b
  MQ5.setRL(10); 
  MQ5.setR0(1.53); 

  //MQ5.serialDebug(true); 
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
  MQ5.update(); 
  float alcohol_t = MQ5.readSensor(); 
  String alcohol = String(alcohol_t, 2);
  //MQ5.serialDebug(); 

  sprintf(buffer, "aq,location=exterior H2=%s ", h2);
  Serial.println(buffer);
  pub_measurment.publish(buffer);

  sprintf(buffer, "aq,location=exterior LPG=%s ", lpg);
  Serial.println(buffer);
  pub_measurment.publish(buffer);

  sprintf(buffer, "aq,location=exterior CH4=%s ", ch4);
  Serial.println(buffer);
  pub_measurment.publish(buffer);

  sprintf(buffer, "aq,location=exterior CO=%s ", co);
  Serial.println(buffer);
  pub_measurment.publish(buffer);

  sprintf(buffer, "aq,location=exterior ALCOHOL=%s ", alcohol);
  Serial.println(buffer);  
  pub_measurment.publish(buffer);
  delay(5000);
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
