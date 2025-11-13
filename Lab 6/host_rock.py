import paho.mqtt.client as mqtt
import time
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# --- Display setup (matches Human Greeter wiring) ---
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
    bbox = draw.textbbox((0, 0), title, font=font_big)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - tw) // 2, 40), title, font=font_big, fill=color)
    if subtitle:
        bbox2 = draw.textbbox((0, 0), subtitle, font=font_sm)
        sw, sh = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
        draw.text(((width - sw) // 2, 40 + th + 10), subtitle, font=font_sm, fill=color)
    disp.image(image)

# --- Startup welcome ---
show_text("Welcome,", "Rock–Paper–Scissors Host", color=(0, 180, 255))
time.sleep(5)
show_text("Waiting for", "players to join...", color=(255, 255, 0))

# --- MQTT Configuration ---
broker = "farlab.infosci.cornell.edu"
port = 1883
username = "idd"
password = "device@theFarm"

ROUND_DURATION = 10
MIN_PLAYERS = 2

# --- Game State ---
choices = {}
active_players = set()
round_active = False
game_active = False
waiting_for_players = False

# --- MQTT Setup ---
client = mqtt.Client()
client.username_pw_set(username, password)

def determine_winner(players_choices):
    """Determine which choice wins overall."""
    unique_choices = set(players_choices.values())
    if len(unique_choices) == 1 or len(unique_choices) == 3:
        return None
    if unique_choices == {"rock", "scissors"}:
        return "rock"
    if unique_choices == {"scissors", "paper"}:
        return "scissors"
    if unique_choices == {"paper", "rock"}:
        return "paper"

def announce(message, color=(255, 255, 0)):
    """Send message to all players and display it on the host screen."""
    print(message)
    show_text(message, color=color)
    client.publish("IDD/rps/status", message)

def on_message(client, userdata, msg):
    """Handle player messages for join, quit, or moves."""
    global round_active, choices, active_players, game_active, waiting_for_players
    player = msg.topic.split("/")[-1]
    choice = msg.payload.decode().strip().lower()

    # --- Player joins ---
    if choice == "join":
        if player not in active_players:
            active_players.add(player)
            print(f"{player} joined (waiting room).")
            announce(f"{player} joined the game! ({len(active_players)} players now)")

            if not game_active:
                game_active = True
                waiting_for_players = True
                announce("New Rock-Paper-Scissors game starting!")
                announce("Waiting for players to join...")
                time.sleep(1)

            if waiting_for_players and len(active_players) >= MIN_PLAYERS:
                waiting_for_players = False
                announce("Enough players joined! Get ready to play...")
                time.sleep(2)
        return

    # --- Player quits ---
    if choice == "quit":
        if player in active_players:
            active_players.remove(player)
            announce(f"{player} left the game. ({len(active_players)} players left)")
            print(f"{player} quit.")
            if len(active_players) == 1:
                sole_player = list(active_players)[0]
                announce(f"Game Over! Champion: {sole_player}", color=(0, 255, 0))
                reset_game_prompt()
            elif len(active_players) < MIN_PLAYERS:
                waiting_for_players = True
                announce("⚠ Not enough players to continue. Waiting for new players...")
        return

    # --- Player move ---
    if choice not in ["rock", "paper", "scissors"]:
        return

    if not game_active:
        game_active = True
        waiting_for_players = True
        announce("New game starting! Waiting for players...")
        time.sleep(1)

    if not round_active:
        print(f"{player} played early; added to next round.")
        active_players.add(player)
        return

    choices[player] = choice
    active_players.add(player)
    print(f"{player} chose {choice}")

def start_round():
    """Run one full round of play."""
    global round_active, choices, waiting_for_players

    if waiting_for_players:
        announce("⏸ Waiting for enough players to join...")
        return True

    if len(active_players) < MIN_PLAYERS:
        waiting_for_players = True
        announce("⚠ Not enough players to continue. Waiting for new players...")
        return True

    choices.clear()
    round_active = True
    announce(f"New round! {ROUND_DURATION}s to play!", color=(255, 255, 0))
    announce("Send your move: rock, paper, or scissors!")
    countdown = ROUND_DURATION
    while countdown > 0:
        print(f" {countdown}s remaining...", end="\r")
        time.sleep(1)
        countdown -= 1

    round_active = False

    if not choices:
        announce("No moves this round. Waiting for players...")
        return True

    winner_choice = determine_winner(choices)
    if winner_choice is None:
        announce(f"Tie! Everyone stays in. ({choices})", color=(255, 255, 255))
        return True

    survivors = [p for p, c in choices.items() if c == winner_choice]
    eliminated = [p for p in active_players if p not in survivors]
    color_map = {"rock": (255, 0, 0), "paper": (0, 255, 0), "scissors": (0, 0, 255)}
    win_color = color_map.get(winner_choice, (255, 255, 0))

    announce(f"Winning move: {winner_choice.upper()}", color=win_color)
    announce(f"Survivors: {', '.join(survivors)}", color=(0, 255, 0))
    if eliminated:
        announce(f"Eliminated: {', '.join(eliminated)}", color=(255, 0, 0))

    active_players.clear()
    active_players.update(survivors)

    if len(active_players) == 1:
        announce(f"Game Over! Champion: {list(active_players)[0]}", color=(0, 255, 0))
        reset_game_prompt()
        return False
    elif len(active_players) == 0:
        announce("Everyone eliminated! No winner.", color=(255, 255, 255))
        reset_game_prompt()
        return False
    else:
        return True

def reset_game_prompt():
    """Ask the host whether to start another game."""
    global game_active, waiting_for_players
    announce("Game finished!")
    print("\nGame over!")
    while True:
        again = input("Play again? (y/n): ").strip().lower()
        if again == "y":
            announce("🔄 New game starting soon! Waiting for players...")
            waiting_for_players = True
            game_active = True
            active_players.clear()
            time.sleep(2)
            break
        elif again == "n":
            announce("Host ending session.")
            game_active = False
            waiting_for_players = False
            active_players.clear()
            break

def game_loop():
    global game_active
    announce("Rock–Paper–Scissors Host Ready!")
    while True:
        if not game_active:
            time.sleep(1)
            continue
        keep_playing = start_round()
        time.sleep(3)
        if not keep_playing:
            time.sleep(3)

# --- MQTT setup ---
client.on_message = on_message
client.connect(broker, port)
client.subscribe("IDD/rps/choices/#")
client.loop_start()

try:
    game_loop()
except KeyboardInterrupt:
    print("\nStopping host...")
finally:
    client.loop_stop()
    client.disconnect()
