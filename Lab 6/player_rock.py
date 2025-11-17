import paho.mqtt.client as mqtt
import time
import board
import digitalio
import busio
from adafruit_apds9960.apds9960 import APDS9960
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
    fs = max_font_size

    while True:
        font = ImageFont.truetype(font_path, fs)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=4)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        if (tw <= width - 10 and th <= height - 10) or fs <= min_font_size:
            break
        fs -= 2

    x = (width - tw) // 2
    y = (height - th) // 2
    draw.multiline_text(
        (x, y), text, fill=color, font=font, spacing=4, align="center"
    )
    disp.image(image)

# ---------------- GESTURE SENSOR SETUP ----------------
i2c = busio.I2C(board.SCL, board.SDA)
apds = APDS9960(i2c)
apds.enable_gesture = True

# ---------------- MQTT SETUP ----------------
broker = "farlab.infosci.cornell.edu"
port = 1883
username = "idd"
password = "device@theFarm"

# Welcome screen
show_text("Let's play\nPaper, Scissor,\nand Rock!", color=(0, 180, 255))
time.sleep(3)

show_text("Enter your name\n(using keyboard)", color=(255,255,0))
player_name = input("Enter your player name: ").strip()

topic_choice = f"IDD/rps/choices/{player_name}"
topic_status = "IDD/rps/status"

client = mqtt.Client()
client.username_pw_set(username, password)

def on_message(client, userdata, msg):
    m = msg.payload.decode()
    print("\n" + m)

    lower = m.lower()
    if "winner" in lower or "champion" in lower:
        c = (0,255,0)
    elif "eliminated" in lower:
        c = (255,0,0)
    elif "waiting" in lower:
        c = (255,255,255)
    elif "round" in lower or "ready" in lower:
        c = (0,180,255)
    else:
        c = (255,255,0)

    show_text(m, color=c)

client.on_message = on_message
client.connect(broker, port)
client.subscribe(topic_status)
client.loop_start()

# Announce join
client.publish(topic_choice, "join")
show_text(f"Joined as\n{player_name}", color=(0,180,255))
print(f"You joined as {player_name}")
time.sleep(2)

# ---------------- GESTURE SELECTION LOOP ----------------
moves = {
    1: "rock",      # up
    3: "paper",     # left
    4: "scissors"   # right
}

current_choice = "rock"
show_text(f"Select:\n{current_choice.upper()}", color=(0,180,255))

try:
    while True:
        gesture = apds.gesture()

        if gesture is None or gesture == 0:
            time.sleep(0.05)
            continue

        # DOWN => submit
        if gesture == 2:
            client.publish(topic_choice, current_choice)
            print(f"Submitted: {current_choice}")
            show_text(f"Submitted:\n{current_choice.upper()}", color=(255,255,0))
            time.sleep(1)
            continue

        # UP / LEFT / RIGHT => select move
        if gesture in moves:
            current_choice = moves[gesture]
            print(f"Selected: {current_choice}")
            show_text(f"Select:\n{current_choice.upper()}", color=(0,180,255))
            time.sleep(0.4)

finally:
    client.loop_stop()
    client.disconnect()
    show_text("Disconnected.", color=(255,255,255))
