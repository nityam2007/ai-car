# 📋 CHANGELOG – AI Car Project

<!-- edited by: claude + nityam | 2026-02-27 8:00 PM IST | added new changelog entry -->

> **Rules:** Append only. Never edit existing entries. Latest entries go on top.

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
