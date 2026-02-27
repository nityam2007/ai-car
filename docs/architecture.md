# 🏛️ System Architecture – AI Car

<!-- edited by: claude + nityam | 2026-02-27 8:00 PM IST | marked GPS & Gyroscope as optional in architecture -->

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

### Layer 1: Phone → Laptop (Sensor Data)

| Data Type       | Protocol      | Format          | Frequency       |
|-----------------|---------------|-----------------|-----------------|
| Video Stream    | HTTP (MJPEG)  | Video frames    | 15–30 FPS       |
| Gyroscope ⚡    | WebSocket/HTTP| JSON            | 10–50 Hz        |
| GPS ⚡          | WebSocket/HTTP| JSON            | 1–5 Hz          |

> ⚡ Gyroscope & GPS are **optional**. On our list — will add if we can. Core system works with video stream only.

**Flow:**
```
Phone Camera App
    ↓ (HTTP video stream URL)
Laptop OpenCV reads frames
    ↓
Each frame sent to AI model
```

### Layer 2: Laptop → ESP32 (Commands)

| Data Type       | Protocol       | Format          | Frequency       |
|-----------------|----------------|-----------------|-----------------|
| Drive Command   | HTTP / Socket  | String/JSON     | As needed       |

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
Step 1: PHONE starts streaming
    │
    ├── Video → http://phone-ip:8080/video        (CORE)
    ├── Gyro  → ws://phone-ip:8081/gyro            (OPTIONAL)
    └── GPS   → ws://phone-ip:8081/gps             (OPTIONAL)
    │
    ▼
Step 2: LAPTOP receives all data
    │
    ├── cv2.VideoCapture(stream_url) → frames      (CORE)
    ├── WebSocket client → gyro_data                (OPTIONAL)
    └── WebSocket client → gps_data                 (OPTIONAL)
    │
    ▼
Step 3: LAPTOP processes each frame
    │
    ├── Frame → AI Model → detections[]
    ├── detections + gyro + gps → Decision Engine
    └── Decision → command (GO/STOP/SLOW/LEFT/RIGHT)
    │
    ▼
Step 4: LAPTOP sends command to ESP32
    │
    └── HTTP POST http://esp32-ip/command {"cmd": "STOP"}
    │
    ▼
Step 5: ESP32 receives and executes
    │
    ├── Parse command
    ├── Set motor pins accordingly
    └── BUT FIRST: Check ultrasonic (always runs before commands)
    │
    ▼
Step 6: MOTORS move (or stop)
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

### Current: Laptop as Cloud
```
Phone → Laptop → ESP32 (3 devices, Wi-Fi dependent)
```

### Future Option 1: Raspberry Pi on Car
```
Phone/Pi Camera → Raspberry Pi (on car) → ESP32 (no laptop needed)
```

### Future Option 2: Edge AI on ESP32
```
Camera Module → ESP32 with TinyML → Motors (single device)
```

---

← Back to [README](../README.md)
