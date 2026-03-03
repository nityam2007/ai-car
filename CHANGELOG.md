# 📋 CHANGELOG – AI Car Project

<!-- edited by: claude + nityam | 2026-02-27 8:00 PM IST | added new changelog entry -->

> **Rules:** Append only. Never edit existing entries. Latest entries go on top.

---

## [2026-03-03 | Evening IST] — claude + nityam

### 📝 What Changed
- **Created** `src/esp32/main.ino` — Arduino main sketch: Wi-Fi web server + ultrasonic safety + motor control loop
- **Created** `src/esp32/config.h` — Pin definitions (GPIO 2-11), Wi-Fi creds, safety thresholds, speed defaults
- **Created** `src/esp32/motor_control.h` — Tank-drive motor functions for 4WD (2 left + 2 right via L298N)
- **Created** `src/esp32/ultrasonic.h` — HC-SR04 distance reading with emergency detection
- **Created** `src/esp32/wifi_comm.h` — HTTP web server with /drive, /stop, /status, /go, /command endpoints (ESP32 + ESP8266 compatible)
- **Updated** `src/laptop/video_stream.py` — Added ESP32 command sending: steering→tank drive conversion, rate-limited HTTP, stop on quit/AI-off
- **Updated** `docs/hardware.md` — Filled GPIO pin numbers (GPIO 4-11 for L298N, GPIO 2-3 for HC-SR04), added voltage divider diagram, updated for 4WD tank-style
- **Updated** `docs/software.md` — Updated tech stack (kornia-rs, Python 3.12), actual code structure with ✅ markers, HTTP endpoint table, kornia-rs pipeline diagram
- **Updated** `docs/architecture.md` — Updated data flow with actual endpoints (/drive?left=N&right=N), kornia-rs pipeline, actual file references
- **Updated** `docs/sensors.md` — Filled GPIO pins (GPIO 2 TRIG, GPIO 3 ECHO), added voltage divider details, removed LiDAR from future sensors
- **Updated** `docs/modules.md` — Updated task statuses: M2 ultrasonic code ✅, M3 streaming ✅, M5 video_stream + ai_processor + communicator ✅
- **Updated** `README.md` — Updated project structure with actual files, tech stack with kornia-rs, lane following as working feature, realistic future improvements

### 🔧 Key Decisions Made
- **Tank-style 4WD:** 2 left motors in parallel (L298N Ch.A) + 2 right motors in parallel (L298N Ch.B), differential drive for turning
- **HTTP API for motor commands:** GET /drive?left=N&right=N (N = -255 to 255), simple and browser-testable
- **Steering conversion:** PID angle → normalized [-1,1] → differential motor speeds for tank drive
- **Safety layers:** Ultrasonic emergency stop (local, <5ms) + watchdog (stop if no command for 2s) + ESP32 rejects drive commands during emergency
- **ESP32 + ESP8266 compatible:** Same code works on both via #ifdef, analogWrite for PWM
- **Voltage divider required:** HC-SR04 ECHO (5V) → 1kΩ + 2kΩ divider → 3.3V for ESP32 GPIO

### 📁 Files Added/Modified
```
src/esp32/main.ino           (NEW)
src/esp32/config.h           (NEW)
src/esp32/motor_control.h    (NEW)
src/esp32/ultrasonic.h       (NEW)
src/esp32/wifi_comm.h        (NEW)
src/laptop/video_stream.py   (MODIFIED)
docs/hardware.md             (MODIFIED)
docs/software.md             (MODIFIED)
docs/architecture.md         (MODIFIED)
docs/sensors.md              (MODIFIED)
docs/modules.md              (MODIFIED)
README.md                    (MODIFIED)
CHANGELOG.md                 (MODIFIED)
```

---

## [2026-02-27 | 8:15 PM IST] — claude + nityam

