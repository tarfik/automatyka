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
        self.mqtt_client_id = mqtt_client_id
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.last_mqtt_ok = None
        self.client = None

    def connect(self):
        try:
            self.client = MQTTClient(
                self.mqtt_client_id,
                self.mqtt_host,
                self.mqtt_port,
                user=self.mqtt_user,
                password=self.mqtt_password,
                keepalive=60
            )
            self.client.set_last_will(TOPIC_STATUS, b"OFFLINE", retain=True)
    
            self.client.set_callback(self.callback)
            self.client.connect()
    
            self.client.subscribe(TOPIC_CMD)
    
            self.publish("ONLINE")
    
            print("[MQTT] Connected")
            self.last_mqtt_ok = True
            return True
    
        except Exception as e:
            print("[MQTT] Connect failed:", e)
            self.last_mqtt_ok = False
            return False

    def ensure_mqtt(self):
        if self.client is None:
            return self.connect()
        try:
            self.client.ping()
            return True
        except Exception:
            print("[MQTT] reconnecting...")
            return self.connect()

    def process(self):
        # Reserved for future periodic MQTT-related work.
        return
        
    def publish(self, msg):
        if self.client is None:
            return

        if isinstance(msg, str):
            msg = msg.encode()
        self.client.publish(TOPIC_STATUS, msg)

    def log(self, msg):
        if self.client is None:
            return

        if isinstance(msg, str):
            msg = msg.encode()
        self.client.publish(TOPIC_LOG, msg)

    def callback(self, topic, msg):
        try:
            if isinstance(msg, bytes):
                msg = msg.decode()
            self.log("On {} received command: {}".format(get_time_pl(), msg))

            if msg == "OPEN":
                self.publish("OTWIERANIE")
                self.motor.open()

            elif msg == "CLOSE":
                self.publish("ZAMYKANIE")
                self.motor.close()

            elif msg == "STOP":
                self.motor.stop()
                self.publish("ZATRZYMANE")

            elif msg == "UPDATE":
                self.publish("AKTUALIZACJA")
                self.ota.update()
        except Exception as e:
            self.log("Error in callback: {}".format(e))
