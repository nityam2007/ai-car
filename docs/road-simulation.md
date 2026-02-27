# 🛣️ Road Simulation Documentation – AI Car

<!-- edited by: claude + nityam | 2026-02-27 8:00 PM IST | added edit tracking comment -->

> This document covers how to build the miniature test road, traffic signs, traffic lights, and obstacle setup.

← Back to [README](../README.md)

---

## 🎯 Why a Simulated Road?

We can't test a small AI car on real roads. So we build a **miniature city road** on a table or floor. This gives us:
- ✅ Safe testing environment
- ✅ Controlled conditions for training the AI model
- ✅ Repeatable test scenarios
- ✅ Easy debugging

---

## 📏 Road Layout

### Materials Needed
| Material          | Purpose                        | Quantity        |
|-------------------|--------------------------------|-----------------|
| White chart paper | Road surface                   | 4–6 sheets      |
| Black marker/tape | Lane lines                     | As needed        |
| Cardboard         | Traffic signs, dividers         | As needed        |
| Colored LEDs      | Traffic lights                  | Red, Yellow, Green (1 set) |
| Toy cars/boxes    | Obstacles                       | 2–3 objects      |
| Double-sided tape | Stick things to surface         | As needed        |

### Road Design

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│     ══════════════════════════════════════════             │
│     ║            ROAD (Lane 1)              ║             │
│     ║ - - - - - - - - - - - - - - - - - - - ║  (dashed    │
│     ║            ROAD (Lane 2)              ║   center    │
│     ══════════════════════════════════════════   line)     │
│                                                            │
│     ↑ Start                         Finish ↑              │
│                                                            │
│     [🛑 Stop Sign]    [🚦 Traffic Light]    [30 Speed]     │
│                                                            │
│              [🚗 Obstacle (toy car)]                       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Road Specifications
- **Road width:** 20–30 cm (enough for the car to fit with margins)
- **Lane width:** 10–15 cm per lane
- **Center line:** Dashed line (white or yellow marker/tape)
- **Edge lines:** Solid lines on both sides
- **Total length:** 1–2 meters (or in a loop for continuous testing)

### Road Types to Build
1. **Straight Road** — basic forward driving
2. **Curved Road** — test turning
3. **T-Junction** — test left/right decisions
4. **Intersection with Traffic Light** — test stop/go
5. **Road with Obstacles** — test obstacle detection

---

## 🚦 Traffic Lights

### Simple Version (Manual)
- Use 3 colored LEDs: Red, Yellow, Green
- Mount on a small cardboard pole
- Switch manually during testing
- Power with a button cell or small battery

### Advanced Version (Automated)
- Use an **Arduino Nano** or second **ESP32** to cycle lights automatically
- Timing: Red (5s) → Green (5s) → Yellow (2s) → Red...
- Can be synced or independent of the car system

### Build Instructions
```
Materials:
- Cardboard pole (15–20 cm tall)
- 3 LEDs (Red, Yellow, Green)
- 3 resistors (220Ω each)
- Small breadboard or direct wiring
- Battery (3V coin cell or AA)

Assembly:
1. Cut cardboard into a T-shape (pole + base)
2. Poke 3 holes vertically for LEDs
3. Insert LEDs: Red (top), Yellow (middle), Green (bottom)
4. Wire with resistors to battery
5. Add a small switch to change active LED
```

### What the AI Sees
The camera captures the traffic light, and the AI model must:
- Identify which color is ON
- Red → car stops
- Yellow → car slows down
- Green → car goes

---

## 🛑 Traffic Signs

### Signs to Build

| Sign          | Design                                      | AI Action          |
|---------------|---------------------------------------------|---------------------|
| 🛑 Stop       | Red octagon with "STOP" text               | Car stops completely |
| 🚫 No Entry   | Red circle with white bar                  | Car stops or turns   |
| 30 Speed Limit | White circle, red border, "30" in center  | Car reduces speed    |
| 50 Speed Limit | White circle, red border, "50" in center  | Car adjusts speed    |
| ➡️ Turn Right  | Blue square with right arrow               | Car turns right      |
| ⬅️ Turn Left   | Blue square with left arrow                | Car turns left       |

