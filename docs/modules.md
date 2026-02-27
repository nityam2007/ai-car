# 🧩 Module Breakdown & Task Plan – AI Car

<!-- edited by: claude + nityam | 2026-02-27 8:00 PM IST | marked GPS & Gyroscope tasks as optional, added priority order note -->

> This document divides the entire project into independent modules with clear tasks, so team members can work in parallel.
>
> **Priority:** Camera + Ultrasonic + AI first → then GPS/Gyro if time permits.

← Back to [README](../README.md)

---

## 📋 Module Overview

| Module | Name              | Team Size | Dependencies       | Docs                                       |
|--------|-------------------|-----------|--------------------|--------------------------------------------|
| M1     | 🔧 Car Hardware    | 2–3       | None               | [hardware.md](hardware.md)                 |
| M2     | 📡 Sensors         | 1–2       | M1 (car body)      | [sensors.md](sensors.md)                   |
| M3     | 📱 Phone Streaming | 1–2       | None               | [software.md](software.md)                 |
| M4     | 🧠 AI Model        | 2–3       | M6 (training data) | [software.md](software.md)                 |
| M5     | 💻 Laptop Software | 2–3       | M3, M4             | [software.md](software.md)                 |
| M6     | 🛣️ Road & Signs    | 2–3       | None               | [road-simulation.md](road-simulation.md)   |
| M7     | 🔗 Integration     | All       | M1–M6              | [architecture.md](architecture.md)         |

---

## M1: 🔧 Car Hardware

**Goal:** Assemble the car body with motors, motor driver, ESP32, and batteries.

### Tasks

| #  | Task                              | Status      | Notes                              |
|----|-----------------------------------|-------------|------------------------------------|
| 1  | Get car chassis (buy or build)    | ⬜ Not Started |                                  |
| 2  | Mount DC motors on chassis        | ⬜ Not Started |                                  |
| 3  | Wire motors to L298N driver       | ⬜ Not Started | See [hardware.md](hardware.md)   |
| 4  | Wire L298N to ESP32-C6            | ⬜ Not Started | Pin mapping needed               |
| 5  | Set up battery pack (18650)       | ⬜ Not Started | 2S configuration                 |
| 6  | Test motor control (forward/back) | ⬜ Not Started | Basic Arduino/ESP code           |
| 7  | Mount phone holder on car         | ⬜ Not Started |                                  |
| 8  | Final assembly & cable management | ⬜ Not Started |                                  |

### Deliverable
✅ A car that can move forward, backward, left, right when given commands from ESP32.

---

## M2: 📡 Sensors

**Goal:** Set up ultrasonic sensor on ESP32 for emergency braking.

### Tasks

| #  | Task                                     | Status      | Notes                              |
|----|------------------------------------------|-------------|------------------------------------|
| 1  | Wire HC-SR04 to ESP32                    | ⬜ Not Started | Add voltage divider for ECHO     |
| 2  | Write ESP32 code to read distance        | ⬜ Not Started | Test with serial monitor         |
| 3  | Set emergency threshold (e.g., 15cm)     | ⬜ Not Started | Calibrate based on car speed     |
| 4  | Implement emergency stop in ESP32 code   | ⬜ Not Started | Must run BEFORE Wi-Fi commands   |
| 5  | Test emergency brake with obstacles      | ⬜ Not Started | Use boxes, hands, toy cars       |

### Deliverable
✅ ESP32 can detect obstacles within 15cm and **immediately stop motors** without any laptop/Wi-Fi involvement.

---

## M3: 📱 Phone Streaming

**Goal:** Stream live video + sensor data from phone to laptop.

### Tasks

| #  | Task                                         | Status      | Notes                            |
|----|----------------------------------------------|-------------|----------------------------------|
| 1  | Choose streaming app (IP Webcam / DroidCam)  | ⬜ Not Started | Test both, pick best           |
| 2  | Test video stream on laptop (OpenCV)         | ⬜ Not Started | `cv2.VideoCapture(url)`        |
| 3  | ⚡ Set up gyroscope data streaming (OPTIONAL) | ⬜ Not Started | Optional — will add if we can  |
| 4  | ⚡ Set up GPS data streaming (OPTIONAL)       | ⬜ Not Started | Optional — will add if we can  |
| 5  | Test all streams running simultaneously      | ⬜ Not Started | Check for lag and bandwidth    |
| 6  | Document stream URLs and setup steps         | ⬜ Not Started |                                |

### Deliverable
✅ Laptop can receive live video frames from the phone over Wi-Fi. *(Optionally: gyroscope and GPS data too, if added.)*

---

## M4: 🧠 AI Model

**Goal:** Train a model to detect traffic signs, traffic lights, and obstacles.

### Tasks

| #  | Task                                        | Status      | Notes                            |
|----|---------------------------------------------|-------------|----------------------------------|
| 1  | Define classes to detect                    | ⬜ Not Started | stop, red, yellow, green, speed, obstacle |
| 2  | Collect training images from simulated road | ⬜ Not Started | Need M6 road/signs ready       |
| 3  | Label training data                         | ⬜ Not Started | Use LabelImg or similar tool   |
| 4  | Choose model architecture                   | ⬜ Not Started | CNN / MobileNet / YOLO         |
| 5  | Train the model                             | ⬜ Not Started | Use laptop GPU if available    |
| 6  | Test model accuracy on test images          | ⬜ Not Started | Target: >80% accuracy         |
| 7  | Optimize for real-time speed                | ⬜ Not Started | Target: >10 FPS               |
| 8  | Export model for inference                  | ⬜ Not Started | .h5 / .tflite / .onnx         |

