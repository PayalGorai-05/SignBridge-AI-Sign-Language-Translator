
import csv
import os
import time
import serial

# ---------------- CONFIGURATION ----------------

PORT = "COM5"
BAUD_RATE = 115200
READINGS_PER_GESTURE = 50

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "my_gesture_dataset.csv")

FEATURES = [
    "flex0", "flex1", "flex2", "flex3", "flex4",
    "ax", "ay", "az", "gx", "gy", "gz"
]

COLUMNS = FEATURES + ["gesture"]

# ------------------------------------------------


def parse_sensor_line(line):
    """Accept only 11 comma-separated numeric sensor values."""
    values = line.strip().split(",")

    if len(values) != 11:
        return None

    try:
        numbers = [float(value.strip()) for value in values]
    except ValueError:
        return None

    return numbers


def main():
    esp32 = None

    try:
        print(f"Connecting to ESP32 on {PORT}...")

        esp32 = serial.Serial(
            PORT,
            BAUD_RATE,
            timeout=2
        )

        # ESP32 may reset when the serial port opens
        time.sleep(2)
        esp32.reset_input_buffer()

        print("ESP32 connected!")
        print("Waiting for sensor data...")
        print("Expected format: 100,200,300,400,500,0.1,0.2,9.8,0,0,0")
        print("Close Arduino Serial Monitor before running this script.\n")

        file_exists = (
            os.path.exists(CSV_FILE)
            and os.path.getsize(CSV_FILE) > 0
        )

        with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(COLUMNS)

            while True:
                gesture = input(
                    "Enter gesture label (or 'exit'): "
                ).strip().lower()

                if gesture == "exit":
                    print("Collection stopped.")
                    break

                if not gesture:
                    print("Gesture label cannot be empty.\n")
                    continue

                input(
                    f"Make '{gesture}' and press Enter to start collecting..."
                )

                collected = 0
                invalid = 0
                last_invalid_shown = False

                print(f"\nCollecting {READINGS_PER_GESTURE} rows for '{gesture}'...")

                while collected < READINGS_PER_GESTURE:
                    raw = esp32.readline().decode(
                        "utf-8", errors="ignore"
                    ).strip()

                    if not raw:
                        continue

                    sensor_values = parse_sensor_line(raw)

                    if sensor_values is None:
                        invalid += 1

                        # Show one example to help diagnose the format
                        if not last_invalid_shown:
                            print(f"Received non-data line: {raw}")
                            print(
                                "Expected 11 comma-separated numeric values. "
                                "Check the ESP32 Serial output format."
                            )
                            last_invalid_shown = True
                        continue

                    writer.writerow(sensor_values + [gesture])
                    file.flush()
                    collected += 1

                    if collected % 10 == 0:
                        print(f"Collected {collected}/{READINGS_PER_GESTURE}")

                print(f"Saved {collected} rows for '{gesture}'.")
                print(f"Ignored {invalid} non-data lines.")
                print(f"CSV: {CSV_FILE}\n")

        print(f"Final dataset: {CSV_FILE}")

    except serial.SerialException as error:
        print(f"\nSerial port error: {error}")
        print("Check COM5 and close Arduino Serial Monitor.")

    except KeyboardInterrupt:
        print("\nCollection interrupted.")

    finally:
        if esp32 is not None and esp32.is_open:
            esp32.close()
            print("Serial connection closed.")


if __name__ == "__main__":
    main()
