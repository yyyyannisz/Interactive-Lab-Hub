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
font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)

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
# Helpers (same angle system as Pillow pieslice)
# 0° at 3 o'clock, CCW positive, +y is down.
# ----------------------------------
def pol2xy(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))

def draw_centered_text(draw_obj, text, center_xy, font, fill):
    l, t, r, b = draw_obj.textbbox((0, 0), text, font=font)
    w, h = (r - l, b - t)
    draw_obj.text((center_xy[0] - w / 2, center_xy[1] - h / 2), text, font=font, fill=fill)

def phase_for_day(day):
    """Return (name, color) for a 1-based day-of-cycle."""
    d = day
    for name, days, color in phases:
        if d <= days:
            return name, color
        d -= days
    # fallback
    return phases[-1][0], phases[-1][2]

# Layout constants
TITLE_Y = 4
LEGEND_H = 40                   # reserved space at bottom for legend
CHART_AREA_H = height - LEGEND_H
CENTER = (width // 2, CHART_AREA_H // 2 + 6)  # push slightly down
RADIUS = 44                     # leave room for title
POINTER_COLOR = "black"
START_OFFSET = -90              # 12 o'clock

def draw_legend(draw_obj, x0, y0, row_gap=4, col_gap=12):
    """2-column legend with colored squares and labels."""
    swatch = 9
    col_w = (width - 2 * x0) // 2
    # two rows × two columns
    items = [
        phases[0], phases[1],
        phases[2], phases[3],
    ]
    for idx, (name, _, color) in enumerate(items):
        row = idx // 2
        col = idx % 2
        cx = x0 + col * col_w
        cy = y0 + row * (swatch + row_gap + 10)
        # color square
        draw_obj.rectangle([cx, cy, cx + swatch, cy + swatch], fill=color, outline="white")
        # text
        draw_obj.text((cx + swatch + 5, cy - 2), name, font=font_small, fill="white")

def rounded_rect(draw_obj, bbox, radius, fill, outline=None, width=1):
    # Pillow has rounded_rectangle; keep this wrapper for clarity
    draw_obj.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)

def text_size(draw_obj, text, font):
    """Return width and height of given text."""
    l, t, r, b = draw_obj.textbbox((0, 0), text, font=font)
    return (r - l, b - t)

def draw_badge(draw_obj, text, x, y, pad_x=6, pad_y=2, bg="#2A2A2A", fg="white"):
    w, h = text_size(draw_obj, text, font_small)
    rounded_rect(draw_obj, (x, y, x + w + 2*pad_x, y + h + 2*pad_y), radius=6, fill=bg)
    draw_obj.text((x + pad_x, y + pad_y), text, font=font_small, fill=fg)
    return (x + w + 2*pad_x, y + h + 2*pad_y)

def bullet_row(draw_obj, x, y, text, color, line_w=10, gap=8):
    # colored line “bullet” + label
    draw_obj.rounded_rectangle((x, y+6, x+line_w, y+8), radius=2, fill=color)
    draw_obj.text((x + line_w + gap, y), text, font=font_medium, fill="white")
    
while True:
    if not buttonA.value:  # pressed
        screen_mode = (screen_mode + 1) % 3
        time.sleep(0.3)  # debounce

    # clear screen
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

    if screen_mode == 0:
        # -------- Screen 1: Cycle Clock (labels moved to legend) --------
        day_of_cycle = 7  # TODO: replace with real value
        # title
        draw.text((6, TITLE_Y), f"{day_of_cycle}th day", font=font_medium, fill="white")

        # pie
        start_angle = START_OFFSET
        for name, days, color in phases:
            sweep = (days / total_days) * 360.0
            end_angle = start_angle + sweep
            draw.pieslice(
                [CENTER[0] - RADIUS, CENTER[1] - RADIUS, CENTER[0] + RADIUS, CENTER[1] + RADIUS],
                start=start_angle, end=end_angle, fill=color, outline="white",
            )
            start_angle = end_angle

        # pointer
        angle = START_OFFSET + (day_of_cycle / total_days) * 360.0
        ax, ay = pol2xy(CENTER[0], CENTER[1], RADIUS * 0.82, angle)
        draw.line([CENTER, (ax, ay)], fill=POINTER_COLOR, width=3)
    
        # legend at bottom
        legend_y = height - LEGEND_H + 8
        draw_legend(draw, x0=12, y0=legend_y)

    elif screen_mode == 1:
        # -------- Page 2: Summary (redesigned) --------
        # Card background
        card_margin = 6
        card_bbox = (card_margin, card_margin, width - card_margin, height - card_margin)
        rounded_rect(draw, card_bbox, radius=12, fill="#1B1E22")  # dark blue-gray
        inner_pad = 10

        # Header row: Date + phase badge
        header_x = card_bbox[0] + inner_pad
        header_y = card_bbox[1] + inner_pad

        date_text = "Sat, Sep 27"
        draw.text((header_x, header_y), date_text, font=font_large, fill="white")

        # Phase badge on the right
        day_of_cycle = 7  # TODO: your real value
        phase_name, phase_color = phase_for_day(day_of_cycle)
        badge_text = f"{day_of_cycle}ᵗʰ  •  {phase_name}"
        bw, bh = text_size(draw, badge_text, font_small)
        badge_right = card_bbox[2] - inner_pad
        badge_x = badge_right - (bw + 12)
        badge_y = header_y + 2
        draw_badge(draw, badge_text, badge_x, badge_y, pad_x=6, pad_y=2, bg="#2C3137", fg="white")

        # Divider
        divider_y = header_y + 24
        draw.line((card_bbox[0] + inner_pad, divider_y, card_bbox[2] - inner_pad, divider_y), fill="#3C424A", width=1)

        # Subtitle
        sub_y = divider_y + 6
        draw.text((header_x, sub_y), "Today’s snapshot", font=font_medium, fill="#BFC7D1")

        # Bullet rows
        row_y = sub_y + 18
        line_x = header_x
        bullet_row(draw, line_x, row_y, "Rising Energy", color="#A8E3DC")   # teal
        row_y += 20
        bullet_row(draw, line_x, row_y, "Light Bleeding", color="#F28BA0")  # light red
        row_y += 20
        bullet_row(draw, line_x, row_y, "Good for starting tasks", color="#FFE88A")  # yellow hint


    elif screen_mode == 2:
        # ----------- Screen 3: Last Period Input View ------------
        draw.text((10, 10), "Last Period", font=font_small, fill="white")
        draw.text((10, 50), "MM: 09", font=font_small, fill="white")
        draw.text((10, 80), "DD: 21", font=font_small, fill="white")
        draw.text((10, 120), "[Done]", font=font_small, fill="green")

    # Display image
    disp.image(image, rotation)
    time.sleep(0.1)
