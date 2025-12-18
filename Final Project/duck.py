# ========== IMPORTS ==========
from google import genai
from google.genai import types
import sounddevice as sd
import queue
from vosk import Model, KaldiRecognizer
import json
import subprocess
import threading
import board
from adafruit_apds9960.apds9960 import APDS9960
import time
import os
from gtts import gTTS
import pyaudio
import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter

# ========== GEMINI SETUP ==========
# TODO: Paste your Google API Key here
GOOGLE_API_KEY = "AIzaSyAU_jF7Qup2Sgczd03utbZo6dosrvMcKOo"

client = genai.Client(api_key=GOOGLE_API_KEY)

# 'helper_chat' remembers the conversation while in helper mode
helper_chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a calm, thoughtful assistant who helps people think clearly. Keep replies concise.",
        temperature=0.7
    )
)

# ========== OLD SPEECH RECOGNITION SETUP (KEPT FOR HELPER MODE) ==========
# The old helper mode still uses sounddevice and a queue, so we'll keep this.
q = queue.Queue()

def callback(indata, frames, time_, status):
    if status:
        print(status)
    q.put(bytes(indata))

print("Loading Vosk model...")
model = Model(lang="en-us")
device_info = sd.query_devices(None, "input")
samplerate = int(device_info["default_samplerate"])

