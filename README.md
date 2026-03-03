# 🚗 AI Car – Vision-Based Autonomous Driving System

<!-- edited by: claude + nityam | 2026-02-27 8:00 PM IST | added priority order, marked GPS/Gyro as optional -->
<!-- edited by: claude + nityam | 2026-03-03 | updated project structure, tech stack, features, removed unrealistic items -->

> A miniature self-driving car that **sees** the road through a phone camera, **thinks** using AI on a laptop, and **acts** through an ESP32 controller — all in real time.

---

## 🚦 Priority Order (What We Build First)

> We build the **core system first**, then add extras one by one.

| Priority | Feature                    | Status       | Notes                                                        |
|----------|----------------------------|--------------|--------------------------------------------------------------|
| 🥇 1st   | 📷 Phone Camera + Streaming | Core         | This is the car's eyes — everything depends on this          |
| 🥇 1st   | 📏 Ultrasonic Sensor (UR)   | Core         | Safety-critical — emergency brake, runs locally on ESP32     |
| 🥇 1st   | 🧠 AI Model + OpenCV        | Core         | The brain — detects signs, lights, obstacles                 |
| 🥇 1st   | 🔧 Car Hardware + Motors    | Core         | The body — without this, nothing moves                       |
| 🥈 2nd   | 🛣️ Road & Signs             | Core         | Needed for testing and training the AI model                 |
| 🥉 3rd   | 📐 Gyroscope (Phone)        | ⚡ Optional   | Nice to have for orientation — will add if time permits      |
| 🥉 3rd   | 🗺️ GPS (Phone)              | ⚡ Optional   | Nice to have for position tracking — will add if time permits|

> ⚡ **Optional features:** These are on our list. If we can add them, we will — but the car works fully without them.

---

## 🧭 What Is This Project?

**In Simple Words:**
We built a small car that can drive itself. It watches the road using a phone camera, understands traffic signs and obstacles using AI, and controls the car motors automatically.

**In Technical Terms:**
This is a vision-based autonomous vehicle prototype using real-time video streaming, computer vision (OpenCV), machine learning-based traffic sign/object recognition, and ultrasonic-based emergency braking — orchestrated between a smartphone (camera), a laptop (acting as the cloud/server), and an ESP32-C6 microcontroller. Optionally, we plan to integrate phone gyroscope and GPS for orientation and position tracking if time permits.

---

## 📐 How It Works (Quick Overview)

```
┌──────────────────────────────────────────────────────────────────┐
│                        SMARTPHONE                                │
│   📷 Camera (Video Stream)              ← CORE                   │
│   📡 Gyroscope (Orientation/Tilt)       ← OPTIONAL (if we add it)│
│   🗺️  GPS (Position Tracking)           ← OPTIONAL (if we add it)│
│              ↓ Wi-Fi Stream                                      │
├──────────────────────────────────────────────────────────────────┤
│                    LAPTOP (Cloud/Server)                          │
│   🧠 AI Model → Detects signs, lights, obstacles                │
│   👁️  OpenCV  → Processes video frames                           │
│   📊 Decision Engine → Stop / Go / Slow / Turn                  │
│              ↓ Wi-Fi / Serial Command                            │
├──────────────────────────────────────────────────────────────────┤
│                    ESP32-C6 CONTROLLER                            │
│   ⚡ Receives commands from laptop                               │
│   🔊 Reads ultrasonic sensor LOCALLY (no laptop needed)          │
│   🚨 Emergency brake = instant, no delay                         │
│              ↓ Motor Signals                                     │
├──────────────────────────────────────────────────────────────────┤
│                      CAR HARDWARE                                │
│   🏎️  DC Motors + L298N Driver → Movement                        │
│   🔋 18650 Li-ion Batteries → Power                              │
│   📏 Ultrasonic Sensor → Emergency Obstacle Detection            │
└──────────────────────────────────────────────────────────────────┘
```

> **Key Point:** The ultrasonic sensor works **directly on the ESP32** — it does NOT go through the laptop. This means emergency braking happens **instantly**, even if Wi-Fi is slow or disconnected.

📖 **Detailed architecture →** [docs/architecture.md](docs/architecture.md)

---

## 🧩 Project Modules

