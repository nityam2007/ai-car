# 💻 Software Documentation – AI Car

<!-- edited by: claude + nityam | 2026-02-27 8:15 PM IST | added chosen streaming app (IP Webcam), actual working code, src/laptop/video_stream.py reference -->

> This document covers the software stack, AI model, video processing, and communication.

← Back to [README](../README.md)

---

## 📋 Software Overview

The software runs in **3 layers**:

| Layer              | Runs On     | What It Does                                    |
|--------------------|-------------|------------------------------------------------|
| **Streaming Layer** | Smartphone  | Captures video (core) + sensor data (optional), sends to laptop |
| **AI/Processing**   | Laptop      | Processes video, detects signs/objects, decides  |
| **Control Layer**   | ESP32-C6    | Receives commands, controls motors, reads sensors|

---

## 📱 Layer 1: Smartphone (Streaming)

### Video Streaming
The phone camera streams live video to the laptop over Wi-Fi.

**App We Use:** [IP Webcam by shenyaocn](https://play.google.com/store/apps/details?id=com.shenyaocn.android.WebCam) (Free, Android)

**Quick Setup:**
1. Install the app on your phone
2. Open app → tap **Start Server**
3. Note the IP shown on screen (e.g. `192.168.1.50`)
4. Phone + laptop must be on the **same Wi-Fi**
5. Stream URL: `http://<phone-ip>:8080/video`

**Other options (if needed):**
| Method              | How It Works                                          | Difficulty |
|---------------------|-------------------------------------------------------|------------|
| IP Webcam (shenyaocn) | ✅ **Our choice** — MJPEG stream over Wi-Fi         | Easy       |
| DroidCam            | Turns phone into a webcam, accessible via IP          | Easy       |
| Custom Web App      | HTML + JavaScript to access camera and stream         | Medium     |
| RTSP Stream         | Professional streaming protocol                       | Advanced   |

**Working code** → [`src/laptop/video_stream.py`](../src/laptop/video_stream.py)

```python
import cv2

PHONE_IP = "192.168.1.50"   # Change to your phone's IP
STREAM_URL = f"http://{PHONE_IP}:8080/video"

cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    print("Error: Could not open stream.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        continue

    cv2.imshow('AI Car — Phone Stream', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Phone Sensor Data (Gyroscope + GPS) — ⚡ OPTIONAL

> ⚡ **These are optional.** They are on our list — if we can add them, we will. The core system works with just the camera video stream.

The phone can also send gyroscope and GPS data. This can be done via:
- The same streaming app (some apps include sensor data)
- A separate app like **SensorServer** or **Phyphox**
- A custom web app using JavaScript `DeviceOrientation` and `Geolocation` APIs

---

## 🧠 Layer 2: Laptop (AI Processing)

### What the Laptop Does
1. **Receives** video stream from phone
2. **Processes** each frame using OpenCV
3. **Runs AI model** to detect:
   - Traffic signs (stop, speed limit)
   - Traffic lights (red, yellow, green)
   - Obstacles (cars, objects)
4. **Makes decisions** based on detections
5. **Sends commands** to ESP32

### Tech Stack on Laptop

| Tool          | Version (Suggested) | Purpose                           |
|---------------|---------------------|-----------------------------------|
| Python        | 3.9+                | Main language                     |
| OpenCV        | 4.x                 | Image/video processing            |
| NumPy         | Latest               | Array operations for image data   |
| TensorFlow / PyTorch | Latest        | AI model training & inference     |
| scikit-learn  | Latest               | ML utilities (optional)           |
| Socket / Flask | Latest              | Communication with ESP32          |

### AI Model Options

| Approach              | Pros                              | Cons                          |
|-----------------------|-----------------------------------|-------------------------------|
| Custom CNN Model      | Tailored to our signs             | Needs training data           |
| Pre-trained MobileNet | Fast, lightweight                 | May need fine-tuning          |
| YOLOv5/v8             | Real-time object detection        | Heavier, needs good GPU       |
| Template Matching     | Simple, no ML needed              | Not robust to angles/lighting |

### Decision Logic (Pseudo Code)
```
FOR each video frame:
    detections = AI_MODEL.detect(frame)
    
    IF "stop_sign" in detections:
        command = "STOP"
    ELIF "red_light" in detections:
        command = "STOP"
    ELIF "yellow_light" in detections:
        command = "SLOW"
    ELIF "speed_limit_30" in detections:
        command = "SPEED_30"
    ELIF "obstacle" in detections:
        command = "SLOW" or "STOP"
    ELSE:
        command = "GO"
    
    send_to_esp32(command)
```

---

## ⚡ Layer 3: ESP32 (Control)

### What the ESP32 Code Does
1. **Connects to Wi-Fi** (same network as laptop)
2. **Listens for commands** from laptop (via HTTP/Socket)
3. **Controls motors** based on received command
4. **Reads ultrasonic sensor** independently
5. **Emergency brake** — if object too close, override any command and STOP

### Command Protocol (Laptop → ESP32)

| Command       | Action                        |
|---------------|-------------------------------|
| `GO`          | Move forward at normal speed  |
| `STOP`        | Stop all motors               |
| `SLOW`        | Reduce speed                  |
| `SPEED_30`    | Set speed to 30% PWM         |
| `SPEED_50`    | Set speed to 50% PWM         |
| `SPEED_100`   | Set speed to 100% PWM        |
| `LEFT`        | Turn left                     |
| `RIGHT`       | Turn right                    |
| `REVERSE`     | Move backward                 |
| `E_STOP`      | Emergency stop (from ultrasonic) |

### ESP32 Code Structure (Pseudo)
```
setup():
    connect_wifi()
    setup_motor_pins()
    setup_ultrasonic_pins()

loop():
    // SAFETY FIRST - check ultrasonic
    distance = read_ultrasonic()
    IF distance < EMERGENCY_THRESHOLD:
        stop_all_motors()      // INSTANT - no Wi-Fi needed
        return

    // Then check for laptop commands
    IF new_command_received():
        command = get_command()
        execute_command(command)
```

> ⚠️ **Critical:** The ultrasonic check happens BEFORE checking laptop commands. Safety first.

---

## 🔗 Communication Architecture

```
Phone ──── Wi-Fi ────→ Laptop ──── Wi-Fi/Serial ────→ ESP32
 │                        │                               │
 ├─ Video Stream (CORE)   ├─ AI Processing                ├─ Motor Control
 ├─ Gyro Data (OPTIONAL)  ├─ Decision Making              ├─ Ultrasonic Read
 └─ GPS Data (OPTIONAL)   └─ Command Generation           └─ Emergency Brake
```

### Communication Methods

| Link                  | Protocol         | Data                    |
|-----------------------|------------------|-------------------------|
| Phone → Laptop        | HTTP (video URL) | Video frames            |
| Phone → Laptop ⚡     | HTTP/WebSocket   | Gyro + GPS data (OPTIONAL) |
| Laptop → ESP32        | HTTP / Socket    | Driving commands        |
| ESP32 → Ultrasonic    | GPIO (direct)    | Distance measurement    |

---

## 📁 Planned Code Structure

```
src/
├── laptop/
│   ├── main.py              # Main entry point
│   ├── video_stream.py      # Captures video from phone
│   ├── ai_model.py          # AI model loading + prediction
│   ├── detector.py          # OpenCV-based detection logic
│   ├── decision_engine.py   # Makes driving decisions
│   ├── communicator.py      # Sends commands to ESP32
│   └── phone_sensors.py     # (OPTIONAL) Receives gyro + GPS from phone
│
├── esp32/
│   ├── main.ino             # Arduino/ESP-IDF main file
│   ├── motor_control.h      # Motor control functions
│   ├── ultrasonic.h         # Ultrasonic sensor functions
│   └── wifi_comm.h          # Wi-Fi command receiver
│
└── phone/
    └── (streaming app config or custom web app)
```

---

## 🧪 Testing the Software

### Test Individually
1. **Video Stream:** Run phone stream → check if laptop receives frames
2. **AI Model:** Feed test images → check if detections are correct
3. **ESP32 Commands:** Send test commands from laptop → check if motors respond
4. **Ultrasonic:** Place object in front → check if ESP32 stops motors

### Test Together
1. Start phone stream
2. Start laptop AI processing
3. Start ESP32 listener
4. Place car on test road
5. Watch it drive autonomously!

---

← Back to [README](../README.md) | Prev: [← Hardware](hardware.md) | Next: [Sensors →](sensors.md)
