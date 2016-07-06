#!/usr/bin/python

import os
import time
import RPi.GPIO as GPIO
import subprocess
#import sys
import signal

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

buttonPin = 17
buzzPin = 22

GPIO.setup(buttonPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(buzzPin, GPIO.OUT)
GPIO.output(buzzPin, GPIO.LOW)

# Morse

def dot():
    GPIO.output(buzzPin, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(buzzPin, GPIO.LOW)
    time.sleep(0.1)

def dash():
    GPIO.output(buzzPin, GPIO.HIGH)
    time.sleep(0.3)
    GPIO.output(buzzPin, GPIO.LOW)
    time.sleep(0.1)

def letterSpace():
    time.sleep(0.2)

def up():
    dot()
    dot()
    dash()

def down():
    dash()
    dot()
    dot()

def log(c):
    global motion
    if (motion):
        print("stop")
        subprocess.call(['service','motion','stop'])
	motion = False
        down()
    else:
        print("start")
        subprocess.call(['service','motion','start'])
        motion = True
        up()

def main():
    GPIO.add_event_detect(buttonPin,GPIO.RISING,callback=log,bouncetime=300)
    signal.pause()

motion = False
main()

GPIO.remove_event_detect(buttonPin)
GPIO.cleanup()