# ===================================================
# VOLUME CONTROL UTILITY
# ===================================================
def set_volume(percentage):
    """Sets the ALSA master volume to a percentage (e.g., '50%')."""
    try:
        subprocess.run(["amixer", "sset", "Master", f"{percentage}%"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        try:
            subprocess.run(["amixer", "sset", "PCM", f"{percentage}%"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Warning: Could not set volume using amixer. Error: {e}")

# ========== TEXT-TO-SPEECH (gTTS) ==========
def speak(text):
    print(f"Assistant speaking: {text}")
    set_volume(100) 
    
    try:
        tts = gTTS(text=text, lang='en', tld='com.au', slow=False)
        filename = "/tmp/temp_voice.mp3"
        tts.save(filename)
        subprocess.run(["mpg123", "-q", filename], check=False)
        
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        print(f"gTTS Error: {e}")
        subprocess.run(["espeak", "-a", "80", "-s", "150", text], check=False)
        
    finally:
        set_volume(100) 

# ---------------------------------------------------
# Play WAV audio
# ---------------------------------------------------
def play_audio(filename):
    """Play .wav files directly using aplay with fixed volume."""
    audio_path = os.path.join("audios", filename)
    print(f"[Playing audio: {audio_path}]")
    if os.path.exists(audio_path):
        try:
            subprocess.run(["aplay", "-D", "default", "-V", "50", audio_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
             print("Warning: Volume control failed for aplay, playing without volume flag.")
             os.system(f"aplay {audio_path}")
    else:
        print(f"Warning: {audio_path} not found.")
        speak(f"Audio file {filename.replace('.wav', '')} not found.")

# ---------------------------------------------------
# SPEECH RECOGNITION (single listening)
# ---------------------------------------------------
def listen_for_speech(prompt_wav=None, timeout=6):
    if prompt_wav:
        play_audio(prompt_wav)

    print("Listening... (Speak now)")
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
            
            if result.get("text", ""):
                 spoken_text = result.get("text", "")
                 if len(spoken_text.split()) > 0:
                     time.sleep(0.5) 
                     break 

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("User said:", spoken_text)
    return spoken_text.strip()

# ========== AI FUNCTIONS ==========
def ask_gemini_chat(message):
    """Sends message to the helper chat history."""
    try:
        response = helper_chat.send_message(message)
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "I'm having trouble connecting to the brain."

# ---------------------------------------------------
# PHONE DETECTION THREAD (5-second continuous rule)
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
# MAIN INTERACTIVE CYBERDUCK TIMER WITH PHONE DETECTION
# ---------------------------------------------------
def run_focus_timer():
    # ---------------------------------------------------
    # 1. Ask for task
    # ---------------------------------------------------
    play_audio("soft_quack.wav") 
    task = listen_for_speech("ask_task.wav") 

    if not task or len(task.split()) < 2:
        play_audio("task_not_understood.wav")
    else:
        play_audio("task_confirm.wav")

    # ---------------------------------------------------
    # 2. Ask for session length
    # ---------------------------------------------------
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

    # ---------------------------------------------------
    # 3. Calming breathing ritual
    # ---------------------------------------------------
    play_audio("breath_intro.wav")
    time.sleep(1)
    play_audio("inhale.wav")
    time.sleep(2)
    play_audio("exhale.wav")
    time.sleep(2)
    play_audio("breath_complete.wav")

    # ---------------------------------------------------
    # Start focus session
    # ---------------------------------------------------
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

    # ---------------------------------------------------
    # TIMER LOOP
    # ---------------------------------------------------
    while total_seconds > 0:
        time.sleep(1)
        total_seconds -= 1

        # Phone reminder (once, after 5s continuous detection)
        if shared_state["phone_should_remind"] and not shared_state["reminder_given"]:
            play_audio("notice.wav")
            play_audio("stay_focus.wav")
            shared_state["reminder_given"] = True
            shared_state["phone_should_remind"] = False

        # Mid-session encouragement
        if total_seconds == 30 and not encouragement_given:
            encouragement_given = True
            play_audio("notice.wav")
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

    # If phone was detected during session, ask for recap
    if shared_state["phone_detected"]:
        recap = listen_for_speech("recap_prompt.wav", timeout=6)
        play_audio("recap_feedback.wav")

    play_audio("soft_quack.wav")
    
    print("Focus timer complete!")

# ========== GESTURE SENSOR SETUP ==========
i2c = board.I2C()
apds = APDS9960(i2c)
apds.enable_proximity = True
apds.enable_gesture = True

assistant_mode = "waiting"

def gesture_listener():
    global assistant_mode
    while True:
        try:
            gesture = apds.gesture()
            if gesture == 0x01:  # UP gesture
                if assistant_mode != "timer":
                    assistant_mode = "timer"
                    print("Gesture: UP -> Timer mode")
                    speak("Timer mode activated!")
            elif gesture == 0x02:  # DOWN gesture
                if assistant_mode != "help":
                    assistant_mode = "help"
                    print("Gesture: DOWN -> Problem-solving mode")
                    speak("Problem solving mode activated.")
            time.sleep(0.1)
        except OSError:
            pass

threading.Thread(target=gesture_listener, daemon=True).start()

# ========== SELECTION WINDOW ==========
speak("System ready. You have 20 seconds to select a mode. Gesture Up for Timer, Down for Help.")
print("Waiting for selection (20s)...")

start_wait = time.time()
while time.time() - start_wait < 20:
    if assistant_mode != "waiting":
        break
    time.sleep(0.1)

if assistant_mode == "waiting":
    speak("No selection made. Defaulting to Timer mode.")
    assistant_mode = "timer"

# ========== MAIN INTERACTION ==========
while True:
    print(f"[{assistant_mode.upper()} MODE] Listening... (timeout after 6 seconds of silence/speech)")
    
    if assistant_mode == "timer":
        run_focus_timer()
        assistant_mode = "help"
        speak("Timer complete. Switching to helper mode.")
        continue
    
    LISTENING_TIMEOUT = 6 
    
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype="int16",
                           channels=1, callback=callback):
        rec = KaldiRecognizer(model, samplerate)
        user_input = ""
        listening = True
        start_time = time.time()
        
        while listening:
            if time.time() - start_time > LISTENING_TIMEOUT:
                listening = False
                break
                
            try:
                data = q.get(timeout=0.1) 
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    
                    if text:
                        print("You said:", text)
                        user_input += text + " "
                        start_time = time.time() 
                        
            except queue.Empty:
                pass
            
            if assistant_mode == "timer":
                listening = False
                break

    clean_input = user_input.strip()

    if clean_input and assistant_mode == "help":
        print(f"Sending to helper chat: {clean_input}")
        answer = ask_gemini_chat(clean_input)
        answer = answer.replace("*", "") 
        print("Assistant:", answer)
        speak(answer)
    
    time.sleep(0.5)