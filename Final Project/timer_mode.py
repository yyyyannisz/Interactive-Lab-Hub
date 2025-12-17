import time
import json
import pyaudio
import os
import threading

import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter
from vosk import Model, KaldiRecognizer


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VOSK_MODEL_PATH = "/home/pi/vosk-models/vosk-model-small-en-us-0.15"

if not os.path.exists(os.path.join(VOSK_MODEL_PATH, "conf", "model.conf")):
    raise RuntimeError(f"Vosk model not found at {VOSK_MODEL_PATH}")

# Load model ONCE
VOSK_MODEL = Model(VOSK_MODEL_PATH)


# ---------------------------------------------------
# Audio helper
# ---------------------------------------------------
def play_audio(filename):
    audio_path = os.path.join("audios", filename)
    print(f"[Playing audio: {audio_path}]")
    os.system(f"aplay {audio_path}")

# ---------------------------------------------------
# Speech recognition (single listening)
# ---------------------------------------------------
def listen_for_speech(prompt_wav=None, timeout=6):

    if prompt_wav:
        play_audio(prompt_wav)

    recognizer = KaldiRecognizer(VOSK_MODEL, 16000)

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

    return spoken_text.strip()


# ---------------------------------------------------
# Phone detection thread (5-second continuous rule)
# ---------------------------------------------------
def phone_detection_loop(stop_event, shared_state):
    MODEL_PATH = "models/phone_detection/model.tflite"
    LABELS_PATH = "models/phone_detection/labels.txt"

    CONF_THRESHOLD = 0.95
    TIME_THRESHOLD = 5.0  # seconds

    labels = []
    with open(LABELS_PATH, "r") as f:
        for line in f:
            labels.append(line.strip().split()[1].lower())

    interpreter = Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    H = input_details[0]["shape"][1]
    W = input_details[0]["shape"][2]

    cap = cv2.VideoCapture(0)

    phone_start_time = None

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            continue

        img = cv2.resize(frame, (W, H))
        img = np.expand_dims(img, axis=0).astype(np.uint8)

        interpreter.set_tensor(input_details[0]["index"], img)
        interpreter.invoke()

        preds = interpreter.get_tensor(output_details[0]["index"])[0]
        scores = preds / 255.0

        phone_score = scores[labels.index("phone")]
        now = time.time()

        if phone_score >= CONF_THRESHOLD:
            if phone_start_time is None:
                phone_start_time = now
            elif now - phone_start_time >= TIME_THRESHOLD:
                shared_state["phone_detected"] = True
                shared_state["phone_should_remind"] = True
        else:
            phone_start_time = None

        time.sleep(0.2)

    cap.release()


# ---------------------------------------------------
# MAIN INTERACTIVE CYBERDUCK TIMER
# ---------------------------------------------------
def run_focus_timer():

    play_audio("soft_quack.wav")
    task = listen_for_speech("ask_task.wav")

    if not task or len(task.split()) < 2:
        play_audio("task_not_understood.wav")
    else:
        play_audio("task_confirm.wav")

    length_text = listen_for_speech("ask_length.wav")

    if "short" in length_text:
        total_seconds = 30
        play_audio("session_short.wav")
    elif "long" in length_text:
        total_seconds = 60
        play_audio("session_long.wav")
    else:
        total_seconds = 45
        play_audio("session_medium.wav")

    play_audio("breath_intro.wav")
    time.sleep(1)
    play_audio("inhale.wav")
    time.sleep(2)
    play_audio("exhale.wav")
    time.sleep(2)
    play_audio("breath_complete.wav")

    play_audio("focus_start.wav")

    # ---------------------------
    # Start phone detection thread
    # ---------------------------
    shared_state = {
        "phone_detected": False,
        "phone_should_remind": False,
        "reminder_given": False
    }

    stop_event = threading.Event()
    detector_thread = threading.Thread(
        target=phone_detection_loop,
        args=(stop_event, shared_state),
        daemon=True
    )
    detector_thread.start()

    encouragement_given = False

    # ---------------------------
    # Timer loop
    # ---------------------------
    while total_seconds > 0:
        time.sleep(1)
        total_seconds -= 1

        # Phone reminder (once, after 5s continuous detection)
        if shared_state["phone_should_remind"] and not shared_state["reminder_given"]:
            play_audio("stay_focused.wav")
            shared_state["reminder_given"] = True
            shared_state["phone_should_remind"] = False

        # Mid-session encouragement
        if total_seconds == 30 and not encouragement_given:
            encouragement_given = True
            play_audio("encouragement.wav")

        # Final countdown
        if total_seconds == 5:
            play_audio("notice.wav")
            play_audio("final_push.wav")

    # ---------------------------
    # End session
    # ---------------------------
    stop_event.set()
    detector_thread.join(timeout=1)

    play_audio("session_complete.wav")

    if shared_state["phone_detected"]:
        recap = listen_for_speech("recap_prompt.wav", timeout=6)
    
        # We don’t parse the content — just acknowledge
        play_audio("recap_feedback.wav")

    play_audio("soft_quack.wav")


# ---------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------
if __name__ == "__main__":
    run_focus_timer()

