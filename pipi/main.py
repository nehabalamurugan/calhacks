from modules.wakeword import WakeWordDetector
import cv2

ACCESS_KEY = "XSArA+g6/iL1DzbxjNl5Jophef8aWqfhyc899ZddK40AJWqdoptdbw=="  # replace with your actual key
KEYWORD_PATH = "assets/hi.ppn"  # adjust to where your .ppn file actually is

def main():
    detector = WakeWordDetector(ACCESS_KEY, KEYWORD_PATH)

    try:
        # Wait for the wake word
        detector.listen()

        # Once heard, open a camera stream
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open camera")
            return

        print("✅ Camera stream started. Press 'q' to quit.")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Camera Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        detector.stop()

if __name__ == "__main__":
    main()