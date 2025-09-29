import time
import json
import os
import subprocess
import digitalio
import board
import math
from datetime import date,datetime
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

# Buttons
buttonA = digitalio.DigitalInOut(board.D23)
buttonA.switch_to_input(pull=digitalio.Pull.UP)
buttonB = digitalio.DigitalInOut(board.D24)  # value +/- (short/long)
buttonB.switch_to_input(pull=digitalio.Pull.UP)


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
# Helpers 
# ----------------------------------
def pol2xy(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))

def text_size(draw_obj, text, font):
    """Return width and height of given text."""
    l, t, r, b = draw_obj.textbbox((0, 0), text, font=font)
    return (r - l, b - t)

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

def compute_day_of_cycle(month, day, cycle_len=total_days):
    """Return 1..cycle_len based on days since last period start."""
    today = date.today()
    try:
        last = date(today.year, month, day)
        if last > today:
            # if the saved date is in the future this year, assume last year
            last = date(today.year - 1, month, day)
    except ValueError:
        return 1  # fallback if invalid date
    delta = (today - last).days
    if delta < 0:
        delta = 0
    return (delta % cycle_len) + 1

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

def draw_badge(draw_obj, text, x, y, pad_x=6, pad_y=2, bg="#2A2A2A", fg="white"):
    w, h = text_size(draw_obj, text, font_small)
    rounded_rect(draw_obj, (x, y, x + w + 2*pad_x, y + h + 2*pad_y), radius=6, fill=bg)
    draw_obj.text((x + pad_x, y + pad_y), text, font=font_small, fill=fg)
    return (x + w + 2*pad_x, y + h + 2*pad_y)

def bullet_row(draw_obj, x, y, text, color, line_w=10, gap=8):
    # colored line “bullet” + label
    draw_obj.rounded_rectangle((x, y+6, x+line_w, y+8), radius=2, fill=color)
    draw_obj.text((x + line_w + gap, y), text, font=font_medium, fill="white")

def days_in_month(mm, yyyy=None):
    # simple month lengths (no leap year for Feb since we don't store year)
    month_lengths = [31,28,31,30,31,30,31,31,30,31,30,31]
    if 1 <= mm <= 12:
        return month_lengths[mm-1]
    return 30

def phase_position_for_day(day, phases_list):
    """
    Given a 1-based day and the current phases list [(name, days, color), ...],
    return (phase_name, phase_color, phase_index, day_in_phase, days_in_phase).
    """
    d = day
    for idx, (name, days, color) in enumerate(phases_list):
        if d <= days:
            return name, color, idx, d, days
        d -= days
    # fallback to last phase
    name, days, color = phases_list[-1]
    return name, color, len(phases_list)-1, days, days

