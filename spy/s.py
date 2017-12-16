#!/usr/bin/env python

# hardware
from gpiozero import MotionSensor
import io
import picamera
from blinkt import set_pixel, set_brightness, show, clear

# software
from datetime import datetime
# import random

# setup
pir = MotionSensor(15)
camera = picamera.PiCamera()
camera.resolution = (1280, 720)
camera.rotation = 180
stream = picamera.PiCameraCircularIO(camera, seconds=10) # back recording
camera.start_recording(stream, format='h264')

# functions
def motion_detected():
    return pir.motion_detected

# main
try:
    print 'ready'
    while True:
        camera.wait_recording(1)
        if motion_detected():
            print 'motion_detected'
            set_pixel(0, 0, 255, 0, 0.1) # recordin:green
            show()
            print 'recording'
            camera.wait_recording(50) # motion recording
            filename = 'out/' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.h264'
            print 'saving'
            stream.copy_to(filename) # back + motion = 60s recording
            stream.seek(0)
            stream.truncate()
            print 'saved'
        else:
            print 'no_motion'
            clear()
            show()
finally:
    camera.stop_recording()
