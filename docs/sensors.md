# 📡 Sensors Documentation – AI Car

<!-- edited by: claude + nityam | 2026-02-27 8:00 PM IST | marked GPS & Gyroscope as optional, camera + ultrasonic are core priority -->

> This document covers all sensors used in the project: ultrasonic, phone camera (core), and optionally phone gyroscope & GPS.

← Back to [README](../README.md)

---

## 📋 Sensor Overview

| #  | Sensor              | Location       | Connected To   | Purpose                        | Cloud/Laptop? | Priority          |
|----|---------------------|----------------|----------------|--------------------------------|---------------|-------------------|
| 1  | 📷 Camera           | Phone (on car) | Laptop (Wi-Fi) | Video stream for AI            | ✅ Yes         | 🥇 **Core**       |
| 2  | 📏 Ultrasonic       | Car (front)    | ESP32 (direct) | Emergency obstacle detection   | ❌ No (LOCAL)  | 🥇 **Core**       |
| 3  | 📐 Gyroscope        | Phone (on car) | Laptop (Wi-Fi) | Orientation, tilt detection    | ✅ Yes         | ⚡ **Optional**    |
| 4  | 🗺️ GPS              | Phone (on car) | Laptop (Wi-Fi) | Position tracking              | ✅ Yes         | ⚡ **Optional**    |

> ⚡ **Gyroscope & GPS are optional.** They are on our list — if we can add them, we will. The car works fully with just Camera + Ultrasonic.

---

## 📏 Ultrasonic Sensor (HC-SR04)

### What Is It? (Simple)
Think of it like a bat. It sends out a sound wave, and when the wave hits something, it bounces back. By measuring how long the bounce takes, we know how far away the object is.

### Why Is It Special in This Project?

> ⚠️ **CRITICAL DESIGN DECISION:**
> The ultrasonic sensor is connected **directly to the ESP32** — it does **NOT** send data to the laptop.

**Why?**
- If we sent ultrasonic data to the laptop → laptop processes it → sends stop command back → that adds **delay** (100ms–500ms+)
- At that speed, the car might **already crash**
- So instead, ESP32 reads the sensor **locally** and stops the motors **instantly**
- This is a **safety-critical** system — no network dependency

### How It Works
```
ESP32 sends a TRIGGER pulse (10μs HIGH)
    ↓
Sound wave travels to obstacle and bounces back
    ↓
ESP32 receives ECHO pulse
    ↓
Distance = (Echo Time × Speed of Sound) / 2
    ↓
If distance < threshold → EMERGENCY STOP
```

### Technical Details

| Specification        | Value                   |
|----------------------|-------------------------|
| Model                | HC-SR04                 |
| Working Voltage      | 5V                      |
| Detection Range      | 2 cm – 400 cm           |
| Accuracy             | ±3 mm                   |
| Trigger Pulse        | 10 μs HIGH              |
| Operating Frequency  | 40 kHz (ultrasound)     |

### Wiring (ESP32 → HC-SR04)

| HC-SR04 Pin | ESP32-C6 Pin | Description        |
|-------------|-------------|---------------------|
| VCC         | 5V          | Power supply        |
| GND         | GND         | Ground              |
| TRIG        | GPIO X      | Trigger signal      |
| ECHO        | GPIO X      | Echo signal         |

> ⚠️ **Note:** The HC-SR04 ECHO pin outputs 5V, but ESP32 GPIO is 3.3V tolerant. Use a **voltage divider** (two resistors) on the ECHO pin to avoid damaging the ESP32.

### Emergency Brake Logic
```
THRESHOLD_CM = 15   // Stop if object is within 15 cm

loop():
    distance = read_ultrasonic()
    
    if distance < THRESHOLD_CM:
        stop_all_motors()       // IMMEDIATE - no Wi-Fi involved
        set_status("EMERGENCY_STOP")
    else:
        // proceed with normal laptop commands
```

### Why NOT Connected to Laptop?

| Factor          | Via Laptop (Bad ❌)              | Direct on ESP32 (Good ✅)       |
|-----------------|----------------------------------|----------------------------------|
| Response Time   | 100ms–500ms+ (Wi-Fi delay)      | < 1ms (direct GPIO)             |
| Reliability     | Depends on Wi-Fi connection      | Always works                     |
| Safety          | Car might crash before stopping  | Instant stop                     |
| Complexity      | Extra network code needed        | Simple local code                |

---

## 📷 Phone Camera

### What Is It? (Simple)
The phone's rear camera acts as the car's "eyes." It sees the road, traffic signs, traffic lights, and obstacles. The video is sent to the laptop for AI processing.

### How It Works
1. Phone runs a camera streaming app
2. App creates a video URL on the local Wi-Fi network
3. Laptop connects to this URL and reads video frames
4. Each frame is sent to the AI model for analysis

### Streaming Options

| App / Method     | Platform | URL Format                              | Free? |
|------------------|----------|-----------------------------------------|-------|
| IP Webcam        | Android  | `http://phone-ip:8080/video`            | ✅     |
| DroidCam         | Android  | `http://phone-ip:4747/video`            | ✅     |
| iVCam            | iOS      | Via USB/Wi-Fi                           | ✅     |
| Custom Web App   | Both     | Custom URL                              | ✅     |

