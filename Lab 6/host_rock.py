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

# Handle rotation
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

# Pad → move mapping
TOUCH_MAP = {
    0: "rock",
    1: "paper",
    2: "scissors"
}

current_move = "rock"
host_submitted = False
last_touch_time = 0
TOUCH_DEBOUNCE = 0.4
LONG_PRESS_SEC = 1.2

host_choice_topic = "IDD/rps/choices/host"


def update_selection_screen():
    show_text(f"Host selecting:\n{current_move.upper()}", color=(0, 180, 255))


update_selection_screen()


def scan_host_touch():
    """Host short touch = pick move, long touch = submit."""
    global current_move, host_submitted, last_touch_time

    for pad, move in TOUCH_MAP.items():
        if mpr121[pad].value:
            now = time.time()
            if now - last_touch_time < TOUCH_DEBOUNCE:
                return
            last_touch_time = now

            press_start = time.time()

            # long press detection
            while mpr121[pad].value:
                if time.time() - press_start > LONG_PRESS_SEC:
                    host_submitted = True
                    client.publish(host_choice_topic, current_move)
                    show_text(
                        f"Host submitted:\n{current_move.upper()}",
                        color=(255, 255, 0)
                    )
                    return
                time.sleep(0.01)

            # short press → select move
            current_move = move
            update_selection_screen()
            return


# ---------------- INITIAL UI ----------------
show_text("Welcome\nRock-Paper-Scissors\nHost", color=(0, 180, 255))
time.sleep(5)
show_text("Waiting for players...", color=(255, 255, 0))


# ---------------- MQTT CONFIG ----------------
broker = "farlab.infosci.cornell.edu"
port = 1883
username = "idd"
password = "device@theFarm"

ROUND_DURATION = 10

choices = {}
active_players = set()
round_active = False
game_active = False

client = mqtt.Client()
client.username_pw_set(username, password)


def determine_winner(players_choices):
    unique = set(players_choices.values())
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
    global active_players, round_active

    player = msg.topic.split("/")[-1]
    choice = msg.payload.decode().strip().lower()

    # join
    if choice == "join":
        active_players.add(player)
        announce(f"{player} joined! ({len(active_players)} players)")
        return

    # quit
    if choice == "quit":
        if player in active_players:
            active_players.remove(player)
            announce(f"{player} left the game.")
        return

    # not a valid move
    if choice not in ["rock", "paper", "scissors"]:
        return

    # not in active round
    if not round_active:
        active_players.add(player)
        return

    # valid move
    choices[player] = choice
    active_players.add(player)


client.on_message = on_message
client.connect(broker, port)
client.subscribe("IDD/rps/choices/#")
client.loop_start()


def start_round():
    global round_active, host_submitted, choices

    host_submitted = False

    announce(f"New round! {ROUND_DURATION}s to play!", color=(0, 180, 255))
    announce("Send your move!")

    round_active = True
    choices.clear()

    countdown = ROUND_DURATION
    while countdown > 0:
        scan_host_touch()
        print(f"{countdown}s...", end="\r")
        time.sleep(1)
        countdown -= 1

    round_active = False

    if not host_submitted:
        announce("Host did NOT submit!", color=(255, 0, 0))
        return True

    if not choices:
        announce("No players submitted this round.")
        return True

    winner_choice = determine_winner(choices)

    if winner_choice is None:
        announce("Tie! No one eliminated.")
        return True

    survivors = [p for p, c in choices.items() if c == winner_choice]
    eliminated = [p for p in active_players if p not in survivors]

    colors = {"rock": (255, 0, 0), "paper": (0, 255, 0), "scissors": (0, 0, 255)}

    announce(f"Winning move: {winner_choice.upper()}", color=colors[winner_choice])
    announce(f"Survivors: {', '.join(survivors)}", color=(0, 255, 0))

    if eliminated:
        announce(f"Eliminated: {', '.join(eliminated)}", color=(255, 0, 0))

    active_players.clear()
    active_players.update(survivors)

    # if one remains
    if len(active_players) == 1:
        champ = list(active_players)[0]
        announce(f"Champion: {champ}", color=(0, 255, 0))
        return False

    return True


def game_loop():
    global game_active
    game_active = True

    while True:
        keep_going = start_round()
        time.sleep(3)
        if not keep_going:
            announce("Game finished!")
            break


try:
    game_loop()

except KeyboardInterrupt:
    print("\nStopping host...")

finally:
    client.loop_stop()
    client.disconnect()
    show_text("Host disconnected.", color=(255, 255, 255))