### How to Make Signs
1. **Print** or **draw** the sign on white cardboard
2. Cut into the correct shape (octagon for stop, circle for speed limit)
3. Make them **5–8 cm tall** (visible to the phone camera)
4. Attach to a small cardboard stand
5. Place along the road at appropriate positions

### Tips for AI Recognition
- Make signs **clear and high-contrast** (bright colors on white background)
- Keep signs **consistent** — same size and style
- Place signs at a **height the camera can see** (match the phone camera height)
- Good lighting is important — avoid shadows on signs
- Take photos of each sign from multiple angles for AI training data

---

## 🚧 Obstacles

### Types of Obstacles
| Obstacle        | What to Use                    | Purpose                    |
|-----------------|--------------------------------|----------------------------|
| Parked car      | Toy car / matchbox car         | Test obstacle detection    |
| Roadblock       | Small cardboard box            | Test emergency stop        |
| Pedestrian      | Small toy figure               | Test object avoidance      |
| Construction    | Orange cone (paper/cardboard)  | Test slow-down behavior    |

### Placement Rules
- Place obstacles **in the car's lane** (not off to the side)
- Keep some distance from the car's starting position
- Test at different distances to calibrate the ultrasonic sensor threshold

---

## 📸 Collecting Training Data

The simulated road is also used to **collect training data** for the AI model.

### How to Collect Data
1. Place signs, lights, and obstacles on the road
2. Mount the phone on the car (or hold it at car-camera height)
3. Take photos/video of each scenario
4. Label each image:
   - "stop_sign"
   - "red_light"
   - "speed_30"
   - "obstacle"
   - "clear_road"
5. Use these labeled images to train the AI model

### Tips for Good Training Data
- Take images from **different angles** (slight left, center, slight right)
- Take images in **different lighting** (bright, dim, shadow)
- Take images at **different distances** (far, medium, close)
- Include images of **empty road** (no sign) as "clear_road"
- The more variety, the better the AI model will be

---

## 🧪 Test Scenarios

| #  | Scenario                        | Expected Behavior                    |
|----|---------------------------------|--------------------------------------|
| 1  | Straight road, no obstacles     | Car drives straight                  |
| 2  | Stop sign ahead                 | Car stops at the sign                |
| 3  | Red traffic light               | Car stops and waits                  |
| 4  | Green traffic light             | Car continues driving                |
| 5  | Yellow traffic light            | Car slows down                       |
| 6  | Speed limit 30 sign             | Car reduces speed                    |
| 7  | Obstacle in lane                | Camera detects → car stops/avoids    |
| 8  | Close obstacle (ultrasonic)     | Emergency brake (ESP32 local)        |
| 9  | Curved road                     | Car follows the curve                |
| 10 | Multiple signs in sequence      | Car reacts to each correctly         |

---

## 📐 Road Layout Template

Here's a suggested layout for your test area (approximately 120cm × 80cm):

```
START ─────────────────────────────────────────── END
  │                                               │
  │    [30]  ←Speed Sign                          │
  │     │                                         │
  ├─────┼─────────── Straight Section ────────────┤
  │     │                                         │
  │    [🚦] ←Traffic Light                        │
  │     │                                         │
  ├─────┼─────────── Intersection ────────────────┤
  │     │                                         │
  │    [🛑] ←Stop Sign                            │
  │     │                                         │
  ├─────┼─────────── Straight Section ────────────┤
  │     │                                         │
  │   [🚗] ←Obstacle                              │
  │     │                                         │
  └─────┴─────────────────────────────────────────┘
```

---

← Back to [README](../README.md) | Prev: [← Sensors](sensors.md) | Next: [Modules →](modules.md)
