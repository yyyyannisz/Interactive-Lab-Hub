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

try:
    font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except:
    font_big = ImageFont.load_default()
    font_sm = ImageFont.load_default()

def show_text(title, subtitle="", color=(255, 255, 0)):
    """Clear and display a title + optional subtitle."""
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
    # Center title
    bbox = draw.textbbox((0, 0), title, font=font_big)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - tw) // 2, 40), title, font=font_big, fill=color)
    if subtitle:
        bbox2 = draw.textbbox((0, 0), subtitle, font=font_sm)
        sw, sh = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
        draw.text(((width - sw) // 2, 40 + th + 10), subtitle, font=font_sm, fill=color)
    disp.image(image)

# --- Initial welcome screen ---
show_text("Welcome to", "the Paper, Scissor, and Rock Game!", color=(0, 180, 255))
time.sleep(1.5)
show_text("Please enter", "your name using keyboard", color=(255, 255, 0))

# --- MQTT Configuration ---
broker = "farlab.infosci.cornell.edu"
port = 1883
username = "idd"
password = "device@theFarm"

# --- Ask for player name ---
player_name = input("Enter your player name: ").strip()

topic_choice = f"IDD/rps/choices/{player_name}"
topic_status = "IDD/rps/status"

client = mqtt.Client()
client.username_pw_set(username, password)

def on_message(client, userdata, msg):
    """Display messages from host on both terminal and TFT."""
    message = msg.payload.decode()
    print(f"\n{message}")

    # Choose colors based on message context
    lower = message.lower()
    if "winner" in lower or "champion" in lower:
        color = (0, 255, 0)
    elif "eliminated" in lower:
        color = (255, 0, 0)
    elif "waiting" in lower:
        color = (255, 255, 255)
    elif "round" in lower or "ready" in lower:
        color = (0, 180, 255)
    else:
        color = (255, 255, 0)
    show_text(message, color=color)

client.on_message = on_message
client.connect(broker, port)
client.subscribe(topic_status)
client.loop_start()

# --- Announce join ---
client.publish(topic_choice, "join")
print(f"You have joined the game as {player_name}!")
show_text("Joined as", player_name, color=(0, 180, 255))
print("Waiting for round announcements...")

try:
    while True:
        msg = input("").strip().lower()
        if msg == "quit":
            client.publish(topic_choice, "quit")
            print("You left the game.")
            show_text("You left", "the game.", color=(255, 0, 0))
            break
        if msg not in ["rock", "paper", "scissors"]:
            print("Invalid choice.")
            show_text("Invalid choice!", "Try again.", color=(255, 255, 255))
            continue

        client.publish(topic_choice, msg)
        print(f"Sent your choice: {msg.upper()}")
        show_text("You chose", msg.upper(), color=(255, 255, 0))
        time.sleep(1)

finally:
    client.loop_stop()
    client.disconnect()
    show_text("Disconnected.", "", color=(255, 255, 255))
