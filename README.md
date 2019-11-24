# RaspberryPi_Put_Realtime

Main program is **realtime_detector.py**

**tsl2561.py** and **lcd1605.py** are the customized drivers, hence no other drivers are required to install.

| Device  | PIN |
|---------|-----|
| DHT22   | 4   |
| TSL2561 | I2C |
| LCD1602 | I2C |

>crontab -e

Set auto run when rebooting: `@reboot sleep 5 && python3 /home/pi/IoT/realtime_detector.py`



