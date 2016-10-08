# import io
# import random
import datetime
import numpy as np
import picamera
import picamera.arrays

self.camera.start_recording('captures/video-%s.h264' % , use_video_port=True)

class DetectMotion(picamera.array.PiMotionAnalysis):
    def __init__(self, camera):
        super(MyMotionDetector, self).__init__(camera)
    def analyze(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 60).sum() > 10:
            print('motion')
            camera.wait_recording(10) # Keep recording for 10 seconds
            print('saving...')
            stream.copy_to('motion-%s.h264' % datetime.datetime.now().isoformat())
            print('saved!')

with picamera.PiCamera() as camera:
    with picamera.PiCameraCircularIO(camera, seconds=20) as stream
        with DetectMotion(camera) as output:
            camera.resolution = (640, 480)
            camera.start_recording(stream, format='h264', motion_output=output(camera))
            # camera.wait_recording(30)
            # camera.stop_recording()