This project is divided into **4 main modules**. Each can be worked on independently.

| #  | Module              | What It Covers                              | Docs Link                                      |
|----|---------------------|---------------------------------------------|-------------------------------------------------|
| 1  | 🔧 **Hardware**     | Car body, motors, ESP32, wiring, batteries  | [docs/hardware.md](docs/hardware.md)            |
| 2  | 💻 **Software**     | AI model, OpenCV, communication, streaming  | [docs/software.md](docs/software.md)            |
| 3  | 📡 **Sensors**      | Ultrasonic, phone gyro, GPS, camera         | [docs/sensors.md](docs/sensors.md)              |
| 4  | 🛣️ **Road & Signs** | Simulated road, traffic signs, lights       | [docs/road-simulation.md](docs/road-simulation.md) |

📖 **Full module breakdown & task plan →** [docs/modules.md](docs/modules.md)

---

## 🎯 Features

### ✅ What the Car Can Do

| Feature                        | How It Works                                                      |
|--------------------------------|-------------------------------------------------------------------|
| 🚦 Traffic Light Detection     | Camera sees red/yellow/green → AI decides stop/slow/go            |
| 🛑 Stop Sign Recognition       | AI model detects stop sign → car stops                            |
| 🚗 Speed Limit Detection       | Reads speed limit signs → adjusts motor speed                     |
| 🚧 Obstacle Detection (AI)     | Camera sees objects ahead → AI decides to stop or avoid           |
| 🚨 Emergency Brake (Ultrasonic)| Sensor detects close object → ESP32 **instantly** stops motors    |
| �️ Lane Following (PID)       | ✅ Camera detects white centerline → PID controller steers car    |
| �📍 Position Tracking (GPS)     | ⚡ **Optional** — Phone GPS sends location data → laptop tracks car position. *On our list, will add if we can.* |
| 📐 Orientation (Gyroscope)     | ⚡ **Optional** — Phone gyro detects tilt/turn → helps with navigation. *On our list, will add if we can.* |

### 🔑 Important Design Decisions

1. **Ultrasonic = Local Safety**
   - The ultrasonic sensor connects **directly to ESP32**
   - It does **NOT** send data to the laptop
   - If something is too close → car stops **immediately**
   - This is a **safety-critical** feature — no network delay allowed

2. **Phone = Camera + Optional Sensors**
   - Camera → video stream for AI **(CORE — always used)**
   - Gyroscope → car orientation and tilt **(OPTIONAL — on our list, will add if we can)**
   - GPS → car position on the road **(OPTIONAL — on our list, will add if we can)**
   - All sent over Wi-Fi to the laptop

