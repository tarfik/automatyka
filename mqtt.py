from umqtt.simple import MQTTClient
import time

MQTT_BROKER = "YOUR_HIVEMQ_HOST"
CLIENT_ID = "drzwi-node"

TOPIC_CMD = b"drzwi/cmd"
TOPIC_STATUS = b"drzwi/status"
TOPIC_LOG = b"drzwi/log"

class MQTT:
    def __init__(self, motor, ota):
        self.motor = motor
        self.ota = ota

        self.client = MQTTClient(
            CLIENT_ID,
            MQTT_BROKER,
            user="USER",
            password="PASS",
            keepalive=60
        )

        self.client.set_callback(self.callback)

    def connect(self):
        self.client.connect()
        self.client.subscribe(TOPIC_CMD)
        self.publish("BOOTED")

    def publish(self, msg):
        self.client.publish(TOPIC_STATUS, msg)

    def log(self, msg):
        self.client.publish(TOPIC_LOG, msg)

    def callback(self, topic, msg):
        msg = msg.decode()

        if msg == "OPEN":
            self.publish("OPENING")
            self.motor.open()
            time.sleep(10)
            self.motor.stop()
            self.publish("OPEN")

        elif msg == "CLOSE":
            self.publish("CLOSING")
            self.motor.close()
            time.sleep(10)
            self.motor.stop()
            self.publish("CLOSED")

        elif msg == "STOP":
            self.motor.stop()
            self.publish("STOPPED")

        elif msg == "UPDATE":
            self.publish("UPDATING")
            self.ota.update()
