from piper import PiperVoice
import sounddevice as sd
import numpy as np

voice = PiperVoice.load("en_US-lessac-high.onnx")

text = "Hello Prakash. I am your personal AI assistant."

# Generate audio samples
audio = voice.synthesize(text)

# Convert to numpy array
samples = np.array(audio.audio_int16_array, dtype=np.int16)

# Play immediately
sd.play(samples, samplerate=audio.sample_rate)
sd.wait()