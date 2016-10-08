import io
import datetime
import numpy as np
import picamera
import picamera.array

class DetectMotion(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, stream):
        super(DetectMotion, self).__init__(camera)
        self.stream = stream
        self.recording = False
    def analyze(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        if (a > 60).sum() > 10:# If there're more than 10 vectors with a magnitude greater than 60, then say we've detected motion
            print('%s' % datetime.datetime.now())
            # if not self.recording:
            #     self.recording = True
            #     filename = 'motion-%s.h264' % datetime.datetime.now().isoformat()
            #     print('saving: %s' % filename)
            #     camera.wait_recording(10) # Keep recording for 10 seconds
            #     self.stream.copy_to(filename)
            #     print('saved: %s' % filename)
            #     self.recording = False

camera = picamera.PiCamera()
stream = picamera.PiCameraCircularIO(camera, seconds=20)
camera.resolution = (1280, 720)
camera.rotation = 180
camera.start_recording(stream, format='h264', motion_output=DetectMotion(camera, stream))

try:
    while True:
        camera.wait_recording(1)
finally:
    camera.stop_recording()
