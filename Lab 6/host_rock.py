import paho.mqtt.client as mqtt
import time
import board
import digitalio
import busio
import adafruit_mpr121
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

# Display size
if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

def show_text(text, color=(255, 255, 0)):
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    max_font = 24
    min_font = 16
    size = max_font

    while True:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=4)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if (tw <= width - 10 and th <= height - 10) or size <= min_font:
            break
        size -= 2

    x = (width - tw) // 2
    y = (height - th) // 2
    draw.multiline_text((x, y), text, fill=color, font=font, align="center", spacing=4)
    disp.image(image)

# ---------------- MPR121 TOUCH SENSOR ----------------
i2c = busio.I2C(board.SCL, board.SDA)
mpr121 = adafruit_mpr121.MPR121(i2c)

# Mapping host choices to touch pads
TOUCH_MAP = {
    0: "rock",
    1: "paper",
    2: "scissors"
}

# Selection state
current_move = "rock"   # default
host_submitted = False
host_choice_topic = "IDD/rps/choices/host"

def update_selection_screen():
    show_text(f"Host selecting:\n{current_move.upper()}", color=(0, 180, 255))

update_selection_screen()

# ---------------- HOST TOUCH HANDLER ----------------
last_touch_time = 0
TOUCH_DEBOUNCE = 0.4  # seconds

def scan_host_touch():
    """
    Host selects ROCK/PAPER/SCISSORS via MPR121 touch pads.
    Short touch = choose move
    Long touch (≥1.2s) = submit choice
    """
    global current_move, host_submitted, last_touch_time

    for pad, move in TOUCH_MAP.items():
        if mpr121[pad].value:
            now = time.time()
            # debounce
            if now - last_touch_time < TOUCH_DEBOUNCE:
                return
            last_touch_time = now

            # measure press length
            press_start = time.time()
            while mpr121[pad].value:
                # long press → submit
                if time.time() - press_start > 1.2:
                   if not host_submitted:
                        host_submitted = True
                        choices["host"] = current_move  # <-- FIX
                        print(f"[HOST] SUBMIT {current_move}")
                        client.publish(host_choice_topic, current_move)
                        show_text(f"Host submitted:\n{current_move.upper()}", color=(255, 255, 0))
                        return
                time.sleep(0.01)

            # short tap → select move
            current_move = move
            
            print(f"[HOST] SELECT {current_move}")
            update_selection_screen()
            return


# ---------------- GAME INITIAL UI ----------------
show_text("Welcome\nRock-Paper-Scissors\nHost", color=(0, 180, 255))
time.sleep(5)
show_text("Waiting for\nplayers to join...", color=(255, 255, 0))

# ---------------- MQTT CONFIG ----------------
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

active_players = {"host"}
client = mqtt.Client()
client.username_pw_set(username, password)

def determine_winner(players_choices):
    unique = set(players_choices.values())
    print(f"Choices this round: {unique}")
    if len(unique) == 1 or len(unique) == 3:
        return None
    if unique == {"rock", "scissors"}: return "rock"
    if unique == {"scissors", "paper"}: return "scissors"
    if unique == {"paper", "rock"}: return "paper"

def announce(msg, color=(255, 255, 0)):
    print(msg)
    show_text(msg, color=color)
    client.publish("IDD/rps/status", msg)

def on_message(client, userdata, msg):
    global round_active, choices, active_players, game_active, waiting_for_players

    player = msg.topic.split("/")[-1]
    choice = msg.payload.decode().strip().lower()

    # --- Player joins ---
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

    # --- Player quits ---
    if choice == "quit":
        if player in active_players:
            active_players.remove(player)
            announce(f"{player} left the game. ({len(active_players)} players left)")

            if len(active_players) == 1:
                champ = list(active_players)[0]
                announce(f"Game Over! Champion: {champ}", color=(0, 255, 0))
                reset_game_prompt()

            elif len(active_players) < MIN_PLAYERS:
                waiting_for_players = True
                announce("Not enough players. Waiting...")
        return

    # --- Invalid payload ---
    if choice not in ["rock", "paper", "scissors"]:
        return

    # --- Round inactive: queue for next round ---
    if not round_active:
        active_players.add(player)
        return

    # --- Valid move during active round ---
    choices[player] = choice
    active_players.add(player)

def start_round():
    global round_active, choices, waiting_for_players, host_submitted, current_move

    host_submitted = False  # reset each round

    if waiting_for_players:
        announce("Waiting for enough players...")
        return True

    if len(active_players) < MIN_PLAYERS:
        waiting_for_players = True
        announce("Not enough players...")
        return True

    choices.clear()
    round_active = True

    announce(f"New round! {ROUND_DURATION}s to play!")
    announce("Send your move!")

    # ---- Countdown with fast touch scanning ----
    end_time = time.time() + ROUND_DURATION
    last_shown = None

    while time.time() < end_time:
        scan_host_touch()

        remaining = int(end_time - time.time())
        if remaining != last_shown and remaining >= 0:
            print(f"{remaining}s...", end="\r")
            last_shown = remaining

        time.sleep(0.05)  # fast scan for sensor

    round_active = False

    # Note: NO auto-submit – if host_submitted is False,
    # the host simply does not play this round.

    if not choices:
        announce("No moves this round. Waiting...")
        return True

    winner_choice = determine_winner(choices)

    if winner_choice is None:
        announce("Tie! Everyone stays in.")
        return True

    survivors = [p for p, c in choices.items() if c == winner_choice]
    eliminated = [p for p in active_players if p not in survivors]

    color_map = {"rock": (255, 0, 0), "paper": (0, 255, 0), "scissors": (0, 0, 255)}
    announce(f"Winning move: {winner_choice.upper()}", color=color_map[winner_choice])
    announce(f"Survivors: {', '.join(survivors)}", color=(0, 255, 0))

    if eliminated:
        announce(f"Eliminated: {', '.join(eliminated)}", color=(255, 0, 0))

    active_players.clear()
    active_players.update(survivors)

    if len(active_players) == 1:
        champ = list(active_players)[0]
        announce(f"Game Over! Champion: {champ}", color=(0, 255, 0))
        reset_game_prompt()
        return False

    if len(active_players) == 0:
        announce("Everyone eliminated! No winner.")
        reset_game_prompt()
        return False

    return True

def reset_game_prompt():
    global game_active, waiting_for_players

    announce("Game finished!")
    print("\nGame over!")

    while True:
        again = input("Play again? (y/n): ").strip().lower()
        if again == "y":
            announce("New game starting! Waiting for players...")
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
        keep_going = start_round()
        time.sleep(3)
        if not keep_going:
            time.sleep(3)

# ---------------- MQTT START ----------------
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
    show_text("Host disconnected.", color=(255, 255, 255))
