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
        self.scheduled_open_time = "07:00"  # Default: open at 7:00
        self.scheduled_close_time = "21:00"  # Default: close at 21:00
        self.scheduling_enabled = True  # Flag to enable/disable scheduling
        self.last_triggered_minute = None  # Track to avoid multiple triggers in same minute

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
        # Check scheduled open/close times (only if scheduling is enabled)
        if not self.scheduling_enabled:
            return
            
        t = time.localtime(time.time() + 3600)
        current_time = "{:02d}:{:02d}".format(t[3], t[4])
        current_minute = (t[3], t[4])
        
        # Avoid triggering multiple times in same minute
        if self.last_triggered_minute != current_minute:
            if self.scheduled_open_time and current_time == self.scheduled_open_time:
                self.log("Scheduled opening at {}".format(current_time))
                self.publish("OTWIERANIE")
                self.motor.open()
                self.last_triggered_minute = current_minute
            
            elif self.scheduled_close_time and current_time == self.scheduled_close_time:
                self.log("Scheduled closing at {}".format(current_time))
                self.publish("ZAMYKANIE")
                self.motor.close()
                self.last_triggered_minute = current_minute
        
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
            
            elif msg.startswith("SET_OPEN_TIME "):
                time_str = msg.split(" ", 1)[1]
                try:
                    # Validate time format HH:MM
                    parts = time_str.split(":")
                    if len(parts) == 2:
                        hour = int(parts[0])
                        minute = int(parts[1])
                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            self.scheduled_open_time = time_str
                            self.publish("OPEN_TIME_SET: {}".format(time_str))
                            self.log("Open time scheduled: {}".format(time_str))
                        else:
                            self.publish("ERROR: Invalid time")
                            self.log("Invalid open time: {}".format(time_str))
                    else:
                        self.publish("ERROR: Use format HH:MM")
                        self.log("Invalid time format: {}".format(time_str))
                except Exception as e:
                    self.publish("ERROR: {}".format(e))
                    self.log("Error setting open time: {}".format(e))
            
            elif msg.startswith("SET_CLOSE_TIME "):
                time_str = msg.split(" ", 1)[1]
                try:
                    # Validate time format HH:MM
                    parts = time_str.split(":")
                    if len(parts) == 2:
                        hour = int(parts[0])
                        minute = int(parts[1])
                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            self.scheduled_close_time = time_str
                            self.publish("CLOSE_TIME_SET: {}".format(time_str))
                            self.log("Close time scheduled: {}".format(time_str))
                        else:
                            self.publish("ERROR: Invalid time")
                            self.log("Invalid close time: {}".format(time_str))
                    else:
                        self.publish("ERROR: Use format HH:MM")
                        self.log("Invalid time format: {}".format(time_str))
                except Exception as e:
                    self.publish("ERROR: {}".format(e))
                    self.log("Error setting close time: {}".format(e))
            
            elif msg == "GET_SCHEDULE":
                status = "ON" if self.scheduling_enabled else "OFF"
                schedule_msg = "SCHEDULE: {}, OPEN: {}, CLOSE: {}".format(
                    status,
                    self.scheduled_open_time or "not set",
                    self.scheduled_close_time or "not set"
                )
                self.publish(schedule_msg)
                self.log("Schedule: {}".format(schedule_msg))
            
            elif msg == "SCHEDULE_OFF":
                self.scheduling_enabled = False
                self.publish("SCHEDULING_DISABLED")
                self.log("Scheduling disabled")
            
            elif msg == "SCHEDULE_ON":
                self.scheduling_enabled = True
                self.publish("SCHEDULING_ENABLED")
                self.log("Scheduling enabled")
                
        except Exception as e:
            self.log("Error in callback: {}".format(e))