### Deliverable
✅ A trained AI model that can take a camera frame and output detected objects with labels and confidence scores.

---

## M5: 💻 Laptop Software

**Goal:** Build the main processing pipeline — receive video, run AI, make decisions, send commands.

### Tasks

| #  | Task                                        | Status      | Notes                            |
|----|---------------------------------------------|-------------|----------------------------------|
| 1  | Set up Python project structure             | ⬜ Not Started | See [software.md](software.md) |
| 2  | Write video stream receiver                 | ⬜ Not Started | `video_stream.py`              |
| 3  | Write AI model loader + predictor           | ⬜ Not Started | `ai_model.py`                  |
| 4  | Write detection logic (OpenCV processing)   | ⬜ Not Started | `detector.py`                  |
| 5  | Write decision engine                       | ⬜ Not Started | `decision_engine.py`           |
| 6  | Write ESP32 communicator                    | ⬜ Not Started | `communicator.py`              |
| 7  | ⚡ Write phone sensor receiver (OPTIONAL)    | ⬜ Not Started | `phone_sensors.py` — only if gyro/GPS added |
| 8  | Write main.py (orchestrates everything)     | ⬜ Not Started | `main.py`                      |
| 9  | Test full pipeline with recorded video      | ⬜ Not Started | Before live testing            |

### Deliverable
✅ A Python application that processes live video, detects signs/obstacles, makes decisions, and sends commands to ESP32.

---

## M6: 🛣️ Road & Signs

**Goal:** Build the simulated test environment with road, signs, lights, and obstacles.

### Tasks

| #  | Task                                     | Status      | Notes                                    |
|----|------------------------------------------|-------------|------------------------------------------|
| 1  | Design road layout on paper              | ⬜ Not Started | See [road-simulation.md](road-simulation.md) |
| 2  | Build road surface (chart paper + tape)  | ⬜ Not Started | Include lanes, intersections             |
| 3  | Build traffic signs (cardboard)          | ⬜ Not Started | Stop, speed limit, turn signs            |
| 4  | Build traffic lights (LEDs)              | ⬜ Not Started | Red, yellow, green                       |
| 5  | Prepare obstacles (toy cars, boxes)      | ⬜ Not Started |                                          |
| 6  | Take photos for training data            | ⬜ Not Started | Multiple angles, distances, lighting     |
| 7  | Set up test scenarios                    | ⬜ Not Started | See test scenarios in road-simulation.md |

### Deliverable
✅ A complete miniature road environment with signs, lights, and obstacles ready for testing + labeled training images.

---

## M7: 🔗 Integration & Testing

**Goal:** Connect all modules together and run full system tests.

### Tasks

| #  | Task                                        | Status      | Notes                            |
|----|---------------------------------------------|-------------|----------------------------------|
| 1  | Connect phone stream → laptop processing    | ⬜ Not Started | M3 + M5                       |
| 2  | Connect laptop commands → ESP32 motors      | ⬜ Not Started | M5 + M1                       |
| 3  | Verify ultrasonic emergency brake works     | ⬜ Not Started | M2 standalone                  |
| 4  | Full system test on simulated road          | ⬜ Not Started | M1–M6 together                 |
| 5  | Fix bugs and calibrate                      | ⬜ Not Started |                                |
| 6  | Record demo video                           | ⬜ Not Started | For project presentation       |
| 7  | Prepare presentation / report               | ⬜ Not Started |                                |

### Deliverable
✅ A fully working autonomous car demo on the simulated road.

---

## 📅 Suggested Work Order

```
Week 1-2: M1 (Car Hardware) + M6 (Road & Signs) — can be done in parallel
Week 2-3: M2 (Sensors) + M3 (Phone Streaming) — can be done in parallel
Week 3-4: M4 (AI Model) — needs training data from M6
Week 4-5: M5 (Laptop Software) — needs M3 and M4
Week 5-6: M7 (Integration) — bring everything together
Week 6:   Testing, debugging, demo prep
```

---

## 👥 Suggested Team Distribution (11 members)

| Module                  | Suggested Team Size | Notes                       |
|-------------------------|---------------------|-----------------------------|
| M1: Car Hardware        | 3 members           | Building, wiring, soldering |
| M2: Sensors             | 1 member            | ESP32 ultrasonic code       |
| M3: Phone Streaming     | 1 member            | App setup, streaming        |
| M4: AI Model            | 3 members           | Data collection + training  |
| M5: Laptop Software     | 2 members           | Python pipeline             |
| M6: Road & Signs        | 3 members           | Building test environment   |
| M7: Integration         | All (led by 2)      | Everyone helps with testing |

> **Note:** Some members can work on multiple modules. M6 team can also help with M4 (collecting training data). M1 team can also help with M2 (sensor wiring).

---

← Back to [README](../README.md) | Prev: [← Road Simulation](road-simulation.md)
