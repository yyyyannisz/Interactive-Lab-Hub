import time
import subprocess
import digitalio
import board
import math
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.D5) 
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
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
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Setup button A (to switch screens)
buttonA = digitalio.DigitalInOut(board.D23)
buttonA.switch_to_input(pull=digitalio.Pull.UP)

screen_mode = 0  # 0: Cycle Clock, 1: Summary, 2: Input

while True:
    if not buttonA.value:  # If button pressed
        screen_mode = (screen_mode + 1) % 3
        time.sleep(0.3)  # debounce delay

    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    if screen_mode == 0:
        # ----------- Screen 1: Menstrual Cycle Clock View ------------
        # Draw a circle and annotate phases
        center = (width // 2, height // 2)
        radius = 50
        draw.ellipse([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius], outline="white", width=2)

        draw.text((center[0]-10, center[1]-radius-20), "Menstrual", font=font, fill="red")
        draw.text((center[0]+radius+5, center[1]-10), "Follicular", font=font, fill="orange")
        draw.text((center[0]-10, center[1]+radius+5), "Ovulatory", font=font, fill="blue")
        draw.text((center[0]-radius-60, center[1]-10), "Luteal", font=font, fill="purple")

        # Add arrow hand (e.g., day 7 = 63 degrees)
        day_of_cycle = 7
        angle = (day_of_cycle / 28) * 360  # Assuming 28-day cycle
        arrow_x = center[0] + radius * 0.8 * math.cos(math.radians(angle))
        arrow_y = center[1] - radius * 0.8 * math.sin(math.radians(angle))
        draw.line([center, (arrow_x, arrow_y)], fill="white", width=3)

        draw.text((10, 10), f"{day_of_cycle}/28 day of cycle", font=font, fill="white")

    elif screen_mode == 1:
        # ----------- Screen 2: Summary Info View ------------
        draw.text((10, 10), "Sat, Sep 27", font=font, fill="white")
        draw.text((10, 40), "7th day of cycle", font=font, fill="white")
        draw.text((10, 70), "⚡ Rising Energy", font=font, fill="white")
        draw.text((10, 100), "❤️ Light Bleeding", font=font, fill="white")
        draw.text((10, 130), "👍 Starting projects", font=font, fill="white")

    elif screen_mode == 2:
        # ----------- Screen 3: Last Period Input View ------------
        draw.text((10, 10), "Last Period", font=font, fill="white")
        draw.text((10, 50), "MM: 09", font=font, fill="white")
        draw.text((10, 80), "DD: 21", font=font, fill="white")
        draw.text((10, 120), "[Done]", font=font, fill="green")

    # Display image
    disp.image(image, rotation)
    time.sleep(0.1)
