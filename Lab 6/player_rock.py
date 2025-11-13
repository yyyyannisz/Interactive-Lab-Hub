import paho.mqtt.client as mqtt
import time
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# --- Display setup ---
cs_pin = digitalio.DigitalInOut(board.CE1)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
BAUDRATE = 64000000

spi = board.SPI()
disp = st7789.ST7789(
    spi,
    height=135,
    y_offset=40,
    rotation=90,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

width = disp.width
height = disp.height
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

def show_text(text, color=(255, 255, 0)):
    """Helper to clear and display text on the PiTFT screen."""
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    # Simple line wrapping for longer messages
    lines = []
    words = text.split()
    line = ""
    for word in words:
        if len(line + " " + word) < 20:
            line += " " + word
        else:
            lines.append(line.strip())
            line = word
    lines.append(line.strip())
    y = 40
    for l in lines:
        draw.text((10, y), l, font=font, fill=color)
        y += 15
    disp.image(image)

# --- MQTT Configuration ---
broker = "farlab.infosci.cornell.edu"
port = 1883
username = "idd"
password = "device@theFarm"

player_name = input("Enter your player name: ").strip()
topic_choice = f"IDD/rps/choices/{player_name}"
topic_status = "IDD/rps/status"

client = mqtt.Client()
client.username_pw_set(username, password)

def on_message(client, userdata, msg):
    """Display messages from host on both terminal and TFT."""
    message = msg.payload.decode()
    print(f"\n{message}")
    # Choose colors based on keywords
    lower = message.lower()
    if "winner" in lower:
        color = (0, 255, 0)
    elif "eliminated" in lower:
        color = (255, 0, 0)
    elif "waiting" in lower:
        color = (255, 255, 255)
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
show_text(f"Joined as {player_name}")
print("Waiting for round announcements...")

try:
    while True:
        msg = input("").strip().lower()
        if msg == "quit":
            client.publish(topic_choice, "quit")
            print("You left the game.")
            show_text("You left the game.", color=(255, 0, 0))
            break
        if msg not in ["rock", "paper", "scissors"]:
            print("Invalid choice.")
            show_text("Invalid choice!", color=(255, 255, 255))
            continue

        client.publish(topic_choice, msg)
        print(f"Sent your choice: {msg.upper()}")
        show_text(f"You chose {msg.upper()}")
        time.sleep(1)

finally:
    client.loop_stop()
    client.disconnect()
    show_text("Disconnected.", color=(255, 255, 255))
