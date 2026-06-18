from umqtt.simple import MQTTClient
import time


TOPIC_CMD = b"drzwi/cmd"
TOPIC_STATUS = b"drzwi/status"
TOPIC_LOG = b"drzwi/log"

def get_time_pl():
    t = time.localtime(time.time() + 3600)
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )

class MQTT:
    def __init__(self, motor, ota, mqtt_client_id, mqtt_host, mqtt_port, mqtt_user, mqtt_password):
        self.motor = motor
        self.ota = ota
        self.last_mqtt_ok = None

        self.client = MQTTClient(
            mqtt_client_id,
            mqtt_host,
            mqtt_port,
            user=mqtt_user,
            password=mqtt_password,
            keepalive=60
        )
        self.client.set_callback(self.callback)

    def connect(self):
        try:
            mqtt.set_last_will(TOPIC_STATUS, b"OFFLINE", retain=True)
    
            mqtt.set_callback(self.callback)
            mqtt.connect()
    
            mqtt.subscribe(TOPIC_CMD)
    
            self.publish("ONLINE")
    
            print("[MQTT] Connected")
            last_mqtt_ok = True
            return True
    
        except Exception as e:
            print("[MQTT] Connect failed:", e)
            last_mqtt_ok = False
            return False

    def publish(self, msg):
        self.client.publish(TOPIC_STATUS, msg)

    def log(self, msg):
        self.client.publish(TOPIC_LOG, msg)

    def callback(self, topic, msg):
        try:
            msg = msg.decode()
            self.log("On {} received command: {}".format(get_time_pl(), msg))

            if msg == "OPEN":
                self.publish("OTWIERANIE")
                self.motor.open()
                time.sleep(10)
                self.motor.stop()
                self.publish("OTWARTE")

            elif msg == "CLOSE":
                self.publish("ZAMYKANIE")
                self.motor.close()
                time.sleep(10)
                self.motor.stop()
                self.publish("ZAMKNIETE")

            elif msg == "STOP":
                self.motor.stop()
                self.publish("ZATRZYMANE")

            elif msg == "UPDATE":
                self.publish("AKTUALIZACJA")
                self.ota.update()
        except Exception as e:
            self.log("Error in callback: {}".format(e))
