import network
import time

from motor import Motor
from mqtt import MQTT
from ota import OTA
from conf import wifi_ssid, wifi_password, mqtt_client_id, mqtt_host, mqtt_port, mqtt_user, mqtt_password
import ntptime

wdt = machine.WDT(timeout=8000)

last_wifi_ok = False
last_mqtt_ok = False

def wifi_connect():
    global last_wifi_ok

    wlan.active(True)

    if wlan.isconnected():
        last_wifi_ok = True
        return True

    print("[WiFi] Connecting...")

    wlan.connect(WIFI_SSID, WIFI_PASS)

    for _ in range(20):
        if wlan.isconnected():
            print("[WiFi] Connected:", wlan.ifconfig())
            last_wifi_ok = True
            return True
        time.sleep(1)

    print("[WiFi] Failed")
    last_wifi_ok = False
    return False

def ensure_wifi():
    if not wlan.isconnected():
        return wifi_connect()
    return True


ntptime.settime()
motor = Motor()
ota = OTA()
mqtt = MQTT(motor, ota, mqtt_client_id, mqtt_host, mqtt_port, mqtt_user, mqtt_password)

wifi_connect()
mqtt.connect()

while True:
    # watchdog feed
    wdt.feed()
    # WIFI check
    if not ensure_wifi():
        time.sleep(2)
        continue

    # MQTT check
    if not mqtt.ensure_mqtt():
        time.sleep(2)
        continue

    try:
        mqtt.client.check_msg()
    except Exception as err:
        print("[MQTT loop error]", e)
        mqtt_connect()
        print("Error:", err)
    time.sleep(0.5)

