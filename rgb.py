#!/usr/bin/env python3

import RPi.GPIO as GPIO
from time import sleep

LED_R_PIN = 21
LED_G_PIN = 20
LED_B_PIN = 26

class RGBLED():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([LED_R_PIN, LED_G_PIN, LED_B_PIN],GPIO.OUT)
        self.red = GPIO.PWM(LED_R_PIN, 1000)
        self.green = GPIO.PWM(LED_G_PIN, 1000)
        self.blue = GPIO.PWM(LED_B_PIN, 1000)
        self.red.start(0)
        self.green.start(0)
        self.blue.start(0)

    def _map(self, x, in_min, in_max, out_min, out_max):
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def __del__(self):
        self.red.stop()
        self.green.stop()
        self.blue.stop()
        GPIO.cleanup()

    def set_color(self, r, g, b):
        '''
        RGB colors, in range [0, 255]
        '''
        self.red.ChangeDutyCycle(self._map(r, 0, 255, 0, 100))
        self.green.ChangeDutyCycle(self._map(g, 0, 255, 0, 100))
        self.blue.ChangeDutyCycle(self._map(b, 0, 255, 0, 100))


if __name__ == "__main__":
    led = RGBLED()
    led.set_color(0, 151, 157)
    sleep(5)
