import paho.mqtt.client as mqtt
import time

broker = "farlab.infosci.cornell.edu"
port = 1883
username = "idd"
password = "device@theFarm"

ROUND_DURATION = 10
MIN_PLAYERS = 2

# --- State ---
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


def announce(message):
    print(message)
    client.publish("IDD/rps/status", message)


def on_message(client, userdata, msg):
    raw = msg.payload.decode()
    lower = raw.lower()
    print("\n" + raw)

    # -----------------------------------------
    # Hide waiting messages completely
    # -----------------------------------------
    if "waiting" in lower:
        return

    # -----------------------------------------
    # New round
    # -----------------------------------------
    if "new round" in lower or "time to play" in lower:
        show_text("Time to play!\nSend your choice:\nROCK, PAPER, SCISSORS!", color=(0,180,255))
        return

    # -----------------------------------------
    # Tie message
    # -----------------------------------------
    if "tie" in lower:
        show_text("TIE!\nEveryone stays in!", color=(255,255,255))
        return

    # -----------------------------------------
    # Winning move
    # -----------------------------------------
    if "winning move" in lower:
        move = raw.split(":")[-1].strip()
        show_text(f"{move} WINS\nthis round!", color=(0,255,0))
        return

    # -----------------------------------------
    # Survivors
    # -----------------------------------------
    if "survivors" in lower:
        names = raw.split(":")[-1].strip()
        show_text(f"Still in:\n{names}", color=(0,255,0))
        return

    # -----------------------------------------
    # Eliminated
    # -----------------------------------------
    if "eliminated" in lower:
        names = raw.split(":")[-1].strip()
        show_text(f"Eliminated:\n{names}", color=(255,0,0))
        return

    # -----------------------------------------
    # GAME OVER
    # -----------------------------------------
    if "champion" in lower:
        champ = raw.split(":")[-1].strip()
        show_text(f"GAME OVER!\nWinner: {champ}", color=(255,0,0))
        return

    if "game over" in lower:
        show_text("GAME OVER!", color=(255,0,0))
        return

    # --- Player quits ---
    if choice == "quit":
        if player in active_players:
            active_players.remove(player)
            announce(f"{player} left the game. ({len(active_players)} players remaining)")
            print(f"{player} quit.")
            # Auto-win if only one remains
            if len(active_players) == 1:
                sole_player = list(active_players)[0]
                announce(f"Game Over! Champion: {sole_player}")
                reset_game_prompt()
            elif len(active_players) < MIN_PLAYERS:
                waiting_for_players = True
                announce("Not enough players to continue. Waiting for new players...")
        return

    # --- Handle regular move ---
    if choice not in ["rock", "paper", "scissors"]:
        return

    if not game_active:
        # Shouldn't happen, but safety
        game_active = True
        waiting_for_players = True
        announce("New game starting! Waiting for players...")
        time.sleep(1)

    if not round_active:
        print(f"{player} played early; added to next round.")
        active_players.add(player)
        return

    # During a round
    choices[player] = choice
    active_players.add(player)
    print(f"{player} chose {choice}")


def start_round():
    """Run one full round of play."""
    global round_active, choices, waiting_for_players

    if waiting_for_players:
        announce("Waiting for enough players to join...")
        return True

    if len(active_players) < MIN_PLAYERS:
        waiting_for_players = True
        announce("Not enough players to continue. Waiting for new players...")
        return True

    # --- Begin round ---
    choices = {}
    round_active = True
    announce(f"\n New round starting! You have {ROUND_DURATION} seconds to play!")
    announce("Time to play! Send your choice: rock, paper, or scissors!")
    countdown = ROUND_DURATION
    while countdown > 0:
        print(f" {countdown}s remaining...", end="\r")
        time.sleep(1)
        countdown -= 1

    round_active = False

    if not choices:
        announce("No moves received this round. Waiting for players...")
        return True

    winner_choice = determine_winner(choices)
    if winner_choice is None:
        announce(f"It's a tie! Everyone stays in. ({choices})")
        return True

    survivors = [p for p, c in choices.items() if c == winner_choice]
    eliminated = [p for p in active_players if p not in survivors]

    announce(f"Winning move: {winner_choice.upper()}")
    announce(f"Survivors: {', '.join(survivors)}")
    if eliminated:
        announce(f"Eliminated: {', '.join(eliminated)}")

    active_players.clear()
    active_players.update(survivors)

    # --- Game end checks ---
    if len(active_players) == 1:
        announce(f"Game Over! Champion: {list(active_players)[0]}")
        reset_game_prompt()
        return False
    elif len(active_players) == 0:
        announce("Everyone eliminated! No winner.")
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
            announce("New game starting soon! Waiting for players...")
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
    announce("Rock-Paper-Scissors Elimination Host Ready!")
    while True:
        if not game_active:
            time.sleep(1)
            continue
        keep_playing = start_round()
        if not keep_playing:
            # round or game ended
            time.sleep(3)
        else:
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
