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
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
except:
    font = ImageFont.load_default()

def show_text(text, color=(255, 255, 0)):
    """Helper to clear and display text on the PiTFT screen."""
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
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
        y += 20
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

    # Choose colors based on message context
    lower = message.lower()
    if "winner" in lower or "champion" in lower:
        color = (0, 255, 0)        # green
    elif "eliminated" in lower:
        color = (255, 0, 0)        # red
    elif "waiting" in lower:
        color = (255, 255, 255)    # white
    elif "round" in lower or "ready" in lower:
        color = (0, 180, 255)      # blue
    else:
        color = (255, 255, 0)      # yellow
    show_text(message, color=color)

client.on_message = on_message
client.connect(broker, port)
client.subscribe(topic_status)
client.loop_start()

# --- Announce join ---
client.publish(topic_choice, "join")
print(f"You have joined the game as {player_name}!")
show_text(f"Joined as {player_name}", color=(0, 180, 255))
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
        show_text(f"You chose {msg.upper()}", color=(255, 255, 0))
        time.sleep(1)

finally:
    client.loop_stop()
    client.disconnect()
    show_text("Disconnected.", color=(255, 255, 255))
