
import serial
import time
import joblib
import numpy as np
import pandas as pd
import warnings

from collections import Counter, deque

warnings.filterwarnings(
    "ignore",
    message=r".*sklearn\.utils\.parallel\.delayed.*",
    category=UserWarning
)

# Configuration
PORT = "COM5"
BAUD_RATE = 115200
MODEL_FILE = "gesture_model.pkl"

FEATURES = [
    "flex0", "flex1", "flex2", "flex3", "flex4",
    "ax", "ay", "az", "gx", "gy", "gz"
]

esp = None

try:
    # Load trained model
    bundle = joblib.load(MODEL_FILE)

    if isinstance(bundle, dict) and "model" in bundle:
        model = bundle["model"]
        id_to_label = bundle.get("id_to_label", {})
        feature_names = bundle.get("features", FEATURES)
    else:
        model = bundle
        id_to_label = {}
        feature_names = FEATURES

    # Prevent unnecessary parallel workers
    if hasattr(model, "n_jobs"):
        model.n_jobs = 1

    # Connect ESP32
    esp = serial.Serial(PORT, BAUD_RATE, timeout=2)
    time.sleep(2)
    esp.reset_input_buffer()

    # Prediction stabilization
    recent = deque(maxlen=5)
    last_gesture = None

    while True:

        line = esp.readline().decode(
            "utf-8", errors="ignore"
        ).strip()

        if not line:
            continue

        values = line.split(",")

        if len(values) != 11:
            continue

        try:
            readings = [float(v) for v in values]
        except ValueError:
            continue

        # Prepare model input
        X = pd.DataFrame(
            [readings],
            columns=feature_names
        )

        # Predict gesture
        prediction = model.predict(X)[0]

        if isinstance(prediction, (int, np.integer)):
            gesture = id_to_label.get(
                int(prediction), str(prediction)
            )
        else:
            gesture = str(prediction)

        gesture = gesture.strip().lower()

        if not gesture:
            continue

        # Stabilize prediction
        recent.append(gesture)

        stable_gesture, count = Counter(
            recent
        ).most_common(1)[0]

        if count >= 3 and stable_gesture != last_gesture:

            # Display only detected gesture in VS Code
            print(
                f"Gesture Detected: {stable_gesture.upper()}",
                flush=True
            )

            # Send prediction to ESP32 for LCD and Blynk
            esp.write(
                (stable_gesture + "\n").encode("utf-8")
            )

            esp.flush()

            last_gesture = stable_gesture

except KeyboardInterrupt:
    pass

except Exception as error:
    print("Error:", error)

finally:
    if esp is not None and esp.is_open:
        esp.close()
