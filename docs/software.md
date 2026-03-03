# 💻 Software Documentation – AI Car

<!-- edited by: claude + nityam | 2026-02-27 8:15 PM IST | added chosen streaming app (IP Webcam), actual working code, src/laptop/video_stream.py reference -->
<!-- edited by: claude + nityam | 2026-03-03 | updated tech stack with kornia-rs, actual code structure, ESP32 endpoints, working file references -->

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

The current implementation uses a **threaded pipeline** with **kornia-rs** (Rust-backed) for fastest JPEG decoding:

```
Reader Thread (persistent HTTP session)
    │
    │  parses MJPEG byte stream (FF D8..FF D9 markers)
    │  decodes JPEG via kornia-rs (2-5x faster than OpenCV)
    │  drops stale frames to keep latency low
    ▼
Queue (maxsize=2, always latest frame)
    │
    ▼
Main Thread
    ├─ ai_processor.py → lane detection + PID steering
    ├─ send command to ESP32 via HTTP (tank drive)
    └─ display with FPS/latency overlay
```

**Key files:**
- `video_stream.py` — threaded MJPEG receiver + ESP32 command sender
- `ai_processor.py` — lane detection (white centerline on black track) + PID controller

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

| Tool          | Version          | Purpose                              |
|---------------|------------------|--------------------------------------|
| Python        | 3.12             | Main language                        |
| kornia-rs     | 0.1.10           | Rust-backed JPEG decode (2-5x faster)|
| OpenCV        | 4.13+            | Image processing, display, contours  |
| NumPy         | 2.4+             | Array operations for image data      |
| requests      | 2.32+            | HTTP streaming + ESP32 commands      |
| TensorFlow / PyTorch | (future)  | AI model training & inference        |

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

The laptop sends HTTP requests to the ESP32 web server:

| Endpoint                          | Action                               |
|-----------------------------------|--------------------------------------|
| `GET /drive?left=N&right=N`       | Tank drive (N = -255 to 255)         |
| `GET /go`                         | Forward at default speed             |
| `GET /stop`                       | Stop all motors                      |
| `GET /slow`                       | Forward at slow speed                |
| `GET /reverse`                    | Backward at default speed            |
| `GET /left`                       | Pivot turn left                      |
| `GET /right`                      | Pivot turn right                     |
| `GET /status`                     | JSON: distance, speed, state, etc.   |
| `POST /command`                   | JSON body: `{"cmd":"GO"}` etc.      |

The AI pipeline uses `/drive?left=N&right=N` (tank drive) for smooth PID-based steering.
Simple commands (`/go`, `/stop`, etc.) are for manual testing from a browser.

### ESP32 Code Structure

The actual ESP32 code is in `src/esp32/`. See [`main.ino`](../src/esp32/main.ino) for the full implementation.

```
setup():
    setup_motors()          // all motors stopped
    setup_ultrasonic()      // HC-SR04 ready
    setup_wifi()            // connect to Wi-Fi
    setup_server()          // start HTTP web server

loop():
    // SAFETY FIRST - check ultrasonic (runs locally, no Wi-Fi)
    distance = read_distance_cm()
    IF distance < 15cm:
        stop_all_motors()   // INSTANT - no network delay
        state = "EMERGENCY_STOP"

    // Handle incoming HTTP commands from laptop
    server.handleClient()

    // Watchdog: stop motors if no command for 2 seconds
    check_watchdog()
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

## 📁 Code Structure

```
src/
├── laptop/
│   ├── video_stream.py      # ✅ Threaded MJPEG receiver + ESP32 commander
│   ├── ai_processor.py      # ✅ Lane detection (PID) + steering angle output
│   ├── video_stream.v2.py   # (old simple version — for reference)
│   ├── main.py              # (planned) Main entry point
│   ├── ai_model.py          # (planned) AI model loading + prediction
│   ├── detector.py          # (planned) Sign/light detection logic
│   └── phone_sensors.py     # (OPTIONAL) Gyro + GPS receiver
│
├── esp32/
│   ├── main.ino             # ✅ Arduino main sketch (setup + loop)
│   ├── config.h             # ✅ Pin definitions, Wi-Fi creds, constants
│   ├── motor_control.h      # ✅ Tank-drive motor functions (L298N)
│   ├── ultrasonic.h         # ✅ HC-SR04 distance reading
│   └── wifi_comm.h          # ✅ Wi-Fi + HTTP web server endpoints
│
└── phone/
    └── (streaming app config or custom web app)
```

> ✅ = implemented and working &nbsp;&nbsp; (planned) = to be built

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
