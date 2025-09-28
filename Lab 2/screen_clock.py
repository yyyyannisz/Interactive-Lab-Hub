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
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Setup button A (to switch screens)
buttonA = digitalio.DigitalInOut(board.D23)
buttonA.switch_to_input(pull=digitalio.Pull.UP)

screen_mode = 0  # 0: Cycle Clock, 1: Summary, 2: Input

# ----------------------------
# Phase Data
# ----------------------------
# Typical lengths – adjust later per user
menstrual_days = 5
follicular_days = 9
ovulation_days = 2
luteal_days = 12
total_days = menstrual_days + follicular_days + ovulation_days + luteal_days

phases = [
    ("Menstrual", menstrual_days, "#F28BA0"),  # red
    ("Follicular", follicular_days, "#A8E3DC"),# teal
    ("Ovulatory", ovulation_days, "#FFE88A"), # yellow
    ("Luteal", luteal_days, "#C7ACDF"),        # purple
]

# ----------------------------------
# Helpers (consistent angle system)
# Pillow pieslice: 0° at 3 o'clock, CCW positive, +y is down.
# ----------------------------------
def pol2xy(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))

def draw_centered_text(draw_obj, text, center_xy, font, fill):
    # center text on a point using textbbox
    l, t, r, b = draw_obj.textbbox((0, 0), text, font=font)
    w, h = (r - l, b - t)
    draw_obj.text((center_xy[0] - w / 2, center_xy[1] - h / 2), text, font=font, fill=fill)

while True:
    if not buttonA.value:  # pressed
        screen_mode = (screen_mode + 1) % 3
        time.sleep(0.3)  # debounce

    # clear screen
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

    if screen_mode == 0:
        # -------- Screen 1: Cycle Clock --------
        center = (width // 2, height // 2)
        radius = 45
        label_r = radius + 16
        start_offset = -90  # start at 12 o'clock
        arrow_color = "black"

        start_angle = start_offset
        for phase, days, color in phases:
            sweep = (days / total_days) * 360.0
            end_angle = start_angle + sweep

            # slice
            draw.pieslice(
                [center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
                start=start_angle,
                end=end_angle,
                fill=color,
                outline="white",
            )

            # centered label at mid-angle
            mid = (start_angle + end_angle) / 2.0
            lx, ly = pol2xy(center[0], center[1], label_r, mid)
            # Use white for readability on light slices
            draw_centered_text(draw, phase, (lx, ly), font=font, fill="white")

            start_angle = end_angle

        # arrow for current day (e.g., day 7)
        day_of_cycle = 7  # TODO: replace with computed value
        cumulative_days = 0
        # convert current day into angle offset
        angle = (day_of_cycle / total_days) * 360
        arrow_x = center[0] + radius * 0.8 * math.cos(math.radians(angle))
        arrow_y = center[1] - radius * 0.8 * math.sin(math.radians(angle))
        draw.line([center, (arrow_x, arrow_y)], fill=arrow_color, width=3)

        draw.text((5, 5), f"{day_of_cycle}/{total_days} day of cycle", font=font, fill="white")

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
