# DO NOT EDIT : AI. : UPDATED ON : 2026-02-27 7:30PM +5:30/IST


# 🚗 AI Car – Vision-Based Autonomous Driving System

An AI-powered miniature autonomous car system that uses a **smartphone as a camera**, a **laptop for AI model processing**, and an **ESA-based controller** to execute driving instructions in real time.

This project demonstrates computer vision, traffic sign recognition, obstacle detection, and decision-based vehicle control in a simulated road environment.

---

## 📌 Project Architecture

```
Smartphone Camera
        ↓ (Live Video Stream)
Laptop (AI Model + OpenCV Processing)
        ↓ (Control Instructions)
ESA Controller
        ↓
Motor Driver → Car Movement
```

---

## 🧠 Core Idea

Instead of running the AI model on embedded hardware (like Raspberry Pi), we:

- Use a **smartphone** for video capture
- Stream live video to a **laptop**
- Run AI model + OpenCV processing on the laptop
- Send control commands to the **ESA controller**
- Controller drives motors accordingly

This allows us to:
- Run heavier AI models
- Debug easily
- Improve model accuracy without hardware limitations

---

## 🎯 Features

- 🚦 Traffic Light Detection (Red / Yellow / Green)
- 🛑 Stop Sign Recognition
- 🚗 Speed Limit Sign Detection
- 🚧 Obstacle Detection (Cars / Objects)
- 🛣️ Basic Lane Detection (Optional – sensor-based or vision-based)
- 🔄 Manual & Autonomous Mode (if implemented)

---

## 🏗️ Tech Stack

### 💻 Software
- Python
- OpenCV
- Machine Learning Model (Custom / Pretrained)
- Socket / HTTP / Serial Communication (for controller instructions)

### 📱 Hardware
- ESA Controller : ESP32 C6 
- DC Motors + Motor Driver : L298N/D
- Smartphone (Camera + Streaming) : APP/WEB
- Laptop (AI Processing)
- Power Supply / Battery Pack : 18650 Li-ion Batteries

---

## 🛣️ Simulation Environment

We are building a small simulated city road using:

- Chart paper (road layout)
- Cardboard (traffic signs)
- Handmade traffic lights
- Mini obstacle objects (toy cars / boxes)

This controlled environment allows:
- Safe testing
- Model training
- Real-time debugging

---

## 🔄 System Workflow

1. Smartphone captures live video.
2. Video stream is sent to laptop.
3. AI model processes each frame.
4. OpenCV extracts relevant features.
5. Model predicts:
   - Stop
   - Slow Down
   - Speed Limit
   - Turn Left/Right
6. Laptop sends command to ESA controller.
7. Controller drives motors accordingly.

---

## 🧪 Future Improvements

- Real-time lane detection using computer vision
- Sensor-based lane assist
- Better object detection model (YOLO-based)
- On-device edge AI (Raspberry Pi upgrade)
- Mobile app controller for manual override

---

## 👥 Team

Developed as a college project by a team of 11 members.

---

## 🚀 Goal

To demonstrate a working prototype of a vision-based autonomous vehicle system capable of recognizing traffic rules and reacting intelligently in real time.
