# RaspberryPi_Put_Realtime

Main program is **realtime_detector.py**

## Preparations
1. Install packages
    ```bash
    sudo apt-get install python3-pip
    sudo pip3 install smbus
    sudo pip3 install Adafruit_DHT
    ```

2. Connect wires

    **tsl2561.py** and **lcd1605.py** are the customized drivers, hence no other drivers are required to install.

    | Device  | PIN |
    |---------|-----|
    | DHT22   | 16  |
    | TSL2561 | I2C |
    | LCD1602 | I2C |

## Setup 
* Set Linux service

1. Create a config
    ```bash
    sudo nano /etc/systemd/system/realtime-detector.service
    ```
2. Config sample:
    ```ini
    [Unit]
    Description= Realtime detector temperature, humidity and illuminance on Raspberry pi

    [Service]
    WorkingDirectory=/home/pi/IoT/RaspberryPi_Weather/
    ExecStart=python /home/pi/IoT/RaspberryPi_Weather/realtime_detector.py
    Restart=always
    # Restart service after 10 seconds if the dotnet service crashes:
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```
3. Enable and run the service:
    ```bash
    sudo systemctl enable realtime-detector.service
    sudo systemctl start realtime-detector.service
    ```
* alternative set crontab
    >crontab -e

  Set auto run when rebooting: `@reboot sleep 5 && python3 /home/pi/IoT/realtime_detector.py`

