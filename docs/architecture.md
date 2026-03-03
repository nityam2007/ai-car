# 🏛️ System Architecture – AI Car

<!-- edited by: claude + nityam | 2026-02-27 8:00 PM IST | marked GPS & Gyroscope as optional in architecture -->
<!-- edited by: claude + nityam | 2026-03-03 | updated data flow with actual HTTP endpoints, kornia-rs pipeline, tank drive -->

> This document explains the full system architecture, data flow, and how all components communicate.

← Back to [README](../README.md)

---

## 🔭 Big Picture

The AI Car system has **3 main nodes** that talk to each other:

```
┌─────────────┐        Wi-Fi         ┌─────────────┐       Wi-Fi/Serial      ┌─────────────┐
│  SMARTPHONE │ ───────────────────→  │   LAPTOP    │ ──────────────────────→  │   ESP32-C6  │
│  (Sensors)  │                       │  (AI Brain) │                          │ (Controller) │
└─────────────┘                       └─────────────┘                          └──────┬──────┘
      │                                      │                                        │
   Captures:                             Processes:                              Controls:
   • Video (CORE)                        • Video frames                          • DC Motors
   • Gyro data (OPTIONAL)                • AI detection                          • Emergency brake
   • GPS data (OPTIONAL)                 • Decision making                       • Reads ultrasonic
```

---

## 🔗 Communication Layers

### Layer 1: Phone → Laptop (Video Stream)

| Data Type       | Protocol      | Format          | Frequency       |
|-----------------|---------------|-----------------|------------------|
| Video Stream    | HTTP (MJPEG)  | JPEG frames     | 15–30 FPS       |
| Gyroscope ⚡    | (not yet)     | JSON            | Optional        |
| GPS ⚡          | (not yet)     | JSON            | Optional        |

> ⚡ Gyroscope & GPS are **optional**. On our list — will add if we can. Core system works with video stream only.

**Current Implementation:**
```
Phone: IP Webcam app → http://<phone-ip>:8081/video (MJPEG)
    ↓
Laptop: video_stream.py reader thread (persistent HTTP session)
    ↓ kornia-rs decode (Rust, 2-5x faster than OpenCV)
    ↓
Queue(maxsize=2) → main thread (AI + display)
```

### Layer 2: Laptop → ESP32 (Motor Commands)

| Data Type       | Protocol       | Format                           | Frequency       |
|-----------------|----------------|----------------------------------|------------------|
| Tank Drive      | HTTP GET       | `/drive?left=N&right=N`          | ~10 Hz          |
| Simple Command  | HTTP GET       | `/go`, `/stop`, `/slow`, etc.    | As needed       |
| Status Query    | HTTP GET       | `/status` → JSON response        | As needed       |

**Current Implementation:**
```
Laptop: ai_processor.py → steering angle (PID)
    ↓ steering_to_tank() → left/right motor speeds
    ↓
GET http://<esp32-ip>/drive?left=150&right=80
    ↓
ESP32: wifi_comm.h → motor_control.h → tank_drive(150, 80)
```

**Flow:**
```
Laptop Decision Engine
    ↓ (HTTP POST or Socket message)
ESP32 Wi-Fi receiver
    ↓
Motor Control
```

### Layer 3: ESP32 ↔ Ultrasonic (Local)

| Data Type       | Protocol       | Format          | Frequency       |
|-----------------|----------------|-----------------|-----------------|
| Distance        | GPIO (direct)  | Pulse width     | 20–40 Hz        |

**Flow:**
```
ESP32 sends TRIG pulse
    ↓
Ultrasonic sends/receives sound
    ↓
ESP32 reads ECHO pulse
    ↓
Calculate distance
    ↓
If too close → EMERGENCY STOP (no laptop involved)
```

---

## 🎯 Two Types of Stopping

This is an important architectural distinction:

