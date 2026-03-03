# 🔧 Hardware Documentation – AI Car

<!-- edited by: claude + nityam | 2026-02-27 8:00 PM IST | added edit tracking comment -->
<!-- edited by: claude + nityam | 2026-03-03 | filled GPIO pins, updated for 4WD tank-style, added voltage divider wiring -->

> This document covers all physical components used in the AI Car project.

← Back to [README](../README.md)

---

## 📋 Component List

| #  | Component                  | Quantity | Purpose                              |
|----|----------------------------|----------|--------------------------------------|
| 1  | ESP32-C6 Dev Board         | 1        | Main microcontroller                 |
| 2  | L298N Motor Driver Module  | 1        | Controls DC motors (speed + direction) |
| 3  | DC Motors (with wheels)    | 4        | Car wheel movement (2 left + 2 right, tank-style) |
| 4  | HC-SR04 Ultrasonic Sensor  | 1        | Emergency obstacle detection (local) |
| 5  | 18650 Li-ion Batteries     | 2–4      | Power supply for car                 |
| 6  | Battery Holder             | 1        | Holds 18650 cells                    |
| 7  | Smartphone                 | 1        | Camera (core) + Gyroscope & GPS (optional) |
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

### Tank-Style 4WD Wiring

We use **4 motors** in a **tank-style** configuration:
- **Motor A (Left pair):** 2 DC motors wired **in parallel** to L298N Channel A
- **Motor B (Right pair):** 2 DC motors wired **in parallel** to L298N Channel B

To turn, we drive the left and right pairs at different speeds (differential drive).

### Pin Connections (ESP32 → L298N)

| ESP32-C6 Pin  | L298N Pin | Function                         |
|---------------|-----------|----------------------------------|
| GPIO 6        | IN1       | Left motors — forward direction  |
| GPIO 7        | IN2       | Left motors — backward direction |
| GPIO 4 (PWM)  | ENA       | Left motors — speed (0–255)      |
| GPIO 10       | IN3       | Right motors — forward direction |
| GPIO 11       | IN4       | Right motors — backward direction|
| GPIO 5 (PWM)  | ENB       | Right motors — speed (0–255)     |
| GND           | GND       | Common ground                    |

> 📌 These pin numbers match `src/esp32/config.h`. If you use different pins, update that file.
>
> 🔧 **For ESP8266 (NodeMCU):** Use D-pin labels (D1=GPIO5, D2=GPIO4, D5=GPIO14, D6=GPIO12, D7=GPIO13, D8=GPIO15) and update `config.h` accordingly.

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
- **Configuration:** 4WD tank-style
  - 2 left motors wired **in parallel** → L298N Channel A
  - 2 right motors wired **in parallel** → L298N Channel B
  - Differential drive: turn by running sides at different speeds

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
18650 Batteries (7.4V) ──→ L298N VIN (Motor Power + 5V Regulator)
                               ├── Left DC Motors  (2 in parallel → Channel A)
                               └── Right DC Motors (2 in parallel → Channel B)

ESP32-C6 GPIO 6,7,4  ──→ L298N IN1, IN2, ENA (Left motors)
ESP32-C6 GPIO 10,11,5 ──→ L298N IN3, IN4, ENB (Right motors)
ESP32-C6 GPIO 2 ──→ HC-SR04 TRIG
HC-SR04 ECHO ──→ Voltage Divider (1kΩ + 2kΩ) ──→ ESP32-C6 GPIO 3
ESP32-C6 ──→ Wi-Fi ──→ Laptop (receives driving commands via HTTP)

Smartphone ──→ Wi-Fi ──→ Laptop (sends video stream via MJPEG)
```

### HC-SR04 Voltage Divider (ECHO pin → 3.3V)

The HC-SR04 ECHO pin outputs 5V, but ESP32 GPIO is 3.3V. Use a simple voltage divider:

```
HC-SR04 ECHO ──→ [1kΩ resistor] ──→ ESP32 GPIO 3
                                  │
                              [2kΩ resistor]
                                  │
                                 GND

Output voltage = 5V × 2kΩ / (1kΩ + 2kΩ) = 3.33V ✅
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
