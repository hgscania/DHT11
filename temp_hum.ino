
#include <DHT11.h>

#define Baudrate  115200
#define dht_pin   5

DHT11 dht11(dht_pin);

char out_data[150];
int result,temperature,humidity;
void setup()
{
    Serial.begin(Baudrate);
}
void loop()
{
    // Attempt to read the temperature and humidity values from the DHT11 sensor.
    result= dht11.readTemperatureHumidity(temperature, humidity);
    if(result == 0)
      sprintf(out_data,"&%d,%d&",temperature*100,humidity*100);
     else
      sprintf(out_data,"&0,0&");
    Serial.println(out_data);
    delay(500);

}
