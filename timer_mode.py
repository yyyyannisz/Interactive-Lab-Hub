
import time
import os
#import pyaudio
#import json
#from vosk import Model, KaldiRecognizer

# ---------------------------------------------------
# Play .wav files directly (you will upload each file)
# ---------------------------------------------------
def play_audio(filename):
    print(f"Playing: {filename}")
    os.system(f"aplay {filename}")

# ---------------------------------------------------
# MAIN FOCUS TIMER
# ---------------------------------------------------
def listen_for_task():
    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8000
    )
    stream.start_stream()

    print("Listening for task... speak now.")

    spoken_text = ""

    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            spoken_text = result.get("text", "")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    if len(spoken_text.strip()) == 0:
        return None
    return spoken_text


def run_focus_timer():
    # Step 1 — Play start + ask-task messages
    play_audio("start.wav")       # “Let's begin! Start this 30-minute focus with me…”

    # Step 4 — Start 45-sec timer
    total_seconds = 45
    five_min_warning_given = False

    while total_seconds > 0:
        time.sleep(1)
        total_seconds -= 1

        # 5-minute remaining point = 20 seconds
        if total_seconds == 20 and not five_min_warning_given:
            five_min_warning_given = True

            # Before sound → soft quack
            play_audio("soft_quack.wav")

            # After sound
            play_audio("notice.wav")           # your 5-min chime
            play_audio("five_min_left.wav")    # “Only 5 minutes left. Stay with me…”

    # Step 5 — Session complete messages
    play_audio("finish_generic.wav")

# ---------------------------------------------------
# RUN
# ---------------------------------------------------
if __name__ == "__main__":
    run_focus_timer()

