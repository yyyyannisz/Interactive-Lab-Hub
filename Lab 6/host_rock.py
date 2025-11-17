import paho.mqtt.client as mqtt
import time
import board
import digitalio
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# ---------------- DISPLAY SETUP ----------------
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

BAUDRATE = 24000000
spi = board.SPI()

disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
    rotation=270,
)

if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

def show_text(text, color=(255, 255, 0)):
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    max_font_size = 24
    min_font_size = 16
    font_size = max_font_size

    while True:
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=4)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        if (tw <= width - 10 and th <= height - 10) or font_size <= min_font_size:
            break
        font_size -= 2

    x = (width - tw) // 2
    y = (height - th) // 2
    draw.multiline_text((x, y), text, font=font, fill=color, spacing=4, align="center")
    disp.image(image)


# ---------------- BUTTON SETUP ----------------
GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 17
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

moves = ["rock", "paper", "scissors"]
move_index = 0
current_move = moves[move_index]
host_submitted = False
host_choice_topic = "IDD/rps/choices/host"


def update_selection_screen():
    show_text(f"Host selecting:\n{current_move.upper()}", color=(0, 180, 255))


update_selection_screen()


def scan_host_button():
    """Short press cycles, long press submits host move."""
    global move_index, current_move, host_submitted

    if GPIO.input(BUTTON_PIN) == GPIO.LOW:
        press_start = time.time()
        while GPIO.input(BUTTON_PIN) == GPIO.LOW:
            time.sleep(0.01)
        press_duration = time.time() - press_start

        # Long press: submit host move
        if press_duration > 1.0:
            client.publish(host_choice_topic, current_move)
            show_text(f"Host submitted:\n{current_move.upper()}", color=(255, 255, 0))
            host_submitted = True
            time.sleep(1)
        else:
            # Short press: cycle choices
            move_index = (move_index + 1) % len(moves)
            current_move = moves[move_index]
            update_selection_screen()
            time.sleep(0.2)


# ---------------- GAME LOGIC (UNCHANGED) ----------------

show_text("Welcome\nRock-Paper-Scissors\nHost", color=(0, 180, 255))
time.sleep(5)
show_text("Waiting for\nplayers to join...", color=(255, 255, 0))

broker = "farlab.infosci.cornell.edu"
port = 1883
username = "idd"
password = "device@theFarm"

ROUND_DURATION = 10
MIN_PLAYERS = 2

choices = {}
active_players = set()
round_active = False
game_active = False
waiting_for_players = False

client = mqtt.Client()
client.username_pw_set(username, password)


def determine_winner(players_choices):
    unique_choices = set(players_choices.values())
    if len(unique_choices) == 1 or len(unique_choices) == 3:
        return None
    if unique_choices == {"rock", "scissors"}:
        return "rock"
    if unique_choices == {"scissors", "paper"}:
        return "scissors"
    if unique_choices == {"paper", "rock"}:
        return "paper"


def announce(message, color=(255, 255, 0)):
    print(message)
    show_text(message, color=color)
    client.publish("IDD/rps/status", message)


def on_message(client, userdata, msg):
    global round_active, choices, active_players, game_active, waiting_for_players
    player = msg.topic.split("/")[-1]
    choice = msg.payload.decode().strip().lower()

    if choice == "join":
        if player not in active_players:
            active_players.add(player)
            announce(f"{player} joined the game! ({len(active_players)} players now)")

            if not game_active:
                game_active = True
                waiting_for_players = True
                announce("New Rock-Paper-Scissors game starting!")
                announce("Waiting for players to join...")
                time.sleep(1)

            if waiting_for_players and len(active_players) >= MIN_PLAYERS:
                waiting_for_players = False
                announce("Enough players joined! Get ready to play...")
                time.sleep(2)
        return

    if choice == "quit":
        if player in active_players:
            active_players.remove(player)
            announce(f"{player} left the game. ({len(active_players)} players left)")
            if len(active_players) == 1:
                sole_player = list(active_players)[0]
                announce(f"Game Over! Champion: {sole_player}", color=(0, 255, 0))
                reset_game_prompt()
            elif len(active_players) < MIN_PLAYERS:
                waiting_for_players = True
                announce("Not enough players to continue. Waiting for new players...")
        return

    if choice not in ["rock", "paper", "scissors"]:
        return

    if not round_active:
        active_players.add(player)
        return

    choices[player] = choice
    active_players.add(player)


def start_round():
    global round_active, choices, waiting_for_players, host_submitted

    # Reset host submission for new round
    host_submitted = False

    # Host must be included as a player
    active_players.add("host")

    if waiting_for_players:
        announce("Waiting for enough players to join...")
        return True

    if len(active_players) < MIN_PLAYERS:
        waiting_for_players = True
        announce("Not enough players to continue. Waiting for new players...")
        return True

    choices.clear()
    round_active = True
    announce(f"New round! {ROUND_DURATION}s to play!")
    announce("Send your move: rock, paper, or scissors!")

    countdown = ROUND_DURATION
    while countdown > 0:
        scan_host_button()  # <-- Host selecting
        print(f"{countdown}s remaining...", end="\r")
        time.sleep(1)
        countdown -= 1

    round_active = False

    if not host_submitted:
        # Auto-submit last selected move
        client.publish(host_choice_topic, current_move)
        announce(f"Host auto-selected:\n{current_move.upper()}", color=(255, 255, 0))
        time.sleep(1)

    if not choices:
        announce("No moves this round. Waiting for players...")
        return True

    winner_choice = determine_winner(choices)
    if winner_choice is None:
        announce(f"Tie! Everyone stays in. ({choices})")
        return True

    survivors = [p for p, c in choices.items() if c == winner_choice]
    eliminated = [p for p in active_players if p not in survivors]
    color_map = {"rock": (255, 0, 0), "paper": (0, 255, 0), "scissors": (0, 0, 255)}
    win_color = color_map.get(winner_choice, (255, 255, 0))

    announce(f"Winning move: {winner_choice.upper()}", color=win_color)
    announce(f"Survivors: {', '.join(survivors)}", color=(0, 255, 0))
    if eliminated:
        announce(f"Eliminated: {', '.join(eliminated)}", color=(255, 0, 0))

    active_players.clear()
    active_players.update(survivors)

    if len(active_players) == 1:
        announce(f"Game Over! Champion: {list(active_players)[0]}", color=(0, 255, 0))
        reset_game_prompt()
        return False
    elif len(active_players) == 0:
        announce("Everyone eliminated! No winner.")
        reset_game_prompt()
        return False
    else:
        return True


def reset_game_prompt():
    global game_active, waiting_for_players
    announce("Game finished!")
    print("\nGame over!")
    while True:
        again = input("Play again? (y/n): ").strip().lower()
        if again == "y":
            announce("New game starting soon! Waiting for players...")
            waiting_for_players = True
            game_active = True
            active_players.clear()
            time.sleep(2)
            break
        elif again == "n":
            announce("Host ending session.")
            game_active = False
            waiting_for_players = False
            active_players.clear()
            break


def game_loop():
    global game_active
    while True:
        if not game_active:
            time.sleep(1)
            continue
        keep_playing = start_round()
        time.sleep(3)
        if not keep_playing:
            time.sleep(3)


client.on_message = on_message
client.connect(broker, port)
client.subscribe("IDD/rps/choices/#")
client.loop_start()

try:
    game_loop()
except KeyboardInterrupt:
    print("\nStopping host...")
finally:
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup()
    show_text("Host disconnected.", color=(255, 255, 255))
