import io
import random
import picamera

def motion_detected():
    # Randomly return True (like a fake motion detection routine)
    return random.randint(0, 10) == 0

class MotionDetector(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, handler):
        super(MyMotionDetector, self).__init__(camera)
        self.handler = handler
        self.first = True

    def analyse(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)
        if (a > 60).sum() > 50:
            # Ignore the first detection
            if self.first:
                self.first = False
                return
            self.handler.motion_detected()

camera = picamera.PiCamera()
stream = picamera.PiCameraCircularIO(camera, seconds=20)
camera.start_recording(stream, format='h264',motion_output=MotionDetector(camera, handler))
try:
    while True:
        camera.wait_recording(1)
        if motion_detected():
            # Keep recording for 10 seconds and only then write the
            # stream to disk
            camera.wait_recording(10)
            stream.copy_to('motion.h264')
finally:
    camera.stop_recording()

                camera.start_recording(
                    '/dev/null', format='h264',

                )
