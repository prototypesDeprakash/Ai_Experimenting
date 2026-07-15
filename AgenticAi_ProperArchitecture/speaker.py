import pyttsx3
import threading
import queue

speech_queue = queue.Queue()

VOICE_INDEX = 1
RATE = 220
VOLUME = 1.0


def _make_engine():
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    if len(voices) > VOICE_INDEX:
        engine.setProperty("voice", voices[VOICE_INDEX].id)
    engine.setProperty("rate", RATE)
    engine.setProperty("volume", VOLUME)
    return engine


def speech_worker():
    # On Windows, SAPI5 needs COM initialized on this thread.
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except ImportError:
        pass  # not on Windows

    while True:
        text = speech_queue.get()

        if text is None:
            break

        # Recreate the engine each time — reusing one engine across
        # multiple runAndWait() calls is what causes pyttsx3 to only
        # speak the first message and then go silent.
        engine = _make_engine()
        engine.say(text)
        engine.runAndWait()
        try:
            engine.stop()
        except Exception:
            pass
        del engine


threading.Thread(target=speech_worker, daemon=True).start()


def speak(text):
    speech_queue.put(text)