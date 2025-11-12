import paho.mqtt.client as mqtt
import time

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
    print(f"\n{msg.payload.decode()}")

client.on_message = on_message
client.connect(broker, port)
client.subscribe(topic_status)
client.loop_start()

# --- Announce join ---
client.publish(topic_choice, "join")
print(f"👋 You have joined the game as {player_name}!")
print("Waiting for round announcements...")

try:
    while True:
        msg = input("").strip().lower()
        if msg == "quit":
            client.publish(topic_choice, "quit")
            print("👋 You left the game.")
            break
        if msg not in ["rock", "paper", "scissors"]:
            print("Invalid choice.")
            continue

        client.publish(topic_choice, msg)
        print("✅ Sent your choice.")
        time.sleep(1)

finally:
    client.loop_stop()
    client.disconnect()
