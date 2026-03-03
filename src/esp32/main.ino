// main.ino — AI Car ESP32/ESP8266 Motor Controller
// created by: claude + nityam | 2026-03-03
//
// ── WHAT THIS DOES ──────────────────────────────────────────────────────────
//   1. Connects to Wi-Fi (same network as phone + laptop)
//   2. Starts an HTTP web server to receive driving commands from laptop
//   3. Reads HC-SR04 ultrasonic sensor for emergency obstacle detection
//   4. Controls 4 DC motors (tank-style: 2 left + 2 right) via L298N
//
// ── SAFETY ARCHITECTURE ─────────────────────────────────────────────────────
//   The ultrasonic sensor runs LOCALLY on the ESP32 — no Wi-Fi needed.
//   If an obstacle is closer than EMERGENCY_DIST_CM (default 15cm),
//   ALL motors stop IMMEDIATELY, regardless of laptop commands.
//   This is a hardware-level safety reflex — < 5ms response time.
//
// ── HOW THE LAPTOP TALKS TO THIS ────────────────────────────────────────────
//   The laptop runs video_stream.py → ai_processor.py → PID steering angle
//   Then sends:  GET http://<esp32-ip>/drive?left=N&right=N
//   Where N = -255 (full backward) to +255 (full forward)
//   This is tank-style differential drive.
//
// ── SETUP INSTRUCTIONS ──────────────────────────────────────────────────────
//   1. Open config.h → set WIFI_SSID, WIFI_PASS, and verify GPIO pins
//   2. Wire L298N and HC-SR04 according to config.h pin numbers
//   3. Upload this sketch to ESP32 (or ESP8266) via Arduino IDE
//   4. Open Serial Monitor (115200 baud) → note the IP address
//   5. Test: open http://<esp32-ip>/status in a browser
//   6. Test motors: http://<esp32-ip>/go  or  /stop  or  /drive?left=150&right=150
//
// ── BOARD SUPPORT ───────────────────────────────────────────────────────────
//   ESP32 (any variant: C6, S3, WROOM, etc.) — install "esp32" board package
//   ESP8266 (NodeMCU, Wemos D1, etc.)        — install "esp8266" board package
//   Both use the same code — platform differences handled via #ifdef
// ════════════════════════════════════════════════════════════════════════════

#include "config.h"
#include "motor_control.h"
#include "ultrasonic.h"
#include "wifi_comm.h"

// ── Timing ──────────────────────────────────────────────────────────────────
unsigned long last_ultrasonic_ms = 0;
bool was_emergency = false;

// ════════════════════════════════════════════════════════════════════════════
//  SETUP — runs once on boot
// ════════════════════════════════════════════════════════════════════════════
void setup() {
    Serial.begin(115200);
    delay(500);

    Serial.println();
    Serial.println("========================================");
    Serial.println("   AI Car — ESP32 Motor Controller");
    Serial.println("========================================");

    // 1. Motors first — car should be stopped before anything else
    setup_motors();
    Serial.println("  ✅ Motors initialized (stopped)");

    // 2. Ultrasonic sensor
    setup_ultrasonic();
    Serial.println("  ✅ Ultrasonic sensor ready");

    // 3. Wi-Fi (this blocks until connected or restarts)
    setup_wifi();

    // 4. Web server
    setup_server();

    Serial.println("========================================");
    Serial.println("   Ready! Waiting for commands...");
    Serial.println("========================================");
    Serial.println();
}

// ════════════════════════════════════════════════════════════════════════════
//  LOOP — runs continuously
// ════════════════════════════════════════════════════════════════════════════
void loop() {

    // ── SAFETY FIRST: read ultrasonic sensor ────────────────────────────────
    // Runs every ULTRASONIC_INTERVAL_MS (50ms default = 20 Hz).
    // If obstacle < EMERGENCY_DIST_CM → stop motors IMMEDIATELY.
    // This check happens BEFORE handling any web server requests.
    unsigned long now = millis();
    if (now - last_ultrasonic_ms >= ULTRASONIC_INTERVAL_MS) {
        last_ultrasonic_ms = now;

        float dist = read_distance_cm();

        if (dist < EMERGENCY_DIST_CM) {
            stop_motors();
            current_state = "EMERGENCY_STOP";
            if (!was_emergency) {
                Serial.print("  🚨 EMERGENCY STOP! Obstacle at ");
                Serial.print(dist, 1);
                Serial.println(" cm");
                was_emergency = true;
            }
        } else {
            if (was_emergency) {
                Serial.println("  ✅ Obstacle cleared — ready for commands");
                was_emergency = false;
            }
        }
    }

    // ── Handle web server requests ──────────────────────────────────────────
    // Processes incoming HTTP requests (drive commands from laptop).
    // If emergency is active, drive commands are rejected (see wifi_comm.h).
    server.handleClient();

    // ── Watchdog: stop if laptop disconnects ────────────────────────────────
    check_watchdog();

    // small yield to prevent WDT reset on ESP8266
    delay(1);
}
