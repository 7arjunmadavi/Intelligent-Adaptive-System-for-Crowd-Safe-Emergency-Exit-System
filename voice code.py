import time
import requests
import pyttsx3

ESP_IP = "192.168.128.6" # my ESP32 IP
POLL_SEC = 1
REPEAT_SEC = 1.5

# The person is standing facing east (right).
DIRECTION = {

    1: "straight ahead",

    2: "to the left",

    3: "to the right",

}

def speak(text):

    engine = pyttsx3.init()

    engine.setProperty("rate", 150)

    engine.say(text)

    engine.runAndWait()

    engine.stop()

# Based on which gate has fire, determine which gate to use.

PREFERRED = {

    1: 2,

    2: 3,

    3: 2,

}

def build_message(r):

    fires = [g for g, k in ((1, "f1"), (2, "f2"), (3, "f3")) if r[k]]

    if not fires:

        return None

    if len(fires) == 1:

        fire_text = f"Fire is at Gate {fires[0]}."

    else:

        fire_text = "Fire is at " + " and ".join(f"Gate {g}" for g in fires) + "."

    unsafe = {1: r["u1"], 2: r["u2"], 3: r["u3"]}

    crowd = {1: r["c1"], 2: r["c2"], 3: 0}      # There is no camera at Gate 3.

    safe_gates = [g for g in (1, 2, 3) if not unsafe[g]]

    if not safe_gates:

        return fire_text + " All gates are unsafe. Please follow staff instructions."

    # If there is fire at only one gate and its preferred gate is safe, recommend that gate.

    if len(fires) == 1 and PREFERRED[fires[0]] in safe_gates:

        safe = PREFERRED[fires[0]]

    else:

        safe = min(safe_gates, key=lambda g: crowd[g])

    return f"{fire_text} Please go {DIRECTION[safe]} and use Gate {safe}."

last_msg, last_time = "", 0

while True:

    try:

        r = requests.get(f"http://{ESP_IP}/status", timeout=2).json()

        msg = build_message(r)

        if msg:

            if msg != last_msg or time.time() - last_time > REPEAT_SEC:

                speak(msg)

                last_msg, last_time = msg, time.time()

        else:

            last_msg = ""      # Reset when the fire is gone.

    except Exception as e:

        print("Could not connect to ESP32:", e)

    time.sleep(POLL_SEC)