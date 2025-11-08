import time
import cv2 as cv
from teachable_machine_lite import TeachableMachineLite

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import subprocess  # For TTS
from datetime import datetime

print("Starting human greeter...")

# Display setup (but don't turn on backlight yet)
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = False  # backlight OFF initially

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

def show_screen(title, subtitle="", bg=(0, 0, 0), fg=(255, 255, 255)):
    draw.rectangle((0, 0, width, height), fill=bg)
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except Exception:
        font_big = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=font_big)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - tw) // 2, 18), title, font=font_big, fill=fg)

    if subtitle:
        bbox_sub = draw.textbbox((0, 0), subtitle, font=font_sm)
        sw, sh = bbox_sub[2] - bbox_sub[0], bbox_sub[3] - bbox_sub[1]
        draw.text(((width - sw) // 2, 18 + th + 6), subtitle, font=font_sm, fill=fg)

    disp.image(image)

def get_time_based_message():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning! You've got this."
    elif hour < 18:
        return "Welcome back. Ready to focus?"
    else:
        return "Good evening. Let's get a bit done."


# Do NOT show anything yet
print("Display initialized (backlight off).")

# Load model
model_path = "model.tflite"
labels_path = "labels.txt"
tm_model = TeachableMachineLite(model_path=model_path, labels_file_path=labels_path)
print("Model loaded.")

# Start camera
print("Opening camera...")
cap = cv.VideoCapture(0)
image_file_name = "frame.jpg"

last_detect_time = 0
display_delay = 5  # seconds to show welcome screen
current_state = "blank"
display_ready = False  # track when we first show something

# Debounce Variable
debounce_start = None
debounce_duration = 0.3 #300ms debounce window

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        continue

    cv.imwrite(image_file_name, frame)
    print("Frame saved.")

    results = tm_model.classify_image(image_file_name)
    print(f"Results: {results}")

    top_label = results["label"]
    confidence = results["confidence"] / 100  # convert to 0–1
    now = time.time()

    if not display_ready:
        print("Turning on backlight and showing first screen.")
        backlight.value = True
        show_screen("Waiting...", "Scanning for human")
        current_state = "waiting"
        display_ready = True

    if results["highest_class_id"] == 0 and confidence > 0.8:
	 # Start or continue debounce
	if debounce_start is None:
		debounce_start = now
	elif (now - debounce_start) >= debounce_duration:
		 print("Human detected!")
        	if current_state != "detected":
            		motivational_message = get_time_based_message()
           		 show_screen("Welcome!", "Human detected", bg=(0, 80, 0))
           		 subprocess.run(["flite", "-voice", "slt", "-t", motivational_message])
           		 current_state = "detected"
       		last_detect_time = now

    else:
       # Reset debounce when no human is seen
	debounce_start = None
	print("No human detected.")
        
	if current_state == "detected" and (now - last_detect_time) > display_delay:
            print("Timeout: switching to scanning mode.")
            show_screen("Waiting...", "Scanning for human")
            current_state = "waiting"
        elif current_state != "detected" and (now - last_detect_time) > display_delay:
            show_screen("Waiting...", "Scanning for human")
            current_state = "waiting"

    k = cv.waitKey(1)
    if k % 255 == 27:  # ESC to quit
        print("Exiting.")
        break

cap.release()
cv.destroyAllWindows()