### 1. AI-Based Stop (Via Laptop)
```
Camera sees stop sign
    → Phone sends video to Laptop
    → AI model detects "stop_sign"
    → Laptop sends "STOP" command to ESP32
    → ESP32 stops motors

⏱️ Response Time: 200ms – 1000ms (includes network + processing)
🎯 Use Case: Traffic rules, signs, lights
```

### 2. Emergency Stop (Local on ESP32)
```
Ultrasonic detects object at < 15cm
    → ESP32 reads sensor directly
    → ESP32 stops motors IMMEDIATELY

⏱️ Response Time: < 5ms (no network involved)
🎯 Use Case: Crash prevention, safety
```

> **Why both?** The AI stop handles "intelligent" decisions (understanding signs), while the emergency stop handles "reflex" safety (something is about to hit). Just like a human driver — you follow traffic rules (brain) but also slam the brakes if something jumps in front of you (reflex).

---

## 🔄 Complete Data Flow Diagram

```
Step 1: PHONE starts streaming (IP Webcam app)
    │
    └── Video → http://<phone-ip>:8081/video  (MJPEG stream)
    │
    ▼
Step 2: LAPTOP receives video stream
    │
    ├── video_stream.py: Reader Thread (persistent HTTP, kornia-rs decode)
    │   └── Queue(maxsize=2) → always latest frame
    │
    ▼
Step 3: LAPTOP processes each frame
    │
    ├── ai_processor.py: ROI → grayscale → threshold → contours → PID
    │   └── Output: steering angle in degrees (+right / -left)
    │
    ▼
Step 4: LAPTOP sends tank-drive command to ESP32
    │
    └── GET http://<esp32-ip>/drive?left=N&right=N
    │   (steering angle → differential motor speeds)
    │
    ▼
Step 5: ESP32 receives and executes
    │
    ├── wifi_comm.h: WebServer parses /drive request
    ├── motor_control.h: tank_drive(left, right)
    └── BUT FIRST: ultrasonic.h checks distance (always runs before commands)
    │
    ▼
Step 6: MOTORS move (or stop if emergency)
```

---

## 🌐 Network Setup

All devices must be on the **same Wi-Fi network**.

```
Wi-Fi Router / Hotspot
    ├── Phone:  192.168.1.X  (streaming video + sensors)
    ├── Laptop: 192.168.1.Y  (AI processing)
    └── ESP32:  192.168.1.Z  (motor control)
```

### Options for Wi-Fi
1. **Home Router** — all devices connect to home Wi-Fi
2. **Phone Hotspot** — phone creates hotspot, laptop + ESP32 connect to it
3. **Laptop Hotspot** — laptop creates hotspot (but phone camera quality may vary)

> **Recommended:** Use a dedicated Wi-Fi router or phone hotspot for consistent connection.

---

## 🔐 Priority & Safety Architecture

```
PRIORITY LEVELS (highest to lowest):

1. 🚨 EMERGENCY STOP (Ultrasonic on ESP32)
   - Always runs, cannot be overridden by laptop
   - Triggered when object < 15cm
   
2. 🛑 AI STOP (Laptop command)  
   - Stop sign, red light detected
   
3. 🐢 AI SLOW (Laptop command)
   - Yellow light, speed limit, distant obstacle
   
4. 🚗 AI GO (Laptop command)
   - Clear road, green light

ESP32 Logic:
    if ultrasonic < emergency_threshold:
        → STOP (override everything)
    else:
        → Follow laptop command
```

---

## 🔮 Architecture Evolution (Future)

### Current: Laptop as Brain
```
Phone (Camera) → Laptop (AI + PID) → ESP32 (Motors) — 3 devices, all on Wi-Fi
```

### Future Option: Raspberry Pi on Car
```
Pi Camera → Raspberry Pi (on car, runs AI) → ESP32 (motors) — no laptop needed
```

> The current 3-device architecture works well for our diploma project. A Raspberry Pi upgrade would make the car fully self-contained.

---

← Back to [README](../README.md)
