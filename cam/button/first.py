import os
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

ButtonPin = 17
GPIO.setup(ButtonPin, GPIO.IN)

print("---------------")
print(" Button + GPIO ")
print("---------------")

#print(GPIO.input(ButtonPin))

while True:
    print(GPIO.input(ButtonPin))
#    if GPIO.input(ButtonPin) == False:
#        print("Button Pressed")
#        print(GPIO.input(ButtonPin))
#        time.sleep(1) # Sleep for 1 second
#    else:
#        os.system('clear') # Clears the screen
#        print("Waiting for you to press a button")
