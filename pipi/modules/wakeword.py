import struct
import pvporcupine
import pyaudio

class DualWakeWordDetector:
    def __init__(self, access_key_hi, keyword_path_hi, access_key_bye, keyword_path_bye):
        """
        access_key_hi: your Picovoice access key for 'hi' wake word
        keyword_path_hi: path to your 'hi' .ppn file (e.g. 'assets/hi.ppn')
        access_key_bye: your Picovoice access key for 'bye' wake word
        keyword_path_bye: path to your 'bye' .ppn file (e.g. 'assets/bye.ppn')
        """
        self.access_key_hi = access_key_hi
        self.keyword_path_hi = keyword_path_hi
        self.access_key_bye = access_key_bye
        self.keyword_path_bye = keyword_path_bye
        self.porcupine_hi = None
        self.porcupine_bye = None
        self.pa = None
        self.stream = None

    def start(self):
        """Initialize Porcupine instances and open the microphone stream"""
        self.porcupine_hi = pvporcupine.create(
            access_key=self.access_key_hi,
            keyword_paths=[self.keyword_path_hi]
        )
        self.porcupine_bye = pvporcupine.create(
            access_key=self.access_key_bye,
            keyword_paths=[self.keyword_path_bye]
        )

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine_hi.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine_hi.frame_length,
        )

    def listen(self, non_blocking=False):
        """Block until one of the wake words is detected"""
        if not self.porcupine_hi or not self.porcupine_bye:
            self.start()

        print("Listening for wake words...")

        while True:
            if non_blocking:
                try:
                    pcm = self.stream.read(self.porcupine_hi.frame_length, exception_on_overflow=False)
                except IOError:
                    return None
            else:
                pcm = self.stream.read(self.porcupine_hi.frame_length, exception_on_overflow=False)

            pcm = struct.unpack_from("h" * self.porcupine_hi.frame_length, pcm)
            result_hi = self.porcupine_hi.process(pcm)
            result_bye = self.porcupine_bye.process(pcm)
            if result_hi >= 0:
                print("Wake word 'hi' detected!")
                return "hi"  # return control to main.py with 'hi'
            if result_bye >= 0:
                print("Wake word 'bye' detected!")
                return "bye"  # return control to main.py with 'bye'

    def stop(self):
        """Clean up resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine_hi:
            self.porcupine_hi.delete()
        if self.porcupine_bye:
            self.porcupine_bye.delete()