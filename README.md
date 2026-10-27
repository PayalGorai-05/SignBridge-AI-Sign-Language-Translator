# SignBridge: AI-Enabled Smart Glove for Sign Language Recognition and IoT

**An ESP32-based wearable system integrating Embedded Systems, Machine Learning, and IoT.**

## 📌 Project Overview

SignBridge is an AI-enabled smart glove designed to recognize predefined hand gestures using flex sensors, an MPU6050 motion sensor, and machine learning.

The system uses an ESP32 microcontroller to acquire real-time sensor readings and transmit them to a Python-based machine learning application running on a laptop.

The trained machine learning model classifies gestures and sends the predicted labels back to the ESP32 for display on a 16×2 LCD.

The system also integrates Blynk IoT for virtual home automation, allowing users to control virtual light and fan states using hand gestures.

**Project Type:** Final Year B.Tech Group Project

---

## 🚀 Key Features

- Real-time recognition of nine predefined hand gestures
- Five flex sensors for finger-bending detection
- MPU6050 accelerometer and gyroscope for motion sensing
- ESP32-based sensor acquisition and processing
- Python-based machine learning classification
- Five machine learning algorithms implemented and evaluated
- Random Forest classification with 98.00% testing accuracy
- Bidirectional ESP32–Python serial communication
- 16×2 I2C LCD for gesture display
- Blynk IoT-based virtual light and fan control
- USB-powered hardware prototype

---

## 🛠️ Technologies Used

### Hardware
- ESP32 DevKit (ESP32-WROOM-32)
- Five Resistive Flex Sensors
- Five 12 kΩ Resistors
- MPU6050 Accelerometer and Gyroscope
- 16×2 I2C LCD
- USB Cable
- Smart Glove

### Programming Languages
- Python
- Arduino C++

### Machine Learning
- Decision Tree
- Random Forest
- K-Nearest Neighbors (KNN)
- Support Vector Machine (SVM)
- XGBoost

### Python Libraries
- NumPy
- Pandas
- Scikit-learn
- XGBoost
- Matplotlib
- Joblib
- PySerial

### Development Tools
- Arduino IDE
- Visual Studio Code
- Blynk IoT

---

## ⚙️ System Architecture

The working principle of SignBridge involves the following stages:

1. Five flex sensors measure individual finger bending.
2. The MPU6050 captures acceleration and angular velocity.
3. ESP32 acquires eleven numerical sensor features.
4. Sensor readings are transmitted to the laptop through USB serial communication.
5. A trained Random Forest model predicts the corresponding gesture.
6. Python sends the recognized gesture to the ESP32.
7. ESP32 displays the gesture on the LCD.
8. ESP32 updates the Blynk IoT dashboard through Wi-Fi.

### System Workflow

```text
         SIGNBRIDGE SMART GLOVE
                  |
                  v
         Five Flex Sensors
                  +
               MPU6050
                  |
                  v
             ESP32 DevKit
                  |
          USB Serial (115200)
                  |
                  v
           Python Application
                  |
                  v
         Random Forest Model
                  |
                  v
          Predicted Gesture
                  |
          USB Serial Return
                  |
                  v
             ESP32 DevKit
               /     \
              /       \
             v         v
        16x2 LCD    Blynk IoT
                    Dashboard
```

Machine learning inference is performed on the laptop, not directly on the ESP32.

---

## 🔌 Hardware Pin Configuration

| Component | ESP32 Pin |
|-----------|-----------|
| Thumb Flex Sensor | GPIO34 |
| Index Flex Sensor | GPIO35 |
| Middle Flex Sensor | GPIO33 |
| Ring Flex Sensor | GPIO32 |
| Little Flex Sensor | GPIO36 (VP) |
| MPU6050 SDA | GPIO21 |
| MPU6050 SCL | GPIO22 |
| LCD SDA | GPIO21 |
| LCD SCL | GPIO22 |

Each flex sensor is connected through a voltage-divider circuit using a 12 kΩ resistor.

The MPU6050 and LCD share the I2C communication bus.

### I2C Addresses

- MPU6050: `0x68`
- LCD: `0x27`

### Power Supply

The complete prototype is powered through a USB connection from a laptop.

---

## 🤖 Machine Learning Implementation

The SignBridge gesture recognition system uses supervised machine learning.

### Dataset Information

| Parameter | Value |
|-----------|-------|
| Total Samples | 4,500 |
| Gesture Classes | 9 |
| Samples per Class | 500 |
| Input Features | 11 |
| Training Samples | 3,600 |
| Testing Samples | 900 |
| Train-Test Split | 80:20 |

### Input Features

```python
FEATURES = [
    "flex0", "flex1", "flex2", "flex3", "flex4",
    "ax", "ay", "az", "gx", "gy", "gz"
]
```

The dataset contains five flex sensor values and six MPU6050 measurements.

### Recognized Gestures

1. Attention
2. Greeting
3. Goodbye
4. Question
5. Victory
6. Light ON
7. Light OFF
8. Fan ON
9. Fan OFF

---

## 📊 Machine Learning Model Comparison