def get_snapshot_structured(day, phases_list):
    """
    Always return 3 rows: Feel, Symptom, 
    Colors are fixed (teal, red, yellow).
    """
    name, color, idx, d_in, d_len = phase_position_for_day(day, phases_list)

    # fixed colors
    C_FEEL = "#3CAEA3"   # teal
    C_SYMP = "#D72638"   # red
    C_TRY  = "#FFD23F"   # yellow

    if name == "Menstrual":
        if d_in <= 2:
            feel    = ("Low energy", C_FEEL)
            symptom = ("Heavier bleeding", C_SYMP)
            to_try  = ("Rest & keep warm", C_TRY)
        else:
            feel    = ("Energy slowly rising", C_FEEL)
            symptom = ("Light bleeding", C_SYMP)
            to_try  = ("Gentle walks", C_TRY)

    elif name == "Follicular":
        early = d_in <= max(1, d_len//2)
        if early:
            feel    = ("Rising energy", C_FEEL)
            symptom = ("Few symptoms", C_SYMP)
            to_try  = ("Plan & brainstorm", C_TRY)
        else:
            feel    = ("Focused & clear", C_FEEL)
            symptom = ("Stable mood", C_SYMP)
            to_try  = ("Start a project", C_TRY)

    elif name == "Ovulatory":
        feel    = ("Peak energy", C_FEEL)
        symptom = ("Fertile signs", C_SYMP)
        to_try  = ("Social / Present work", C_TRY)

    elif name == "Luteal":
        pms_window = d_in > (d_len - 3)
        if pms_window:
            feel    = ("Lower, irritable energy", C_FEEL)
            symptom = ("PMS symptoms", C_SYMP)
            to_try  = ("Stretch & early sleep", C_TRY)
        else:
            feel    = ("Steady energy", C_FEEL)
            symptom = ("Mild bloating/cravings", C_SYMP)
            to_try  = ("Maintain routines", C_TRY)

    else:
        feel, symptom, to_try = (
            ("Check in with energy", C_FEEL),
            ("—", C_SYMP),
            ("Hydrate & light activity", C_TRY)
        )

    return {"feel": feel, "symptom": symptom, "try": to_try}

# ---------- screen 3 input state + helpers ----------
DATA_PATH = "/home/pi/Interactive-Lab-Hub/Lab 2/period_data.json"

def save_data(month, day):
    try:
        with open(DATA_PATH, "w") as f:
            json.dump({"month": month, "day": day}, f)
    except Exception:
        pass

def load_data():
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r") as f:
                d = json.load(f)
                return int(d.get("month", 9)), int(d.get("day", 21))
        except Exception:
            pass
    return 9, 21

# values shown/edited on screen 3
sel_month, sel_day = load_data()
input_focus = 0   # 0 = Month, 1 = Day, 2 = Save
last_b_press_start = None
B_LONG_MS = 600
just_saved_at = 0  # for showing a brief "Saved" badge

while True:
    # derive day_of_cycle from saved input
    day_of_cycle = compute_day_of_cycle(sel_month, sel_day, total_days)
    if not buttonA.value:  # pressed
        if screen_mode == 2:
            # screen 3: A moves focus, and on Save it commits & exits
            if input_focus < 2:
                input_focus += 1            # Month -> Day -> Save
            else:
                # Before saving, make sure user didn't pick a future date
                save_data(sel_month, sel_day)
                just_saved_at = time.monotonic()
                screen_mode = 0             # back to clock
            time.sleep(0.25)                # debounce
        else:
            screen_mode = (screen_mode + 1) % 3
            time.sleep(0.25)                # debounce

    # --- Button B (short/long) behavior on screen 3 only ---
    if screen_mode == 2:
        if not buttonB.value:  # pressed
            if last_b_press_start is None:
                last_b_press_start = time.monotonic()
        else:
            if last_b_press_start is not None:
                press_ms = (time.monotonic() - last_b_press_start) * 1000
                long_press = press_ms >= B_LONG_MS

                # increment on short, decrement on long
                if input_focus == 0:  # Month
                    if long_press:
                        sel_month = 12 if sel_month == 1 else sel_month - 1
                    else:
                        sel_month = 1 if sel_month == 12 else sel_month + 1
                    # clamp day to new month length
                    sel_day = min(sel_day, days_in_month(sel_month))

                elif input_focus == 1:  # Day
                    maxd = days_in_month(sel_month)
                    if long_press:
                        sel_day = maxd if sel_day == 1 else sel_day - 1
                    else:
                        sel_day = 1 if sel_day == maxd else sel_day + 1
                # If focus is Save, B does nothing (A will save)
                last_b_press_start = None

    # clear screen
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

    if screen_mode == 0:
        # -------- Screen 1: Cycle Clock (labels moved to legend) --------
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

        date_text = datetime.now().strftime("%a, %b %d")
        draw.text((header_x, header_y), date_text, font=font_large, fill="white")

        # Phase badge on the right
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

        phase_name, phase_color, phase_idx, d_in, d_len = phase_position_for_day(day_of_cycle, phases)
        snap = get_snapshot_structured(day_of_cycle, phases)

        # Bullet rows
        row_y = sub_y + 18
        line_x = header_x

        bullet_row(draw, line_x, row_y, f"{snap['feel'][0]}",     color=snap['feel'][1])
        row_y += 20
        bullet_row(draw, line_x, row_y, f"{snap['symptom'][0]}", color=snap['symptom'][1])
        row_y += 20
        bullet_row(draw, line_x, row_y, f"{snap['try'][0]}",        color=snap['try'][1])


    elif screen_mode == 2:
        # ----------- Screen 3: Last Period Input View ------------
        panel_margin = 10
        panel_bbox = (panel_margin, panel_margin, width - panel_margin, height - panel_margin)
        rounded_rect(draw, panel_bbox, radius=10, fill="#202428")

        px = panel_bbox[0] + 12
        py = panel_bbox[1] + 10
        draw.text((px, py), "First Day of Last Period", font=font_large, fill="white")
        py += 28

        # Fields with focus highlight
        fields = [("Month", f"{sel_month:02d}", 0), ("Day", f"{sel_day:02d}", 1)]
        for label, val, idx in fields:
            is_focus = (input_focus == idx)
            label_color = "white" if is_focus else "#BFC7D1"
            draw.text((px, py), f"{label}:", font=font_medium, fill=label_color)
            # value badge
            vb_x = px + 76
            vb_y = py - 2
            vb_bg = "#3A3F46" if is_focus else "#2C3137"
            draw_badge(draw, val, vb_x, vb_y, pad_x=8, pad_y=3, bg=vb_bg, fg="white")
            py += 26

        # Save "button" (focus index 2)
        is_focus_save = (input_focus == 2)
        btn_w, btn_h = 72, 26
        btn_x = width - panel_margin - btn_w - 6
        btn_y = panel_bbox[3] - btn_h - 8
        btn_fill = "#2E7D32" if is_focus_save else "#234A27"
        rounded_rect(draw, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), radius=8, fill=btn_fill)
        sw, sh = text_size(draw, "Save", font=font_medium)
        draw.text((btn_x + (btn_w - sw)//2, btn_y + (btn_h - sh)//2), "Save", font=font_medium, fill="white")

        # Brief "Saved" badge after saving
        if just_saved_at and time.monotonic() - just_saved_at < 1.2:
            bx = px
            by = panel_bbox[1] + 6
            draw_badge(draw, "Saved", bx, by, pad_x=8, pad_y=3, bg="#355E3B", fg="white")
        elif just_saved_at:
            just_saved_at = 0  # reset once timeout passes


    # Display image
    disp.image(image, rotation)
    time.sleep(0.1)
