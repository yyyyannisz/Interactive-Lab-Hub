import paho.mqtt.client as mqtt
import time
import board
import digitalio
import busio
import adafruit_mpr121
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# --- Display setup (based on Human Greeter wiring) ---
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
    size = 20
    font = ImageFont.truetype(font_path, size)
    bbox = draw.multiline_textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x, y = (width - tw)//2, (height - th)//2
    draw.multiline_text((x, y), text, font=font, fill=color, align="center")
    disp.image(image)

# --- Startup ---
show_text("Let's play\nPaper, Scissor,\nand Rock!", (0,180,255))
time.sleep(3)

show_text("Please enter\nyour name\nusing keyboard", (255,255,0))
player_name = input("Enter your player name: ").strip()

# --- MQTT ---
broker = "farlab.infosci.cornell.edu"
client = mqtt.Client()
client.username_pw_set("idd", "device@theFarm")
client.connect(broker, 1883)

topic_choice = f"IDD/rps/choices/{player_name}"
topic_status = "IDD/rps/status"

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    lower = message.lower()
    print(f"\n{message}")

    # ---- Hide "waiting for enough players" ----
    if "waiting for enough players" in lower or "not enough players" in lower:
        return

    # ---- Show proper "round start" message ----
    if "new round" in lower or "send your move" in lower:
        show_text("Time to play!\nSend your choice:\nROCK, PAPER, SCISSORS!")
        return

    # ---- Detect GAME OVER ----
    if "champion" in lower or "game over" in lower:
        show_text("GAME OVER!", color=(255,0,0))
        return

    # Default: show host message
    show_text(message)

client.on_message = on_message
client.subscribe(topic_status)
client.loop_start()

# --- MPR121 Touch Sensor ---
i2c = busio.I2C(board.SCL, board.SDA)
mpr121 = adafruit_mpr121.MPR121(i2c)

TOUCH_MAP = {
    0: "rock",
    1: "paper",
    2: "scissors",
}

# Debounce
last_pad = None
last_time = 0
DEBOUNCE_TIME = 0.6

# Announce join
client.publish(topic_choice, "join")
show_text(f"Joined as\n{player_name}", (0,180,255))
print(f"Joined as {player_name}")
time.sleep(2)
show_text("Waiting for host...", (255,255,0))

# --- Main Loop (non-blocking) ---
while True:
    touched_pad = None
    
    for pad in TOUCH_MAP.keys():
        if mpr121[pad].value:
            touched_pad = pad
            break

    if touched_pad is not None:
        now = time.time()
        if (touched_pad != last_pad) or (now - last_time > DEBOUNCE_TIME):
            last_pad = touched_pad
            last_time = now

            choice = TOUCH_MAP[touched_pad]
            print(f"Touched: {choice}")
            show_text(f"You chose\n{choice.upper()}")
            client.publish(topic_choice, choice)

        time.sleep(0.05)
        continue

    if touched_pad is None:
        last_pad = None

    time.sleep(0.05)

