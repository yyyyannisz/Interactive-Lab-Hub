# cyberduck_timer.py
import time
from PIL import Image, ImageDraw, ImageFont
import threading

class CyberDuckTimer:
    def __init__(self, display, speak_func, play_sound_func,
                 quack_sound, notice_sound):
        self.display = display
        self.speak = speak_func
        self.play_sound = play_sound_func
        
        self.quack_sound = quack_sound
        self.notice_sound = notice_sound

        self.task = None
        self.running = False
        self.start_time = None
        self.remaining = 30 * 60  # 30 minutes default

        # fonts (adjust path depending on Pi)
        self.font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

    # -------------------------------
    # ENTRY POINT
    # -------------------------------
    def start_mode(self):
        self.speak("Let’s begin! Start this 30-minute focus with me. First, tell me what you want to work on today.")
        self.task = self.get_user_task()

        if self.task:
            self.speak(f"Got it. I’ll stay with you while you work on {self.task}. Let’s go!")
        else:
            self.speak("Got it. I’ll stay with you while you get things done. Let’s go!")

        self.running = True
        self.start_time = time.time()

        thread = threading.Thread(target=self.timer_loop)
        thread.start()

        self.ui_loop()  # stays in UI loop

    # -------------------------------
    # GET USER TASK  (replace later with STT)
    # -------------------------------
    def get_user_task(self):
        # TEMP: use input — replace with Whisper/Vosk later
        try:
            return input("What do you want to work on? ").strip()
        except:
            return None

    # -------------------------------
    # TIMER COUNTDOWN LOGIC
    # -------------------------------
    def timer_loop(self):
        five_min_notified = False

        while self.running:
            elapsed = int(time.time() - self.start_time)
            self.remaining = 30*60 - elapsed

            if self.remaining <= 5*60 and not five_min_notified:
                five_min_notified = True
                self.play_sound(self.quack_sound)  # soft quack
                self.play_sound(self.notice_sound)
                self.speak("Only 5 minutes left. Stay with me—you're almost done!")

            if self.remaining <= 0:
                self.running = False
                self.finish_session()
                break

            time.sleep(1)

    # -------------------------------
    # UI LOOP (ST7789)
    # -------------------------------
    def ui_loop(self):
        while self.running:
            img = Image.new("RGB", (240, 240), "white")
            draw = ImageDraw.Draw(img)

            # Title
            draw.text((20, 10), "Focus Timer", fill="black", font=self.font_small)

            # Countdown MM:SS
            mins = max(self.remaining, 0) // 60
            secs = max(self.remaining, 0) % 60
            timer_str = f"{mins:02d}:{secs:02d}"
            draw.text((60, 90), timer_str, fill="black", font=self.font_big)

            # Task label
            if self.task:
                draw.text((20, 180), f"Task: {self.task}", fill="black", font=self.font_small)
            else:
                draw.text((20, 180), "Task: (none)", fill="gray", font=self.font_small)

            self.display.show_image(img)
            time.sleep(0.2)

    # -------------------------------
    # FINAL MESSAGE
    # -------------------------------
    def finish_session(self):
        if self.task:
            final_msg = f"Great job! You just spent 30 minutes with me working on {self.task}. I’m proud of you—nice focus!"
        else:
            final_msg = "Great job! You just completed 30 minutes of focus time with me. I’m proud of you—nice focus!"

        self.speak(final_msg)

        # Show final screen
        img = Image.new("RGB", (240, 240), "white")
        draw = ImageDraw.Draw(img)
        draw.text((20, 100), "Session Complete!", fill="black", font=self.font_small)
        self.display.show_image(img)
