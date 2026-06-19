import network
import time
from machine import WDT
from motor import Motor
from mqtt import MQTT
from ota import OTA
from conf import wifi_ssid, wifi_password, mqtt_client_id, mqtt_host, mqtt_port, mqtt_user, mqtt_password, motor_emergency_timeout_s
import ntptime


wdt = WDT()

class WifiNet:
    def __init__(self, wdt_obj=None):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wdt = wdt_obj

    def wifi_connect(self):
        if self.wlan.isconnected():
            return True

        print("[WiFi] Connecting...")

        try:
            self.wlan.disconnect()
        except Exception:
            pass

        self.wlan.connect(wifi_ssid, wifi_password)

        for _ in range(20):
            if self.wdt is not None:
                self.wdt.feed()
            if self.wlan.isconnected():
                print("[WiFi] Connected:", self.wlan.ifconfig())
                return True
            time.sleep(1)

        print("[WiFi] Failed")
        return False

    def ensure_wifi(self):
        if not self.wlan.isconnected():
            return self.wifi_connect()
        return True


motor = Motor(emergency_timeout_s=motor_emergency_timeout_s)
ota = OTA()
mqtt = MQTT(motor, ota, mqtt_client_id, mqtt_host, mqtt_port, mqtt_user, mqtt_password)

wifi = WifiNet(wdt)
wifi.wifi_connect()
try:
    ntptime.settime()
    print("[NTP] Time synced")
except Exception as err:
    print("[NTP] Time sync failed:", err)
mqtt.connect()

while True:
    # watchdog feed
    wdt.feed()

    timed_out_direction = motor.check_emergency_timeout()
    if timed_out_direction is not None:
        alarm_msg = "AWARIA_TIMEOUT_{}".format(timed_out_direction)
        print("[SAFETY]", alarm_msg)
        mqtt.log(alarm_msg)
        mqtt.publish(alarm_msg)

    # WIFI check
    if not wifi.ensure_wifi():
        time.sleep(2)
        continue

    # MQTT check
    if not mqtt.ensure_mqtt():
        time.sleep(2)
        continue

    try:
        mqtt.process()
        mqtt.client.check_msg()
    except Exception as err:
        print("[MQTT loop error]", err)
        mqtt.connect()
    time.sleep(0.5)

