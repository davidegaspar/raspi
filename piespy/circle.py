import io
import random
import picamera

def motion_detected():
    # Randomly return True (like a fake motion detection routine)
    return random.randint(0, 10) == 0

camera = picamera.PiCamera()
stream = picamera.PiCameraCircularIO(camera, seconds=20)
camera.start_recording(stream, format='h264')
count = 3
try:
    while count:
        camera.wait_recording(1)
        if motion_detected():
            count -= 1
            print "start %02d" % count
             and only then write the
            camera.wait_recording(10) # Keep recording for 10 seconds
            stream.copy_to('motion%02d.h264' % count)
            print "stop %02d" % count
finally:
    camera.stop_recording()
