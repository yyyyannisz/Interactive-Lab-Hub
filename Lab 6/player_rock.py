import paho.mqtt.client as mqtt
import time
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# --- Display setup (based on Human Greeter lab) ---
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True  # Turn on backlight

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

# Determine width/height after rotation
if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

# TFT drawing
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

def show_text(text, color=(255, 255, 0)):
    """Display centered text on the PiTFT."""
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    max_size, min_size = 24, 16
    size = max_size

    while True:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=4)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if (tw <= width - 10 and th <= height - 10) or size <= min_size:
            break
        size -= 2

    x = (width - tw) // 2
    y = (height - th) // 2
    draw.multiline_text((x, y), text, font=font, fill=color, spacing=4, align="center")
    disp.image(image)

# ----------------------------
# Buttons (same config as your earlier Lab)
# ----------------------------
buttonA = digitalio.DigitalInOut(board.D23)  # short press = cycle moves
buttonA.switch_to_input(pull=digitalio.Pull.UP)

buttonB = digitalio.DigitalInOut(board.D24)  # long press = submit move
buttonB.switch_to_input(pull=digitalio.Pull.UP)

B_LONG_MS = 600
b_press_start = None

# --- Step 1: Welcome screen ---
show_text("Let's play\nRock, Paper,\nScissors!", color=(0, 180, 255))
time.sleep(4)

# --- Step 2: Input name (keyboard still needed here) ---
show_text("Enter player\nname via\nkeyboard", color=(255, 255, 0))
player_name = input("Enter your player name: ").strip()

# --- MQTT setup ---
broker = "farlab.infosci.cornell.edu"
port = 1883
username = "idd"
password = "device@theFarm"

topic_choice = f"IDD/rps/choices/{player_name}"
topic_status = "IDD/rps/status"

client = mqtt.Client()
client.username_pw_set(username, password)

# --- Show status messages from Host ---
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print("\nHOST:", message)

    lower = message.lower()
    if "champion" in lower:
        color = (0, 255, 0)
    elif "eliminated" in lower:
        color = (255, 0, 0)
    elif "round" in lower:
        color = (0, 180, 255)
    else:
        color = (255, 255, 0)

    show_text(message, color=color)

client.on_message = on_message
client.connect(broker, port)
client.subscribe(topic_status)
client.loop_start()

# Announce join
client.publish(topic_choice, "join")
show_text(f"Joined as\n{player_name}", color=(0, 180, 255))
print("Joined MQTT game. Waiting for Host...")

# --- Move selection state ---
moves = ["rock", "paper", "scissors"]
move_index = 0
current_move = moves[move_index]
show_text(f"Selected:\n{current_move.upper()}")

# ------------------------------------------------------
# Main loop: use button A (cycle) & button B (submit)
# ------------------------------------------------------
try:
    while True:

        # ----- Button A: short press = cycle moves -----
        if not buttonA.value:  # button is pressed
            move_index = (move_index + 1) % len(moves)
            current_move = moves[move_index]
            print("Cycle:", current_move)
            show_text(f"Selected:\n{current_move.upper()}")
            time.sleep(0.25)  # debounce

        # ----- Button B: short/long press detection -----
        if not buttonB.value:
            if b_press_start is None:
                b_press_start = time.monotonic()
        else:
            if b_press_start is not None:
                press_ms = (time.monotonic() - b_press_start) * 1000
                long_press = press_ms >= B_LONG_MS

                if long_press:
                    # SEND MOVE
                    client.publish(topic_choice, current_move)
                    print("Submitted:", current_move)
                    show_text(f"Submitted:\n{current_move.upper()}", color=(255, 255, 0))
                    time.sleep(1)

                b_press_start = None

        time.sleep(0.05)

finally:
    client.loop_stop()
    client.disconnect()
    show_text("Disconnected.", color=(255, 255, 255))

