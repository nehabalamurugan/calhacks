from modules.wakeword import WakeWordDetector
import cv2
from picamera2 import Picamera2

ACCESS_KEY = "XSArA+g6/iL1DzbxjNl5Jophef8aWqfhyc899ZddK40AJWqdoptdbw=="  # replace with your actual key
KEYWORD_PATH = "assets/hi.ppn"  # adjust to where your .ppn file actually is

def main():
    detector = WakeWordDetector(ACCESS_KEY, KEYWORD_PATH)

    try:
        # Wait for the wake word
        detector.listen()

        # Once heard, open a camera stream using picamera2
        picam2 = Picamera2()
        config = picam2.create_video_configuration(main={"format": "RGB888", "size": (1920, 1080)}, controls={"FrameDurationLimits": (33333, 33333)})
        picam2.configure(config)
        picam2.set_controls({"AfMode": 2, "AeEnable": True, "AwbEnable": True})
        picam2.start()

        print("✅ Camera stream started. Press 'q' to quit.")
        cv2.namedWindow("Camera Stream", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Camera Stream", 960, 540)
        while True:
            frame = picam2.capture_array()
            cv2.imshow("Camera Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        picam2.stop()
        cv2.destroyAllWindows()

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        detector.stop()

if __name__ == "__main__":
    main()