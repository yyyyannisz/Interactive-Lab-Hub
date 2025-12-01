
import time
import os

# ---------------------------------------------------
# Play .wav files directly (you will upload each file)
# ---------------------------------------------------
def play_audio(filename):
    print(f"Playing: {filename}")
    os.system(f"aplay {filename}")

# ---------------------------------------------------
# MAIN FOCUS TIMER
# ---------------------------------------------------
def run_focus_timer():
    # Step 1 — Play start + ask-task messages
    play_audio("start.wav")       # “Let's begin! Start this 30-minute focus with me…”
    play_audio("ask_task.wav")    # “First, tell me what you want to work on today.”

    # Step 2 — Read user reply (later replace with STT)
    try:
        task = input("User says: ").strip()
    except:
        task = ""

    # Step 3 — Confirm (different audio depending on whether task exists)
    if task:
        play_audio("confirm_task.wav")
    else:
        play_audio("confirm_generic.wav")

    # Step 4 — Start 30-minute timer
    total_seconds = 30 * 60
    five_min_warning_given = False

    while total_seconds > 0:
        time.sleep(1)
        total_seconds -= 1

        # 5-minute remaining point = 300 seconds
        if total_seconds == 5 * 60 and not five_min_warning_given:
            five_min_warning_given = True

            # Before sound → soft quack
            play_audio("soft_quack.wav")

            # After sound
            play_audio("notice.wav")           # your 5-min chime
            play_audio("five_min_left.wav")    # “Only 5 minutes left. Stay with me…”

    # Step 5 — Session complete messages
    if task:
        play_audio("finish_task.wav")
    else:
        play_audio("finish_generic.wav")

# ---------------------------------------------------
# RUN
# ---------------------------------------------------
if __name__ == "__main__":
    run_focus_timer()

