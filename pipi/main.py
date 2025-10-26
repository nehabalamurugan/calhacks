from modules.wakeword import DualWakeWordDetector
import cv2
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import sounddevice as sd
import soundfile as sf
import threading
import os
from datetime import datetime
from modules.assemblyai_test import transcribe_audio
import time
print("hi")
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
    audio_recording = False
    audio_frames = []
    audio_thread = None
    stop_audio_event = threading.Event()

    os.makedirs("temp_storage", exist_ok=True)

    def audio_callback(indata, frames, time, status):
        if status:
            print(status)
        audio_frames.append(indata.copy())

    def record_audio():
        with sd.InputStream(samplerate=44100, channels=1, callback=audio_callback):
            stop_audio_event.wait()

    def capture_images(timestamp):
        for i in range(1, 4):
            time.sleep(5)
            image = picam2.capture_array()
            image_path = os.path.join("temp_storage", f"image_{timestamp}_{i}.jpg")
            cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            print(f"📸 Snapshot {i} saved to {image_path}")

    try:
        while True:
            # Wait for either wake word
            word = detector.listen()
            if word == "hi":
                if picam2 is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    picam2 = Picamera2()
                    config = picam2.create_video_configuration(main={"format": "RGB888", "size": (1920, 1080)})
                    picam2.configure(config)
                    picam2.start()

                    # Disable auto white balance and manually correct blue tint
                    picam2.set_controls({
                        "AwbEnable": False,
                        "ColourGains": (2.2, 1.0),  # Increase red, reduce blue
                        "Brightness": 0.0,
                        "Contrast": 1.2,
                        "Saturation": 1.4,
                    })
                    print("🎨 Manual white balance applied (red boosted, blue reduced).")

                    # Start video recording
                    video_path = os.path.join("temp_storage", f"video_{timestamp}.mp4")
                    encoder = H264Encoder()
                    picam2.start_recording(encoder, video_path)

                    # Start audio recording
                    audio_frames.clear()
                    stop_audio_event.clear()
                    audio_thread = threading.Thread(target=record_audio)
                    audio_thread.start()
                    audio_recording = True

                    # Start image capture thread
                    image_thread = threading.Thread(target=capture_images, args=(timestamp,))
                    image_thread.start()

                    print("✅ Recording started. Say 'bye' to stop.")

                # Wait for "bye" to stop recording
                while True:
                    detected_word = detector.listen(non_blocking=True)
                    if detected_word == "bye":
                        break

                # Stop recording
                if picam2 is not None and audio_recording:
                    picam2.stop_recording()

                    stop_audio_event.set()
                    audio_thread.join()
                    audio_recording = False

                    # Save audio file
                    audio_path = os.path.join("temp_storage", f"audio_{timestamp}.wav")
                    import numpy as np
                    audio_np = np.concatenate(audio_frames, axis=0)
                    sf.write(audio_path, audio_np, 44100)

                    picam2.stop()
                    try:
                        picam2.close()
                    except Exception:
                        pass
                    del picam2
                    picam2 = None

                    print(f"🛑 Recording stopped. Video saved to {video_path}, audio saved to {audio_path}. Returning to listening.")

                    transcript = transcribe_audio(audio_path)
                    print(f"Transcript:\n{transcript}")
                    transcript_path = os.path.join("temp_storage", f"transcript_{timestamp}.txt")
                    with open(transcript_path, "w") as f:
                        transcript_text = "\n".join([x["speaker"]+": "+x["text"] for x in transcript])
                        f.write(transcript_text)

            elif word == "bye":
                if picam2 is not None and audio_recording:
                    picam2.stop_recording()

                    stop_audio_event.set()
                    audio_thread.join()
                    audio_recording = False

                    audio_path = os.path.join("/home/babapi/calhacks/pipi/temp_storage", f"audio_{timestamp}.wav")
                    import numpy as np
                    audio_np = np.concatenate(audio_frames, axis=0)
                    sf.write(audio_path, audio_np, 44100)

                    picam2.stop()
                    try:
                        picam2.close()
                    except Exception:
                        pass
                    del picam2
                    picam2 = None

                    print(f"🛑 Recording stopped. Video saved to {video_path}, audio saved to {audio_path}. Returning to listening.")

                    transcript = transcribe_audio(audio_path)
                    print(f"Transcript:\n{transcript}")
                    transcript_path = os.path.join("/home/babapi/calhacks/pipi/temp_storage", f"transcript_{timestamp}.txt")
                    with open(transcript_path, "w") as f:
                        f.write(transcript)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        detector.stop()
        if picam2 is not None:
            if audio_recording:
                picam2.stop_recording()
                stop_audio_event.set()
                audio_thread.join()
            picam2.stop()
            try:
                picam2.close()
            except Exception:
                pass
            del picam2

if __name__ == "__main__":
    main()