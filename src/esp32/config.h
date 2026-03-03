// config.h — Pin Definitions & Constants for AI Car
// created by: claude + nityam | 2026-03-03
//
// ── HARDWARE ────────────────────────────────────────────────────────────────
//   ESP32-C6 (or ESP8266) + L298N Motor Driver + HC-SR04 Ultrasonic
//   Tank-style 4WD: 2 Left motors (Motor A) + 2 Right motors (Motor B)
//   Each pair wired in parallel to one L298N channel
//
// ── CHANGE THESE ────────────────────────────────────────────────────────────
//   1. Set your Wi-Fi SSID and password
//   2. Verify GPIO pins match your wiring
//   3. Adjust EMERGENCY_DIST_CM for your car's braking distance
// ════════════════════════════════════════════════════════════════════════════

#pragma once

// ─── Wi-Fi Credentials ─────────────────────────────────────────────────────
// Phone, laptop, and ESP32 must all be on the SAME Wi-Fi network
const char* WIFI_SSID = "YOUR_WIFI_SSID";      // ← change this
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";   // ← change this

// ─── Web Server ─────────────────────────────────────────────────────────────
#define SERVER_PORT  80   // HTTP port (laptop sends commands here)

// ─── L298N Motor Driver Pins ────────────────────────────────────────────────
// Tank-style wiring:
//   Motor A = Left pair  (2 DC motors wired in parallel to L298N Channel A)
//   Motor B = Right pair (2 DC motors wired in parallel to L298N Channel B)
//
// For ESP8266 (NodeMCU): use D1-D8 pin labels or raw GPIO numbers
// For ESP32-C6: use GPIO numbers below (change if your board differs)

#define ENA_PIN   4    // Left motors speed  (PWM) — L298N ENA
#define IN1_PIN   6    // Left motors forward       — L298N IN1
#define IN2_PIN   7    // Left motors backward      — L298N IN2

#define ENB_PIN   5    // Right motors speed (PWM) — L298N ENB
#define IN3_PIN  10    // Right motors forward      — L298N IN3
#define IN4_PIN  11    // Right motors backward     — L298N IN4

// ─── HC-SR04 Ultrasonic Sensor ──────────────────────────────────────────────
// ⚠️ ECHO pin outputs 5V — use a voltage divider (2 resistors) to bring it
//    down to 3.3V for ESP32. See docs/hardware.md for wiring details.
#define TRIG_PIN  2    // Trigger (output from ESP32)
#define ECHO_PIN  3    // Echo    (input to ESP32 — through voltage divider!)

// ─── Safety Thresholds ──────────────────────────────────────────────────────
#define EMERGENCY_DIST_CM  15    // emergency stop if obstacle closer than this
#define ECHO_TIMEOUT_US    30000 // pulseIn timeout (30ms ≈ ~5m range)

// ─── Speed Defaults ─────────────────────────────────────────────────────────
// PWM range: 0 (off) to 255 (full speed)
#define DEFAULT_SPEED  180   // normal forward speed
#define SLOW_SPEED     100   // reduced speed (yellow light, obstacle far)
#define MIN_SPEED       60   // below this, motors stall (depends on your motors)

// ─── Timing ─────────────────────────────────────────────────────────────────
#define ULTRASONIC_INTERVAL_MS  50   // read ultrasonic every 50ms (20 Hz)
#define WATCHDOG_TIMEOUT_MS   2000   // stop motors if no command for 2 seconds