3. **Laptop = The Brain (Cloud)**
   - Runs heavy AI models (can't run on ESP32)
   - Processes video frames with OpenCV
   - Makes driving decisions
   - Sends simple commands to ESP32

---

## 🏗️ Tech Stack Summary

### 💻 Software

| Tool / Library       | Purpose                                    |
|----------------------|--------------------------------------------|
| Python 3.12          | Main programming language                  |
| kornia-rs (Rust)     | Fast JPEG decoding (2-5x faster)           |
| OpenCV               | Video frame processing, image analysis     |
| NumPy                | Array operations for image data            |
| requests             | HTTP streaming + ESP32 commands            |
| ML Model (Custom)    | Traffic sign & object recognition (planned)|

### 🔧 Hardware

| Component                  | Purpose                                      |
|----------------------------|----------------------------------------------|
| ESP32-C6                   | Main controller (receives commands, reads sensors) |
| L298N Motor Driver         | Controls DC motors (direction + speed)       |
| DC Motors                  | Car wheel movement                           |
| HC-SR04 Ultrasonic Sensor  | Emergency obstacle detection (local)         |
| Smartphone                 | Camera (core) + Gyroscope & GPS (optional)   |
| 18650 Li-ion Batteries     | Power supply for car                         |
| Laptop                     | AI processing (acts as cloud server)         |

📖 **Full hardware details & wiring →** [docs/hardware.md](docs/hardware.md)

---

## 🛣️ Test Environment

We built a **miniature city road** for testing:

- 📄 **Chart paper** → Road surface with lanes
- 📦 **Cardboard** → Traffic signs (stop, speed limit)
- 💡 **Handmade traffic lights** → Red / Yellow / Green LEDs
- 🚗 **Toy cars / boxes** → Obstacles for detection

This lets us test safely without needing a real road.

📖 **Road setup guide →** [docs/road-simulation.md](docs/road-simulation.md)

---

## 🔄 System Workflow (Step by Step)

```
1. Phone camera starts streaming video over Wi-Fi
2. (Optional) Phone also sends gyroscope + GPS data to laptop — if enabled
3. Laptop receives video stream
4. AI model processes each frame:
   → Is there a stop sign? → STOP
   → Is there a red light? → STOP
   → Is there a speed limit? → ADJUST SPEED
   → Is there an obstacle? → SLOW DOWN or STOP
5. Laptop sends command to ESP32 over Wi-Fi
6. ESP32 controls motors via L298N driver
7. MEANWHILE: Ultrasonic sensor on ESP32 runs independently
   → If object detected within emergency range → INSTANT STOP
   → No laptop/Wi-Fi needed for this
```

---

## 📁 Project Structure

```
PROJECT/
├── README.md                  ← You are here
├── CHANGELOG.md               ← Project change history
├── requirements.txt           ← Python dependencies (pip install -r)
├── .gitignore
├── aicar.md                   ← Original project notes (DO NOT EDIT)
├── docs/
│   ├── architecture.md        ← System design & data flow
│   ├── hardware.md            ← Hardware components & wiring
│   ├── software.md            ← Software stack, code structure
│   ├── sensors.md             ← Sensor details (ultrasonic, camera)
│   ├── road-simulation.md     ← Test environment setup
│   └── modules.md             ← Module-wise task breakdown
├── src/
│   ├── laptop/
│   │   ├── video_stream.py    ← ✅ Threaded MJPEG receiver + ESP32 commander
│   │   ├── ai_processor.py    ← ✅ Lane detection + PID steering
│   │   └── video_stream.v2.py ← (old simple version)
│   └── esp32/
│       ├── main.ino           ← ✅ Arduino main sketch
│       ├── config.h           ← ✅ Pin defs, Wi-Fi creds, constants
│       ├── motor_control.h    ← ✅ Tank-drive motor functions
│       ├── ultrasonic.h       ← ✅ HC-SR04 distance reading
│       └── wifi_comm.h        ← ✅ Wi-Fi + HTTP web server
├── models/                    ← Trained AI models (to be added)
└── assets/                    ← Images, diagrams (to be added)
```

---

## 👥 Team

Developed as a **Diploma Semester 6 Project** by a team of **11 members**.

---

## 🧪 Future Improvements

- 🎯 Traffic sign detection using a trained CNN model
- 🚦 Traffic light color recognition (red/yellow/green)
- 📱 Mobile app for manual override control
- 🤖 Raspberry Pi on-car upgrade (remove laptop dependency)
- 📊 Dashboard web UI showing live stats from ESP32 `/status`
- 🔧 PID tuning interface for real-time gain adjustment

---

## 📚 Documentation Index

| Document                                           | Description                                    |
|----------------------------------------------------|------------------------------------------------|
| [docs/architecture.md](docs/architecture.md)       | System architecture & data flow diagrams       |
| [docs/hardware.md](docs/hardware.md)               | Hardware components, wiring, power setup       |
| [docs/software.md](docs/software.md)               | Software stack, AI model, code structure       |
| [docs/sensors.md](docs/sensors.md)                 | All sensors: ultrasonic, gyro, GPS, camera     |
| [docs/road-simulation.md](docs/road-simulation.md) | Test road setup, signs, traffic lights         |
| [docs/modules.md](docs/modules.md)                 | Module-wise task breakdown & responsibilities  |
| [CHANGELOG.md](CHANGELOG.md)                       | Project change log (append-only)               |

---

## 🚀 Goal

To demonstrate a working prototype of a **vision-based autonomous vehicle** that can:
- **See** the road (camera + sensors)
- **Understand** traffic rules (AI + computer vision)
- **React** intelligently in real time (motor control)
- **Stay safe** with local emergency braking (ultrasonic)

---

> ⚠️ **Note:** The file [aicar.md](aicar.md) contains the original project notes and must **NOT** be edited.
