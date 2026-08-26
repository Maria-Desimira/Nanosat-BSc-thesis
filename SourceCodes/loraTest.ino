#include <SoftwareSerial.h>
#include <RH_RF95.h>

SoftwareSerial ss(3, 4);
RH_RF95 rf95(ss);

char commandBuffer[32];
uint8_t commandLength = 0;

void setup()
{
    Serial.begin(9600);
    ss.begin(57600);

    if (!rf95.init())
    {
        Serial.println("LoRa init failed");

        while (1);
    }

    rf95.setFrequency(434.0);
}

void sendCommand(const char* command)
{
    rf95.send((uint8_t*)command, strlen(command) + 1);
    rf95.waitPacketSent();
}

void loop()
{
    // Проверка дали е въведена команда в Serial Monitor
    while (Serial.available())
    {
        char c = Serial.read();

        if (c == '\n' || c == '\r')
        {
            if (commandLength > 0)
            {
                commandBuffer[commandLength] = '\0';

                if (strcmp(commandBuffer, "temp_c") == 0 ||
                    strcmp(commandBuffer, "temp_k") == 0 ||
                    strcmp(commandBuffer, "gps") == 0 ||
                    strcmp(commandBuffer, "alt") == 0 ||
                    strcmp(commandBuffer, "sat") == 0 ||
                    strcmp(commandBuffer, "acc") == 0 ||
                    strcmp(commandBuffer, "gyro") == 0 ||
                    strcmp(commandBuffer, "mag") == 0 ||
                    strcmp(commandBuffer, "data") == 0 )

                {
                    sendCommand(commandBuffer);
                }

                commandLength = 0;
            }
        }
        else if (commandLength < sizeof(commandBuffer) - 1)
        {
            commandBuffer[commandLength++] = c;
        }
    }

    // Проверка дали има получен пакет
    if (rf95.available())
    {
        uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
        uint8_t len = sizeof(buf);

        if (rf95.recv(buf, &len))
        {
            if (len >= sizeof(buf))
                len = sizeof(buf) - 1;

            buf[len] = '\0';

            Serial.println((char*)buf);
        }
    }
}