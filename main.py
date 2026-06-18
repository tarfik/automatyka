import network
import time

from motor import Motor
from mqtt import MQTT
from ota import OTA
from conf import wifi_ssid, wifi_password

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)

    while not wlan.isconnected():
        time.sleep(1)

motor = Motor()
ota = OTA()
mqtt = MQTT(motor, ota)

wifi_connect()
mqtt.connect()

while True:
    mqtt.client.check_msg()
    time.sleep(0.1)
