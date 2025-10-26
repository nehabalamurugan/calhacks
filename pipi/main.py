from modules.wakeword import DualWakeWordDetector
import cv2
from picamera2 import Picamera2

ACCESS_KEY_HI = "XSArA+g6/iL1DzbxjNl5Jophef8aWqfhyc899ZddK40AJWqdoptdbw=="  # replace with your actual key for "hi"
KEYWORD_PATH_HI = "assets/hi.ppn"  # adjust to where your .ppn file for "hi" actually is

ACCESS_KEY_BYE = "uJLCkob+AhUu+De449z0Bmr7ItnjE54/xRBrsr4UWsDtq9Wk+bIMlw=="  # replace with your actual key for "bye"
KEYWORD_PATH_BYE = "assets/bye.ppn"  # adjust to where your .ppn file for "bye" actually is

def main():
    detector = DualWakeWordDetector(
        access_key_hi=ACCESS_KEY_HI,
        keyword_path_hi=KEYWORD_PATH_HI,
        access_key_bye=ACCESS_KEY_BYE,
        keyword_path_bye=KEYWORD_PATH_BYE,
    )

    picam2 = None
    try:
        while True:
            # Wait for either wake word
            word = detector.listen()
            if word == "hi":
                if picam2 is None:
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
                        # Also check if "bye" is detected while streaming
                        detected_word = detector.listen(non_blocking=True)
                        if detected_word == "bye":
                            break

                    picam2.stop()
                    cv2.destroyAllWindows()
                    picam2 = None
                    print("🛑 Camera stream stopped. Returning to listening.")
            elif word == "bye":
                if picam2 is not None:
                    picam2.stop()
                    cv2.destroyAllWindows()
                    picam2 = None
                    print("🛑 Camera stream stopped. Returning to listening.")

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        detector.stop()
        if picam2 is not None:
            picam2.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()