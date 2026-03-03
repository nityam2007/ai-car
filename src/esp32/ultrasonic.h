// ultrasonic.h — HC-SR04 Ultrasonic Distance Sensor for AI Car
// created by: claude + nityam | 2026-03-03
//
// Wiring:  TRIG → ESP32 GPIO (output)
//          ECHO → voltage divider → ESP32 GPIO (input, 3.3V safe)
//          VCC  → 5V,  GND → GND
//
// ⚠️ The ECHO pin outputs 5V pulses. ESP32 GPIO is 3.3V!
//    Use a voltage divider: ECHO → 1kΩ → ESP32_PIN → 2kΩ → GND
//    This gives ~3.3V on the ESP32 pin. Without this you may damage the chip.
// ════════════════════════════════════════════════════════════════════════════

#pragma once
#include "config.h"

// ─── Last reading (readable from other files) ───────────────────────────────
float last_distance_cm = 999.0;

// ─── Setup ──────────────────────────────────────────────────────────────────
void setup_ultrasonic() {
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    digitalWrite(TRIG_PIN, LOW);
}

// ─── Read distance ──────────────────────────────────────────────────────────
// Returns distance in cm. Returns 999.0 if no echo (no obstacle in range).
// Non-blocking if called at reasonable intervals (every 50ms+).
//
// How it works:
//   1. Send a 10μs HIGH pulse on TRIG
//   2. Sensor sends 8 ultrasonic pulses at 40 kHz
//   3. Sound travels to obstacle and bounces back
//   4. ECHO pin goes HIGH for the duration of the round-trip
//   5. Distance = (time × speed_of_sound) / 2
//      speed_of_sound ≈ 343 m/s = 0.0343 cm/μs
float read_distance_cm() {
    // send trigger pulse
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // measure echo duration (microseconds)
    // timeout prevents blocking if no object in range
    long duration = pulseIn(ECHO_PIN, HIGH, ECHO_TIMEOUT_US);

    if (duration == 0) {
        last_distance_cm = 999.0;   // no echo → nothing in range
        return last_distance_cm;
    }

    // convert to cm
    last_distance_cm = (duration * 0.0343) / 2.0;
    return last_distance_cm;
}

// ─── Check if obstacle is dangerously close ─────────────────────────────────
bool is_emergency() {
    return (last_distance_cm < EMERGENCY_DIST_CM);
}