### 📝 What Changed
- **Created** `src/laptop/video_stream.py` — Working phone camera stream receiver using OpenCV
- **Decided** streaming app: [IP Webcam by shenyaocn](https://play.google.com/store/apps/details?id=com.shenyaocn.android.WebCam)
- **Updated** `docs/software.md` — Added chosen app, setup steps, working code reference

### 🔧 Key Decisions Made
- **Streaming App:** IP Webcam by shenyaocn (free, Android, MJPEG over Wi-Fi)
- Stream URL format: `http://<phone-ip>:8080/video`
- First working code added to `src/laptop/`

### 📁 Files Added/Modified
```
src/laptop/video_stream.py   (NEW)
docs/software.md             (MODIFIED)
CHANGELOG.md                 (MODIFIED)
```

---

## [2026-02-27 | 8:00 PM IST] — claude + nityam

### 📝 What Changed
- **Edited** `README.md` — Added priority order section (Camera + UR + AI first), marked GPS & Gyroscope as optional
- **Edited** `docs/sensors.md` — Marked GPS & Gyroscope as optional features ("on our list, will add if we can")
- **Edited** `docs/architecture.md` — Marked Gyro/GPS as optional in all diagrams and communication layers
- **Edited** `docs/software.md` — Marked Gyro/GPS streaming & phone_sensors.py as optional
- **Edited** `docs/modules.md` — Marked Gyro/GPS tasks as optional in M3 and M5
- **Edited** `docs/hardware.md` — Added edit tracking comment
- **Edited** `docs/road-simulation.md` — Added edit tracking comment
- **Added** `<!-- edited by: name | timestamp | description -->` comments in all files for change tracking
- **Initialized** Git repo, pushed to GitHub as private repo

### 🔧 Key Decisions Made
- **Priority order set:** Camera → Ultrasonic → AI Model → Road/Signs first. GPS & Gyroscope are optional extras.
- GPS & Gyroscope labeled as: "Optional — on our list, if we can add it we will"
- All file edits now carry `<!-- edited by: name | timestamp -->` comments for traceability
- CHANGELOG entries include person name + timestamp

### 📁 Files Modified
```
README.md
CHANGELOG.md
docs/architecture.md
docs/hardware.md
docs/software.md
docs/sensors.md
docs/road-simulation.md
docs/modules.md
```

---

## [2026-02-27 | 7:30 PM IST] — claude + nityam

### 📝 What Changed
- **Created** `README.md` — Full project overview with module-wise breakdown, beginner-friendly language, and tech details
- **Created** `CHANGELOG.md` — This file. Append-only change log with timestamps
- **Created** `docs/architecture.md` — System architecture, data flow, communication layers
- **Created** `docs/hardware.md` — All hardware components, wiring info, power setup
- **Created** `docs/software.md` — Software stack, AI model details, code structure plan
- **Created** `docs/sensors.md` — Sensor details: ultrasonic (local emergency brake), phone gyro, GPS, camera
- **Created** `docs/road-simulation.md` — Test environment setup guide (road, signs, lights, obstacles)
- **Created** `docs/modules.md` — Module-wise task breakdown and plan

### 🔧 Key Decisions Made
- Ultrasonic sensor runs **locally on ESP32** — not connected to laptop (cloud). Emergency brake is instant.
- Phone acts as **multi-sensor hub**: camera + gyroscope + GPS
- Laptop acts as **cloud/server** — runs AI model, sends commands to ESP32
- Project documentation split into modular docs for easier management

### 📁 Files Added
```
README.md
CHANGELOG.md
docs/architecture.md
docs/hardware.md
docs/software.md
docs/sensors.md
docs/road-simulation.md
docs/modules.md
```

---

<!-- 
TEMPLATE FOR NEW ENTRIES (copy-paste this at the TOP, above the latest entry):

## [YYYY-MM-DD | HH:MM AM/PM IST] — person_name

### 📝 What Changed
- 

### 🔧 Key Decisions Made
- 

### 📁 Files Added/Modified
```

```

---
-->
