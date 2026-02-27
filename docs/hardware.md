# 🔧 Hardware Documentation – AI Car

<!-- edited by: claude + nityam | 2026-02-27 8:00 PM IST | added edit tracking comment -->

> This document covers all physical components used in the AI Car project.

← Back to [README](../README.md)

---

## 📋 Component List

| #  | Component                  | Quantity | Purpose                              |
|----|----------------------------|----------|--------------------------------------|
| 1  | ESP32-C6 Dev Board         | 1        | Main microcontroller                 |
| 2  | L298N Motor Driver Module  | 1        | Controls DC motors (speed + direction) |
| 3  | DC Motors (with wheels)    | 2–4      | Car wheel movement                   |
| 4  | HC-SR04 Ultrasonic Sensor  | 1        | Emergency obstacle detection (local) |
| 5  | 18650 Li-ion Batteries     | 2–4      | Power supply for car                 |
| 6  | Battery Holder             | 1        | Holds 18650 cells                    |
| 7  | Smartphone                 | 1        | Camera + Gyroscope + GPS             |
| 8  | Laptop                     | 1        | AI processing (cloud/server)         |
| 9  | Car Chassis                | 1        | Car body/frame                       |
| 10 | Jumper Wires               | Many     | Connections between components       |
| 11 | Breadboard (optional)      | 1        | Prototyping connections              |
| 12 | Phone Mount/Holder         | 1        | Mounts phone on car                  |

---

## 🔌 ESP32-C6 – The Controller

### What Is It? (Simple)
The ESP32-C6 is a small computer chip that controls the car. It receives commands from the laptop (like "go forward" or "stop") and tells the motors what to do. It also reads the ultrasonic sensor directly for emergency stops.

### Technical Details
- **Chip:** ESP32-C6 (RISC-V architecture)
- **Wi-Fi:** 802.11b/g/n (2.4 GHz) — used to receive commands from laptop
- **Bluetooth:** BLE 5.0 (available if needed)
- **GPIO Pins:** Used to connect motors (via L298N) and ultrasonic sensor
- **Power:** Can be powered via USB or external battery

### What It Does in This Project
1. **Receives driving commands** from laptop over Wi-Fi (stop, go, turn, speed)
2. **Reads ultrasonic sensor** directly — no Wi-Fi needed for this
3. **Controls motors** through L298N motor driver
4. **Emergency brake** — if ultrasonic detects obstacle too close, ESP32 stops motors instantly (independent of laptop)

---

## ⚡ L298N Motor Driver

### What Is It? (Simple)
The motors need more power than the ESP32 can give. The L298N is a "power bridge" — it takes small signals from ESP32 and converts them into strong signals for the motors.

### Technical Details
- **Channels:** 2 (can drive 2 DC motors independently)
- **Voltage:** Supports 5V–35V motor supply
- **Current:** Up to 2A per channel
- **Control Pins:**
  - `IN1`, `IN2` → Motor A direction
  - `IN3`, `IN4` → Motor B direction
  - `ENA`, `ENB` → Speed control (PWM)

### Pin Connections (ESP32 → L298N)

| ESP32-C6 Pin | L298N Pin | Function           |
|--------------|-----------|---------------------|
| GPIO X       | IN1       | Motor A Forward     |
| GPIO X       | IN2       | Motor A Backward    |
| GPIO X       | IN3       | Motor B Forward     |
| GPIO X       | IN4       | Motor B Backward    |
| GPIO X (PWM) | ENA       | Motor A Speed       |
| GPIO X (PWM) | ENB       | Motor B Speed       |
| GND          | GND       | Common Ground       |

> ⚠️ **Note:** Actual GPIO pin numbers will be decided during wiring. Replace `GPIO X` with final values.

---

## 🔋 Power Supply

### Battery: 18650 Li-ion Cells
- **Voltage:** 3.7V per cell (4.2V fully charged)
- **Configuration:** 2S (2 cells in series) = 7.4V — suitable for L298N
- **Capacity:** Typically 2000–3500 mAh per cell

### Power Distribution
```
18650 Batteries (7.4V)
    ├── L298N Motor Driver (powers motors)
    │       └── DC Motors
    └── ESP32-C6 (via voltage regulator or L298N 5V output)
```

### Safety Notes
- Use a battery management system (BMS) or protection circuit
- Do not short-circuit the batteries
- Charge with a proper Li-ion charger
- Do not over-discharge below 3.0V per cell

---

## 🏎️ Car Chassis & Motors

### DC Motors
- **Type:** TT DC Gear Motors (common in robotics kits)
- **Voltage:** 3V–6V (driven via L298N at higher voltage)
- **Configuration:**
  - 2WD: 2 drive motors + 1 caster wheel
  - 4WD: 4 drive motors (optional)

### Chassis
- Can be a ready-made robot car chassis kit
- Or custom-built with acrylic/cardboard
- Must have space to mount: ESP32, L298N, batteries, phone holder, ultrasonic sensor

---

## 📱 Smartphone Mounting

The phone sits on top of the car, facing forward. It needs a stable mount so the camera view doesn't shake.

### Requirements
- Phone holder or clip mounted on the chassis
- Phone should face forward (camera = car's eyes)
- Phone should be connected to the same Wi-Fi network as the laptop

---

## 🔗 Overall Wiring Summary

```
18650 Batteries ──→ L298N (Motor Power + 5V Regulator)
                         ├── DC Motor A
                         └── DC Motor B

ESP32-C6 ──→ L298N (Control Pins: IN1, IN2, IN3, IN4, ENA, ENB)
ESP32-C6 ──→ HC-SR04 Ultrasonic Sensor (Trig + Echo pins)
ESP32-C6 ──→ Wi-Fi ──→ Laptop (receives commands)

Smartphone ──→ Wi-Fi ──→ Laptop (sends video + sensor data)
```

---

## ⚠️ Common Issues & Tips

| Issue                        | Solution                                              |
|------------------------------|-------------------------------------------------------|
| Motors not spinning           | Check L298N power, check IN1-IN4 signals              |
| ESP32 keeps resetting         | Power supply too weak — use separate power for motors  |
| Ultrasonic gives wrong values | Check wiring, ensure Trig and Echo pins are correct    |
| Car pulls to one side         | Motors have different speeds — calibrate via PWM       |
| Phone falls off               | Use a better mount, add rubber bands or clips          |

---

← Back to [README](../README.md) | Next: [Software →](software.md)
