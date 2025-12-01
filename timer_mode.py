import time
import threading

class CyberDuckTimer:
    def __init__(self, speak_function, play_sound_function, quack_sound_path, notice_sound_path):
        self.speak = speak_function
        self.play_sound = play_sound_function
        self.quack_sound_path = quack_sound_path
        self.notice_sound_path = notice_sound_path
        self.task = None
        self.timer_thread = None
        self.is_running = False

    def start(self):
        print("Timer mode started")

        # Step 1 — Duck greets & asks question
        self.speak("Let’s begin! Start this 30-minute focus with me. First, tell me what you want to work on today.")

        # Step 2 — Capture user’s reply (voice or text)
        self.task = self.get_user_task()

        # Step 3 — Duck responds
        if self.task:
            self.speak(f"Got it. I’ll stay with you while you work on {self.task}. Let’s go!")
        else:
            self.speak("Got it. I’ll stay with you while you get things done. Let’s go!")

        # Start timer thread
        self.timer_thread = threading.Thread(target=self.run_timer)
        self.timer_thread.start()

    def get_user_task(self):
        """
        Placeholder:
        Replace this function with actual STT or text input.
        """
        print("Waiting for user response...")
        try:
            user_input = input("User says: ").strip()
            return user_input if len(user_input) > 0 else None
        except:
            return None

    def run_timer(self):
        self.is_running = True
        total_seconds = 30 * 60   # 30 minutes

        while total_seconds > 0 and self.is_running:
            time.sleep(1)
            total_seconds -= 1

            # At 5-minute mark (300 seconds)
            if total_seconds == 5 * 60:
                self.speak_soft_quack()
                self.play_notice_and_message()

        if self.is_running:  
            self.finish_session()

    def speak_soft_quack(self):
        # soft quack sound before the notice
        print("Playing soft quack...")
        self.play_sound(self.quack_sound_path)

    def play_notice_and_message(self):
        # Play the 5-min warning sound
        print("Playing notice sound...")
        self.play_sound(self.notice_sound_path)

        # Speak the 5-minute warning message
        self.speak("Only 5 minutes left. Stay with me—you're almost done!")

    def finish_session(self):
        # Final congratulation message
        if self.task:
            self.speak(f"Great job! You just spent 30 minutes with me working on {self.task}. I’m proud of you—nice focus!")
        else:
            self.speak("Great job! You just completed 30 minutes of focus time with me. I’m proud of you—nice focus!")

        self.is_running = False

    def stop(self):
        self.is_running = False
        self.speak("Timer canceled.")
