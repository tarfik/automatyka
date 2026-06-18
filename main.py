import network
import time

from motor import Motor
from mqtt import MQTT
from ota import OTA
from conf import wifi_ssid, wifi_password, mqtt_client_id, mqtt_host, mqtt_port, mqtt_user, mqtt_password
import ntptime

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)

    while not wlan.isconnected():
        print('waiting for connection')
        time.sleep(1)

try:
    ntptime.settime()
    motor = Motor()
    ota = OTA()
    mqtt = MQTT(motor, ota, mqtt_client_id, mqtt_host, mqtt_port, mqtt_user, mqtt_password)

    wifi_connect()
    mqtt.connect()

    while True:
        try:
            mqtt.client.check_msg()
        except Exception as err"
            print("Error:", err)
        time.sleep(0.5)
except Exception as e:
    print("Error:", e)
    raise
