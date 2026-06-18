from machine import Pin, PWM
import time

class Motor:
    def __init__(self):
        self.R_EN = Pin(5, Pin.OUT)   # D1
        self.L_EN = Pin(4, Pin.OUT)   # D2
        self.R_PWM = PWM(Pin(14))     # D5
        self.L_PWM = PWM(Pin(12))     # D6

        self.R_PWM.freq(1000)
        self.L_PWM.freq(1000)

        self.stop()

    def open(self):
        self.R_EN.on()
        self.L_EN.on()

        self.R_PWM.duty(800)
        self.L_PWM.duty(0)

    def close(self):
        self.R_EN.on()
        self.L_EN.on()

        self.R_PWM.duty(0)
        self.L_PWM.duty(800)

    def stop(self):
        self.R_PWM.duty(0)
        self.L_PWM.duty(0)
        self.R_EN.off()
        self.L_EN.off()
