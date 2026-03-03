// motor_control.h — L298N Tank-Drive Motor Control for AI Car
// created by: claude + nityam | 2026-03-03
//
// Tank-style 4WD:
//   Left pair  (2 DC motors wired in parallel) → L298N Channel A (IN1, IN2, ENA)
//   Right pair (2 DC motors wired in parallel) → L298N Channel B (IN3, IN4, ENB)
//
// Speed range: -255 to +255  (negative = backward)
// All public functions use this same range.
// ════════════════════════════════════════════════════════════════════════════

#pragma once
#include "config.h"

// ─── Current state (readable from wifi_comm.h) ──────────────────────────────
int motor_left_speed  = 0;   // -255..+255
int motor_right_speed = 0;   // -255..+255

// ─── Setup ──────────────────────────────────────────────────────────────────
void setup_motors() {
    pinMode(IN1_PIN, OUTPUT);
    pinMode(IN2_PIN, OUTPUT);
    pinMode(IN3_PIN, OUTPUT);
    pinMode(IN4_PIN, OUTPUT);
    pinMode(ENA_PIN, OUTPUT);
    pinMode(ENB_PIN, OUTPUT);

    // ESP8266: set analogWrite range to 0-255 (default is 0-1023)
    #if defined(ESP8266)
        analogWriteRange(255);
    #endif

    // all off
    digitalWrite(IN1_PIN, LOW);
    digitalWrite(IN2_PIN, LOW);
    digitalWrite(IN3_PIN, LOW);
    digitalWrite(IN4_PIN, LOW);
    analogWrite(ENA_PIN, 0);
    analogWrite(ENB_PIN, 0);
}

// ─── Core: Tank Drive ───────────────────────────────────────────────────────
// Set left and right motor speeds independently.
//   speed > 0 → forward,  speed < 0 → backward,  speed = 0 → stop
//   range: -255 to +255
void tank_drive(int left, int right) {
    motor_left_speed  = constrain(left,  -255, 255);
    motor_right_speed = constrain(right, -255, 255);

    // ── Left motors (Channel A) ──
    if (motor_left_speed > 0) {
        digitalWrite(IN1_PIN, HIGH);
        digitalWrite(IN2_PIN, LOW);
    } else if (motor_left_speed < 0) {
        digitalWrite(IN1_PIN, LOW);
        digitalWrite(IN2_PIN, HIGH);
    } else {
        digitalWrite(IN1_PIN, LOW);
        digitalWrite(IN2_PIN, LOW);
    }
    analogWrite(ENA_PIN, abs(motor_left_speed));

    // ── Right motors (Channel B) ──
    if (motor_right_speed > 0) {
        digitalWrite(IN3_PIN, HIGH);
        digitalWrite(IN4_PIN, LOW);
    } else if (motor_right_speed < 0) {
        digitalWrite(IN3_PIN, LOW);
        digitalWrite(IN4_PIN, HIGH);
    } else {
        digitalWrite(IN3_PIN, LOW);
        digitalWrite(IN4_PIN, LOW);
    }
    analogWrite(ENB_PIN, abs(motor_right_speed));
}

// ─── Convenience Functions ──────────────────────────────────────────────────

void stop_motors() {
    tank_drive(0, 0);
}

void go_forward(int speed) {
    speed = abs(speed);
    tank_drive(speed, speed);
}

void go_backward(int speed) {
    speed = abs(speed);
    tank_drive(-speed, -speed);
}

// Pivot turns: one side stops, other side drives
void turn_left(int speed) {
    speed = abs(speed);
    tank_drive(0, speed);
}

void turn_right(int speed) {
    speed = abs(speed);
    tank_drive(speed, 0);
}

// Spin-in-place: both sides drive in opposite directions
void spin_left(int speed) {
    speed = abs(speed);
    tank_drive(-speed, speed);
}

void spin_right(int speed) {
    speed = abs(speed);
    tank_drive(speed, -speed);
}
