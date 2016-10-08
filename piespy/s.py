import io
import datetime
import numpy as np
import picamera
import picamera.array

class DetectMotion(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, stream):
        super(DetectMotion, self).__init__(camera)
        self.stream = stream
    def analyze(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 60).sum() > 10:
            print('motion %s' % datetime.datetime.now().isoformat())
            camera.wait_recording(5) # Keep recording for 10 seconds
            print('saving...')
            self.stream.copy_to('motion-%s.h264' % datetime.datetime.now().isoformat())
            print('saved!')

with picamera.PiCamera() as camera:
    with picamera.PiCameraCircularIO(camera, seconds=20) as stream:
        # with DetectMotion(camera) as output:
        camera.resolution = (640, 480)
        camera.start_recording(stream, format='h264', motion_output=DetectMotion(camera, stream))
        camera.wait_recording(15)
        camera.stop_recording()
