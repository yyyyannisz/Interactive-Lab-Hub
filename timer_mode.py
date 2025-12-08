import os
os.environ["PULSE_SERVER"] = "127.0.0.1"
os.environ["ALSA_CONFIG_PATH"] = "/dev/null"
os.environ["ALSA_CONFIG_DIR"] = "/dev/null"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["VOSK_LOG_LEVEL"] = "-1"

import ctypes
try:
    ctypes.CDLL('libasound.so').snd_lib_error_set_handler(None)
except:
    pass

import time
import json
import pyaudio
from vosk import Model, KaldiRecognizer



# ---------------------------------------------------
# Simple text output instead of audio
# ---------------------------------------------------
def duck_say(text):
    print("CyberDuck:", text)


# ---------------------------------------------------
# SPEECH RECOGNITION
# ---------------------------------------------------
def listen_for_speech(prompt_text=None, timeout=6):

    if prompt_text:
        duck_say(prompt_text)

    print("Listening... (Speak now)")

    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8000)

    stream.start_stream()
    spoken_text = ""
    start_time = time.time()

    while time.time() - start_time < timeout:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            spoken_text = result.get("text", "")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("User said:", spoken_text)
    return spoken_text.strip()


# ---------------------------------------------------
# MAIN INTERACTIVE CYBERDUCK TIMER
# ---------------------------------------------------
def run_focus_timer():

    # ---------------------------------------------------
    # 1. Ask user for their task
    # ---------------------------------------------------
    task = listen_for_speech("What are you focusing on today?")

    if not task or len(task.split()) < 2:
        duck_say("Sorry, did not catch that, but let's focus anyway!")
    else:
        duck_say("Got it! I'll help you stay focused.")

    # Task complexity reaction
    if len(task.split()) > 6:
        duck_say("Wow, ambitious task! Let's crush it.")
    else:
        duck_say("Nice and simple. I love it.")

    # ---------------------------------------------------
    # 2. Ask user to choose duration
    # ---------------------------------------------------
    length_text = listen_for_speech(
        "Would you like a short, medium, or long session?"
    )

    if "short" in length_text:
        total_seconds = 30
        duck_say("Short session selected!")
    elif "medium" in length_text:
        total_seconds = 45
        duck_say("Medium session selected!")
    elif "long" in length_text:
        total_seconds = 60
        duck_say("Long session selected! Power mode!")
    else:
        total_seconds = 45
        duck_say("Defaulting to medium session.")

    # ---------------------------------------------------
    # 3. Start focusing
    # ---------------------------------------------------
    duck_say("Let's begin your focus sprint!")

    # Recognizer for detecting speech during timer
    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8000)

    stream.start_stream()

    encouragement_given = False
    checkin_done = False

    # ---------------------------------------------------
    # TIMER LOOP
    # ---------------------------------------------------
    while total_seconds > 0:
        time.sleep(1)
        total_seconds -= 1

        # Listen for user talking during focus
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            duck_say("Hey, try to stay focused with me!")

        # Mid session encouragement
        if total_seconds == 30 and not encouragement_given:
            encouragement_given = True
            duck_say("You are doing great! Keep going!")

        # Mid session check-in
        if total_seconds == 25 and not checkin_done:
            checkin_done = True
            response = listen_for_speech("Are you still with me? Say yes!")
            if "yes" in response:
                duck_say("Yay! Let's keep going!")
            else:
                duck_say("That's okay, let's refocus together.")

        # Final countdown
        if total_seconds == 5:
            duck_say("Five seconds left! Final push!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    duck_say("Focus session complete! Great job!")


# ---------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------
if __name__ == "__main__":
    run_focus_timer()
