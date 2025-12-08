import time
import json
import pyaudio
import os
from vosk import Model, KaldiRecognizer


# ---------------------------------------------------
# Play WAV audio instead of text output
# ---------------------------------------------------
def play_audio(filename):
    print(f"[Playing audio: {filename}]")
    os.system(f"aplay {filename}")


# ---------------------------------------------------
# SPEECH RECOGNITION (single listening)
# ---------------------------------------------------
def listen_for_speech(prompt_wav=None, timeout=6):

    # prompt_wav should be a filename (e.g., "ask_task.wav")
    if prompt_wav:
        play_audio(prompt_wav)

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
    # 1. Ask for task
    # ---------------------------------------------------
    play_audio("soft_quack.wav") 
    task = listen_for_speech("ask_task.wav")  
    # ask_task.wav → "What are you focusing on today?"

    if not task or len(task.split()) < 2:
        play_audio("task_not_understood.wav")
        # task_not_understood.wav → "Sorry, I didn't catch that, but let's focus anyway!"
    else:
        play_audio("task_confirm.wav")
        # task_confirm.wav → "Got it! I'll help you stay focused."

    if len(task.split()) > 6:
        play_audio("task_ambitious.wav")
        # task_ambitious.wav → "Wow, that's an ambitious task. Let's crush it!"
    else:
        play_audio("task_simple.wav")
        # task_simple.wav → "Nice and simple. I like it."

    # ---------------------------------------------------
    # 2. Ask for session length
    # ---------------------------------------------------
    length_text = listen_for_speech("ask_length.wav")
    # ask_length.wav → "Would you like a short, medium, or long focus session?"

    if "short" in length_text:
        total_seconds = 30
        play_audio("session_short.wav")
        # session_short.wav → "Short session selected!"
    elif "medium" in length_text:
        total_seconds = 45
        play_audio("session_medium.wav")
        # session_medium.wav → "Medium session selected!"
    elif "long" in length_text:
        total_seconds = 60
        play_audio("session_long.wav")
        # session_long.wav → "Long session selected! Power mode!"
    else:
        total_seconds = 45
        play_audio("session_default_medium.wav")
        # session_default_medium.wav → "I’ll set a medium session for you."

    # ---------------------------------------------------
    # 3. Calming breathing ritual
    # ---------------------------------------------------
    play_audio("breath_intro.wav")
    # breath_intro.wav → "Before we begin, let's take one deep breath together."

    time.sleep(1)
    play_audio("inhale.wav")
    # inhale.wav → "Inhale..."

    time.sleep(2)
    play_audio("exhale.wav")
    # exhale.wav → "Exhale..."

    time.sleep(2)
    play_audio("breath_complete.wav")
    # breath_complete.wav → "Great. Now let's get focused."

    # ---------------------------------------------------
    # Start focus session
    # ---------------------------------------------------
    play_audio("focus_start.wav")
    # focus_start.wav → "Let's begin your focus sprint!"

    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8000,
                    input_device_index=2)

    stream.start_stream()

    encouragement_given = False
    checkin_done = False
    last_warning_time = 0
    warning_interval = 10  # seconds

    # ---------------------------------------------------
    # TIMER LOOP
    # ---------------------------------------------------
    while total_seconds > 0:
        time.sleep(1)
        total_seconds -= 1

        # Detect speech during focus session
        data = stream.read(4000, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            heard_text = result.get("text", "").strip()

            if len(heard_text.split()) > 1:
                if time.time() - last_warning_time > warning_interval:
                    play_audio("stay_focused.wav")
                    # stay_focused.wav → "Try to stay focused with me!"
                    last_warning_time = time.time()

        # Mid-session encouragement
        if total_seconds == 30 and not encouragement_given:
            encouragement_given = True
            play_audio("encouragement.wav")
            # encouragement.wav → "You're doing great! Keep going!"

        # Mid-session check-in
        if total_seconds == 25 and not checkin_done:
            checkin_done = True
            response = listen_for_speech("checkin_prompt.wav")
            # checkin_prompt.wav → "Are you still with me? Say yes!"

            if "yes" in response:
                play_audio("checkin_positive.wav")
                # checkin_positive.wav → "Awesome! Let's keep going!"
            else:
                play_audio("checkin_refocus.wav")
                # checkin_refocus.wav → "That's okay, let's refocus together."

        # Final countdown
        if total_seconds == 5:
            play_audio("notice.wav")
            play_audio("final_push.wav")
            # final_push.wav → "Five seconds left! Final push!"

    # End session
    stream.stop_stream()
    stream.close()
    p.terminate()

    play_audio("session_complete.wav")
    play_audio("soft_quack.wav")
    # session_complete.wav → "Focus session complete! Great job!"


# ---------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------
if __name__ == "__main__":
    run_focus_timer()
