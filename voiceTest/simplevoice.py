import pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty("voices")

# Change index after listing available voices
engine.setProperty("voice", voices[1].id)

engine.setProperty("rate", 250)
engine.setProperty("volume", 1.0)

engine.say("Hello, I am your AI assistant. fuck you mother fucker , sone of a bitch , lick my pussy")
engine.runAndWait()