import paho.mqtt.client as mqtt
import time
import board
import digitalio
import busio
import adafruit_mpr121
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# --- Display setup (based on Human Greeter lab wiring) ---
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True  # Turn on backlight immediately

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

# Handle rotation properly
if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

def show_text(text, color=(255, 255, 0)):
    """Display text adjusted to fit the PiTFT screen neatly."""
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    max_font_size = 24
    min_font_size = 16
    font_size = max_font_size

    while True:
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=4)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        if (tw <= width - 10 and th <= height - 10) or font_size <= min_font_size:
            break
        font_size -= 2

    x = (width - tw) // 2
    y = (height - th) // 2
    draw.multiline_text((x, y), text, font=font, fill=color, align="center", spacing=4)
    disp.image(image)

# --- Startup screens ---
show_text("Let's play\nPaper, Scissor,\nand Rock!", color=(0, 180, 255))
time.sleep(4)

show_text("Please enter\nyour name\nusing keyboard", color=(255, 255, 0))

# --- MQTT Setup ---
broker = "farlab.infosci.cornell.edu"
port = 1883
username = "idd"
password = "device@theFarm"

# --- Name input ---
player_name = input("Enter your player name: ").strip()
topic_choice = f"IDD/rps/choices/{player_name}"
topic_status = "IDD/rps/status"

client = mqtt.Client()
client.username_pw_set(username, password)

# --- Message handler ---
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"\n{message}")

    lower = message.lower()
    if "winner" in lower or "champion" in lower:
        color = (0, 255, 0)
    elif "eliminated" in lower:
        color = (255, 0, 0)
    elif "round" in lower or "ready" in lower:
        color = (0, 180, 255)
    else:
        color = (255, 255, 0)

    show_text(message, color=color)

client.on_message = on_message
client.connect(broker, port)
client.subscribe(topic_status)
client.loop_start()

# --- MPR121 Touch Sensor Setup ---
i2c = busio.I2C(board.SCL, board.SDA)
mpr121 = adafruit_mpr121.MPR121(i2c)

# Touch to move mapping
TOUCH_MAP = {
    0: "rock",
    1: "paper",
    2: "scissors",
}

# --- Announce player joined ---
client.publish(topic_choice, "join")
show_text(f"Joined as\n{player_name}", color=(0, 180, 255))
print(f"You have joined the game as {player_name}!")
time.sleep(2)

show_text("Waiting for host...", color=(255, 255, 0))

# --- Main game loop ---
try:
    while True:
        # --- 1) Check touch sensor ---
        touched_choice = None
        for pad, choice in TOUCH_MAP.items():
            if mpr121[pad].value:
                touched_choice = choice
                break

        if touched_choice:
            msg = touched_choice
            print(f"Touched: {msg.upper()}")
            show_text(f"You chose\n{msg.upper()}", color=(255, 255, 0))
            client.publish(topic_choice, msg)
            time.sleep(1)
            continue  # skip keyboard

        # --- 2) Keyboard fallback ---
        msg = input("").strip().lower()

        if msg == "quit":
            client.publish(topic_choice, "quit")
            print("You left the game.")
            show_text("You left\nthe game.", color=(255, 0, 0))
            break

        if msg not in ["rock", "paper", "scissors"]:
            print("Invalid choice.")
            show_text("Invalid choice!\nTry again.", color=(255, 255, 255))
            continue

        client.publish(topic_choice, msg)
        print(f"Sent your choice: {msg.upper()}")
        show_text(f"You chose\n{msg.upper()}", color=(255, 255, 0))
        time.sleep(1)

finally:
    client.loop_stop()
    client.disconnect()
    show_text("Disconnected.", color=(255, 255, 255))