### Camera Requirements
- Resolution: 480p is enough (higher = slower processing)
- Frame Rate: 15–30 FPS is ideal
- Position: Facing forward, mounted on car

### Tips
- Lower resolution = faster AI processing
- Use a phone holder to keep the camera stable
- Make sure phone and laptop are on the **same Wi-Fi network**
- Keep the phone charged (streaming uses battery fast)

---

## 📐 Phone Gyroscope

> ⚡ **OPTIONAL FEATURE** — This is on our list. If we can add it, we will. The car works without it.

### What Is It? (Simple)
The gyroscope inside your phone detects **rotation and tilt**. It can tell if the car is:
- Tilting left or right
- Tilting forward or backward
- Rotating (turning)

### How We Use It
- Detect if the car is turning properly
- Know the car's orientation on the road
- Help with navigation decisions
- Detect if the car has flipped or tilted abnormally

### Technical Details
The gyroscope measures angular velocity around 3 axes:
- **X-axis (Pitch):** Forward/backward tilt
- **Y-axis (Roll):** Left/right tilt
- **Z-axis (Yaw):** Rotation (turning)

### How to Get Gyroscope Data

**Option 1: Using a Sensor App**
- Apps like **SensorServer**, **Phyphox**, or **Sensor Logger**
- They send sensor data over Wi-Fi to the laptop
- Data format: JSON with x, y, z values

**Option 2: Custom Web App (JavaScript)**
```javascript
// In a web page running on the phone
window.addEventListener('deviceorientation', function(event) {
    let alpha = event.alpha;  // Z-axis (0-360)
    let beta = event.beta;    // X-axis (-180 to 180)
    let gamma = event.gamma;  // Y-axis (-90 to 90)
    
    // Send to laptop via WebSocket
    socket.send(JSON.stringify({ alpha, beta, gamma }));
});
```

### Data Example
```json
{
    "gyro": {
        "x": 0.12,
        "y": -0.05,
        "z": 0.03
    },
    "timestamp": 1740650400000
}
```

---

## 🗺️ Phone GPS

> ⚡ **OPTIONAL FEATURE** — This is on our list. If we can add it, we will. The car works without it.

### What Is It? (Simple)
GPS tells us **where the car is** in the real world. It gives latitude and longitude coordinates. We can use this to:
- Track the car's path
- Know current position
- Plan routes (future feature)

### How We Use It
- Track car position in real time
- Log the car's travel path
- Calculate speed (distance over time)
- Future: Waypoint-based navigation

### How to Get GPS Data

**Option 1: Using a Sensor App**
- Same apps as gyroscope (SensorServer, etc.)
- Send GPS coordinates over Wi-Fi

**Option 2: Custom Web App (JavaScript)**
```javascript
navigator.geolocation.watchPosition(function(position) {
    let lat = position.coords.latitude;
    let lng = position.coords.longitude;
    let speed = position.coords.speed;
    let accuracy = position.coords.accuracy;
    
    // Send to laptop via WebSocket
    socket.send(JSON.stringify({ lat, lng, speed, accuracy }));
});
```

### Data Example
```json
{
    "gps": {
        "latitude": 23.0225,
        "longitude": 72.5714,
        "speed": 0.5,
        "accuracy": 3.0
    },
    "timestamp": 1740650400000
}
```

### GPS Limitations
- GPS accuracy is typically 3–10 meters outdoors
- GPS does **NOT work well indoors** — accuracy drops significantly
- For indoor testing, GPS might not be useful
- Consider using the gyroscope + wheel encoder for indoor positioning instead

---

## 📊 Sensor Data Flow Summary

```
┌─────────────────────────────────────────────────────┐
│                    SMARTPHONE                        │
│                                                      │
│  📷 Camera ───── Video Stream ───────→ Laptop  (CORE)     │
│  📐 Gyro   ───── Orientation Data ───→ Laptop  (OPTIONAL) │
│  🗺️ GPS    ───── Position Data ──────→ Laptop  (OPTIONAL) │
│                                                      │
│  All sent over Wi-Fi to Laptop (cloud)               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                 ESP32-C6 (On Car)                     │
│                                                      │
│  📏 Ultrasonic ──→ ESP32 reads directly              │
│                    ↓                                 │
│              Distance < 15cm?                        │
│              YES → EMERGENCY STOP (instant)          │
│              NO  → Continue with laptop commands     │
│                                                      │
│  ❌ NOT sent to laptop — runs locally for safety     │
└─────────────────────────────────────────────────────┘
```

---

## 🔮 Future Sensor Additions

| Sensor          | Purpose                              | Priority  |
|-----------------|--------------------------------------|-----------|
| IR Sensors      | Line following / lane detection      | Medium    |
| Wheel Encoder   | Measure exact distance traveled      | Medium    |
| IMU (MPU6050)   | Better orientation than phone gyro   | Low       |
| LiDAR           | 360° distance mapping                | Future    |
| Second Ultrasonic| Rear obstacle detection             | Low       |

---

← Back to [README](../README.md) | Prev: [← Software](software.md) | Next: [Road Simulation →](road-simulation.md)
