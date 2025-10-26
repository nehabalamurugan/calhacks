import struct
import pvporcupine
import pyaudio

class WakeWordDetector:
    def __init__(self, access_key, keyword_path):
        """
        access_key: your Picovoice access key
        keyword_path: path to your .ppn file (e.g. 'assets/hi.ppn')
        """
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.porcupine = None
        self.pa = None
        self.stream = None

    def start(self):
        """Initialize Porcupine and open the microphone stream"""
        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=[self.keyword_path]
        )

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
        )

    def listen(self):
        """Block until the wake word is detected"""
        if not self.porcupine:
            self.start()

        print("Listening for wake word...")

        while True:
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            result = self.porcupine.process(pcm)
            if result >= 0:
                print("Wake word detected!")
                return True  # return control to main.py

    def stop(self):
        """Clean up resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()