Five machine learning models were trained and evaluated using the same training and testing dataset split.

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Decision Tree | 94.56% | 94.58% | 94.56% | 94.56% |
| Random Forest | **98.00%** | **98.08%** | **98.00%** | **98.00%** |
| KNN | 94.11% | 94.29% | 94.11% | 94.10% |
| SVM | 94.56% | 95.26% | 94.56% | 94.55% |
| XGBoost | 97.67% | 97.70% | 97.67% | 97.67% |

### Best Performing Model: Random Forest

The Random Forest classifier achieved the highest classification accuracy.

**Final Performance:**

- Training Accuracy: 100.00%
- Testing Accuracy: 98.00%
- Weighted Precision: 98.08%
- Weighted Recall: 98.00%
- Weighted F1-Score: 98.00%
- Correct Predictions: 882 out of 900

The trained classifier is saved as:

`gesture_model.pkl`

**Evaluation Note:** The reported accuracy was obtained using a stratified sample-level test split. Performance across completely new users and recording sessions requires additional validation.

---

## 🌐 Blynk IoT Integration

SignBridge incorporates Blynk IoT for gesture monitoring and virtual home automation.

### Virtual Pin Configuration

| Virtual Pin | Function |
|-------------|----------|
| V0 | Virtual Light Control |
| V1 | Virtual Fan Control |
| V2 | Predicted Gesture Text |

### Gesture-Based Automation

| Gesture | Action |
|---------|--------|
| Light ON | Virtual Light ON |
| Light OFF | Virtual Light OFF |
| Fan ON | Virtual Fan ON |
| Fan OFF | Virtual Fan OFF |

The Blynk dashboard also displays the recognized gesture through V2.

**Note:** The current implementation uses virtual appliance states. No physical relays or electrical appliances are connected.

---

## 📁 Repository Structure

```text
SignBridge-AI-Sign-Language-Translator/
│
├── hardware/
│   └── SignBridge_ESP32.ino
│
├── machine_learning/
│   ├── train_model.py
│   ├── predict_live.py
│   └── gesture_model.pkl
│
├── dataset/
│   └── my_gesture_dataset.csv
│
├── results/
│   ├── model_accuracy_comparison.png
│   ├── all_model_metrics_comparison.png
│   ├── confusion_matrix.png
│   └── model_evaluation_metrics.csv
│
├── diagrams/
│
├── images/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 💻 Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/SignBridge-AI-Sign-Language-Translator.git
```

```bash
cd SignBridge-AI-Sign-Language-Translator
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 2: Install Python Libraries

```bash
pip install numpy pandas scipy scikit-learn xgboost matplotlib joblib pyserial
```

### Step 3: Upload ESP32 Firmware

1. Open Arduino IDE.
2. Select the ESP32 development board.
3. Install the required Arduino libraries.
4. Open `SignBridge_ESP32.ino`.
5. Configure Wi-Fi and Blynk credentials locally.
6. Select the correct COM port.
7. Upload the program to ESP32.

Never publish actual Wi-Fi passwords or Blynk authentication tokens.

### Step 4: Train the Machine Learning Model

The training script expects the dataset in its working directory by default.

Place a copy of `my_gesture_dataset.csv` inside the `machine_learning` folder, or update `DATA_FILE` in `train_model.py` to point to `../dataset/my_gesture_dataset.csv`.

Run the training script from the `machine_learning` directory:

```bash
cd machine_learning
python train_model.py
```

The program trains and evaluates five machine learning models and saves the selected trained classifier.

Training may overwrite an existing `gesture_model.pkl`, so retain a backup if needed.

### Step 5: Run Real-Time Gesture Recognition

Connect the ESP32 to the laptop through USB.

Close the Arduino Serial Monitor before running Python.

Ensure the serial port and baud rate are correctly configured in `predict_live.py`.

```bash
python predict_live.py
```

### Example Output

```text
Gesture Detected: GREETING
Gesture Detected: VICTORY
Gesture Detected: LIGHT ON
Gesture Detected: FAN OFF
Gesture Detected: GOODBYE
```

The recognized gesture is transmitted to ESP32 for LCD display and Blynk IoT integration.

---

## 📈 Results

The implemented system demonstrates:

- Real-time acquisition of finger-bending and motion data
- Machine learning-based gesture classification
- 98.00% Random Forest testing accuracy
- ESP32–Python bidirectional communication
- Gesture output on a 16×2 LCD
- Blynk IoT-based virtual home automation

Evaluation graphs and the confusion matrix are available in the `results` folder.

---

## 🔮 Future Scope

Potential improvements include:

- Expanding the gesture vocabulary
- Collecting additional user-independent datasets
- Improving recognition across different hand sizes and sensor placements
- Deploying optimized machine learning models on embedded hardware
- Developing a dedicated mobile application
- Adding optional speech output
- Extending IoT integration to physical appliances with appropriate electrical safety measures

---

## 🎓 Project Information

**Project Name:** SignBridge

**Project Type:** Final Year B.Tech Group Project

**Domain:** Embedded Systems, Artificial Intelligence, Machine Learning, and Internet of Things

**Department:** Electronics and Communication Engineering

**Institution:** Bharati Vidyapeeth (Deemed to be University) College of Engineering, Pune

---

## 📌 Disclaimer

SignBridge is an academic prototype designed to recognize a limited set of predefined hand gestures.

It is not intended to replace complete natural sign language interpretation systems.

The system demonstrates the integration of wearable sensors, embedded systems, machine learning, and IoT technologies.
