# RaspberryPi-Weather

Show DHT22(temperature, humidity), TSL2561(illuminance) on LCD1602 monitor and publish data to mqtt.

## Preparations
1. Install packages
    ```bash
    sudo apt-get install python3-pip
    sudo pip3 install smbus Adafruit_DHT paho-mqtt
    ```

2. Connect wires

    **tsl2561.py** and **lcd1605.py** are the customized drivers, hence no other drivers are required to install.

    | Device  | PIN |
    |---------|-----|
    | DHT22   | 16  |
    | TSL2561 | I2C |
    | LCD1602 | I2C |

## Setup

Let sensors data publish to MQTT topic `${DEVICE_ID}/weather`.

- Add an `.env` with configs
    ```ini
    DEVICE_ID=home-pi-4b
    MQTT_BROKER=example.s1.eu.hivemq.cloud
    MQTT_PORT=8883
    MQTT_USERNAME=hakunamatata
    MQTT_PASSWORD=wonderful
    ```

- Setup Linux service
    ```bash
    sudo nano /etc/systemd/system/weather-detector.service
    ```

    ```ini
    [Unit]
    Description= Realtime detector temperature, humidity and illuminance on Raspberry pi

    [Service]
    WorkingDirectory=/home/pi/IoT/RaspberryPi_Weather/
    EnvironmentFile=/home/pi/IoT/RaspberryPi_Weather/.env
    ExecStart=/usr/bin/python /home/pi/IoT/RaspberryPi_Weather/weather_detector.py
    Restart=always
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```
3. Enable and run the service:
    ```bash
    sudo systemctl enable weather-detector.service
    sudo systemctl start weather-detector.service
    ```
