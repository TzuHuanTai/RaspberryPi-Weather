import datetime as dt
import json
import os
import random
import smbus
import time
# import Adafruit_DHT as dht
import board
import adafruit_dht
from tsl2561 import TSL2561
from lcd1602 import LCD
from paho.mqtt import client as mqtt

# MQTT configuration
broker = os.environ.get("MQTT_BROKER")
port = int(os.environ.get("MQTT_PORT", 8883))
username = os.environ.get("MQTT_USERNAME")
password = os.environ.get("MQTT_PASSWORD")
device_id = os.environ.get("DEVICE_ID")
topic = f"{device_id}/weather"

# Sensor initialization
dht = adafruit_dht.DHT22(board.D16)
bus = smbus.SMBus(1)
tsl = TSL2561(bus)
lcd = LCD(bus)

readLux = 100
lcd.set_backlight(1)


def display_intro():
    lcd.lcd_display_string("Richard Corp.")
    for i in range(3):
        lcd.set_cursor(1, i * 4)
        lcd.lcd_display_string("go! ")
        time.sleep(0.5)


class Weather:
    def __init__(self, temp, rh, lux):
        self.ObsTime = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        self.temp = round(temp, 1)
        self.rh = round(rh, 1)
        self.lux = round(lux, 0)


def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"python-mqtt-{random.randint(0, 1000)}",
        protocol=mqtt.MQTTv5,
    )
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def read_sensors():
    try:
        # Read temperature and humidity
        t = dht.temperature
        h = dht.humidity

        # Read light level (lux) from TSL2561 sensor
        global readLux
        if readLux < 0:
            tsl.set_gain(0)
        elif readLux < 1024:
            tsl.set_gain(1)
        else:
            tsl.set_gain(0)

        if readLux < 0:
            tsl.set_integration_time(0)
        elif readLux < 1024:
            tsl.set_integration_time(2)
        elif readLux < 4096:
            tsl.set_integration_time(1)
        else:
            tsl.set_integration_time(0)

        lux = tsl.read_lux()
        if lux is None:
            tsl.set_gain(0)
            tsl.set_integration_time(0)
            lux = tsl.read_lux() or -1

        return Weather(t, h, lux)
    except Exception as e:
        print(f"Error reading sensors: {e}")
        return None


def display_weather(data):
    if data:
        lcd.set_cursor(0, 0)
        lcd.lcd_display_string(f"Temp:{data.temp}C Lux: ")
        lcd.set_cursor(1, 0)
        lcd.lcd_display_string(f"Humi:{data.rh}% {data.lux}")
    else:
        lcd.set_cursor(0, 15)
        lcd.lcd_display_string("*")


def publish_data(client, data):
    try:
        if data:
            body = json.dumps(data.__dict__)
            client.publish(topic, body, qos=1)
            print(f"Published: {body}")
    except Exception as e:
        print(f"Error publishing data: {e}")


def main():
    client = connect_mqtt()
    client.loop_start()
    display_intro()
    while True:
        data = read_sensors()
        display_weather(data)
        publish_data(client, data)
        time.sleep(3)


if __name__ == "__main__":
    main()
