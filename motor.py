from machine import Pin, PWM
import time

class Motor:
    def __init__(self, emergency_timeout_s=25):
        self.R_EN = Pin(5, Pin.OUT)   # D1
        self.L_EN = Pin(4, Pin.OUT)   # D2
        self.R_PWM = PWM(Pin(14))     # D5
        self.L_PWM = PWM(Pin(12))     # D6
        self.emergency_timeout_ms = int(emergency_timeout_s * 1000)
        self.running = False
        self.started_ms = 0
        self.direction = None

        self.R_PWM.freq(1000)
        self.L_PWM.freq(1000)

        self.stop()

    def open(self):
        self.R_EN.on()
        self.L_EN.on()

        self.R_PWM.duty(800)
        self.L_PWM.duty(0)
        self.running = True
        self.started_ms = time.ticks_ms()
        self.direction = "OPEN"

    def close(self):
        self.R_EN.on()
        self.L_EN.on()

        self.R_PWM.duty(0)
        self.L_PWM.duty(800)
        self.running = True
        self.started_ms = time.ticks_ms()
        self.direction = "CLOSE"

    def stop(self):
        self.R_PWM.duty(0)
        self.L_PWM.duty(0)
        self.R_EN.off()
        self.L_EN.off()
        self.running = False
        self.started_ms = 0
        self.direction = None

    def check_emergency_timeout(self):
        if not self.running:
            return None

        if time.ticks_diff(time.ticks_ms(), self.started_ms) < self.emergency_timeout_ms:
            return None

        timed_out_direction = self.direction
        self.stop()
        return timed_out_direction
