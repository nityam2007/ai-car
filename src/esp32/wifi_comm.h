// wifi_comm.h — Wi-Fi + HTTP Web Server for AI Car
// created by: claude + nityam | 2026-03-03
//
// Runs a web server on the ESP32/ESP8266 that receives driving commands
// from the laptop over HTTP.
//
// ── ENDPOINTS ───────────────────────────────────────────────────────────────
//   GET  /           → welcome page (plain text)
//   GET  /status     → JSON: distance, speed, state, emergency flag
//   GET  /drive?left=N&right=N  → tank drive (N = -255 to 255)
//   GET  /go         → forward at default speed
//   GET  /stop       → stop all motors
//   GET  /slow       → forward at slow speed
//   GET  /reverse    → backward at default speed
//   GET  /left       → pivot turn left
//   GET  /right      → pivot turn right
//   POST /command    → JSON body: {"cmd":"GO"} or {"cmd":"DRIVE","left":N,"right":N}
//
// The laptop's video_stream.py sends GET /drive?left=L&right=R each frame.
// Simple commands (/go, /stop, etc.) are for manual testing from a browser.
// ════════════════════════════════════════════════════════════════════════════

#pragma once
#include "config.h"

// ── Platform-specific includes ──────────────────────────────────────────────
#if defined(ESP32)
    #include <WiFi.h>
    #include <WebServer.h>
    WebServer server(SERVER_PORT);
#elif defined(ESP8266)
    #include <ESP8266WiFi.h>
    #include <ESP8266WebServer.h>
    ESP8266WebServer server(SERVER_PORT);
#endif

// ── State ───────────────────────────────────────────────────────────────────
String current_state   = "IDLE";
unsigned long last_cmd_time = 0;   // millis() of last command received
int cmd_speed = DEFAULT_SPEED;     // speed set by commands

// forward declarations (defined in motor_control.h)
extern int motor_left_speed;
extern int motor_right_speed;
extern float last_distance_cm;
extern void tank_drive(int left, int right);
extern void stop_motors();
extern void go_forward(int speed);
extern void go_backward(int speed);
extern void turn_left(int speed);
extern void turn_right(int speed);
extern void spin_left(int speed);
extern void spin_right(int speed);
extern bool is_emergency();

// ─── CORS header (allows browser/fetch requests from any origin) ────────────
void send_cors() {
    server.sendHeader("Access-Control-Allow-Origin", "*");
}

// ─── Wi-Fi Connection ───────────────────────────────────────────────────────
void setup_wifi() {
    Serial.print("\n  Connecting to Wi-Fi: ");
    Serial.println(WIFI_SSID);

    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        attempts++;
        if (attempts > 40) {   // 20 seconds
            Serial.println("\n  ❌ Wi-Fi failed! Check SSID/password in config.h");
            Serial.println("  Restarting in 5 seconds...");
            delay(5000);
            ESP.restart();
        }
    }

    Serial.println();
    Serial.println("  ✅ Wi-Fi connected!");
    Serial.print("  IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("  Open in browser: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/status");
}

// ─── Route Handlers ─────────────────────────────────────────────────────────

void handle_root() {
    send_cors();
    String msg = "AI Car ESP32 Controller\n";
    msg += "=======================\n";
    msg += "Endpoints:\n";
    msg += "  GET  /status           - car status (JSON)\n";
    msg += "  GET  /drive?left=N&right=N  - tank drive\n";
    msg += "  GET  /go               - forward\n";
    msg += "  GET  /stop             - stop\n";
    msg += "  GET  /slow             - slow forward\n";
    msg += "  GET  /reverse          - backward\n";
    msg += "  GET  /left             - turn left\n";
    msg += "  GET  /right            - turn right\n";
    msg += "  POST /command          - JSON command\n";
    server.send(200, "text/plain", msg);
}

void handle_status() {
    send_cors();
    String json = "{";
    json += "\"state\":\"" + current_state + "\",";
    json += "\"distance_cm\":" + String(last_distance_cm, 1) + ",";
    json += "\"emergency\":" + String(is_emergency() ? "true" : "false") + ",";
    json += "\"left_speed\":" + String(motor_left_speed) + ",";
    json += "\"right_speed\":" + String(motor_right_speed) + ",";
    json += "\"cmd_speed\":" + String(cmd_speed) + ",";
    json += "\"uptime_ms\":" + String(millis());
    json += "}";
    server.send(200, "application/json", json);
}

void handle_drive() {
    send_cors();
    if (!server.hasArg("left") || !server.hasArg("right")) {
        server.send(400, "text/plain", "Need ?left=N&right=N (-255 to 255)");
        return;
    }
    int left  = server.arg("left").toInt();
    int right = server.arg("right").toInt();

    last_cmd_time = millis();

    if (is_emergency()) {
        stop_motors();
        current_state = "EMERGENCY_STOP";
        server.send(200, "application/json", "{\"ok\":false,\"reason\":\"emergency\"}");
        return;
    }

    tank_drive(left, right);
    current_state = "DRIVE";
    server.send(200, "application/json", "{\"ok\":true}");
}

void handle_go() {
    send_cors();
    last_cmd_time = millis();
    if (is_emergency()) { stop_motors(); current_state = "EMERGENCY_STOP"; }
    else { go_forward(cmd_speed); current_state = "FORWARD"; }
    server.send(200, "application/json", "{\"ok\":true,\"state\":\"" + current_state + "\"}");
}

void handle_stop() {
    send_cors();
    last_cmd_time = millis();
    stop_motors();
    current_state = "STOPPED";
    server.send(200, "application/json", "{\"ok\":true,\"state\":\"STOPPED\"}");
}

void handle_slow() {
    send_cors();
    last_cmd_time = millis();
    if (is_emergency()) { stop_motors(); current_state = "EMERGENCY_STOP"; }
    else { go_forward(SLOW_SPEED); current_state = "SLOW"; }
    server.send(200, "application/json", "{\"ok\":true,\"state\":\"" + current_state + "\"}");
}

void handle_reverse() {
    send_cors();
    last_cmd_time = millis();
    if (is_emergency()) { stop_motors(); current_state = "EMERGENCY_STOP"; }
    else { go_backward(cmd_speed); current_state = "REVERSE"; }
    server.send(200, "application/json", "{\"ok\":true,\"state\":\"" + current_state + "\"}");
}

void handle_left() {
    send_cors();
    last_cmd_time = millis();
    if (is_emergency()) { stop_motors(); current_state = "EMERGENCY_STOP"; }
    else { turn_left(cmd_speed); current_state = "TURN_LEFT"; }
    server.send(200, "application/json", "{\"ok\":true,\"state\":\"" + current_state + "\"}");
}

void handle_right() {
    send_cors();
    last_cmd_time = millis();
    if (is_emergency()) { stop_motors(); current_state = "EMERGENCY_STOP"; }
    else { turn_right(cmd_speed); current_state = "TURN_RIGHT"; }
    server.send(200, "application/json", "{\"ok\":true,\"state\":\"" + current_state + "\"}");
}

void handle_command() {
    send_cors();
    last_cmd_time = millis();

    String body = server.arg("plain");
    body.toUpperCase();

    if (is_emergency() && body.indexOf("STOP") == -1) {
        stop_motors();
        current_state = "EMERGENCY_STOP";
        server.send(200, "application/json", "{\"ok\":false,\"reason\":\"emergency\"}");
        return;
    }

    // parse JSON-ish command — keep it simple, no JSON library needed
    if (body.indexOf("DRIVE") >= 0) {
        // expect {"cmd":"DRIVE","left":N,"right":N}
        int li = body.indexOf("LEFT");
        int ri = body.indexOf("RIGHT");
        if (li >= 0 && ri >= 0) {
            // extract numbers after "left": and "right":
            int left  = extract_number(body, li);
            int right = extract_number(body, ri);
            tank_drive(left, right);
            current_state = "DRIVE";
        }
    } else if (body.indexOf("GO") >= 0 || body.indexOf("FORWARD") >= 0) {
        go_forward(cmd_speed);
        current_state = "FORWARD";
    } else if (body.indexOf("E_STOP") >= 0) {
        stop_motors();
        current_state = "E_STOP";
    } else if (body.indexOf("STOP") >= 0) {
        stop_motors();
        current_state = "STOPPED";
    } else if (body.indexOf("SLOW") >= 0) {
        go_forward(SLOW_SPEED);
        current_state = "SLOW";
    } else if (body.indexOf("SPEED_30") >= 0) {
        cmd_speed = 76;   // 30% of 255
        go_forward(cmd_speed);
        current_state = "SPEED_30";
    } else if (body.indexOf("SPEED_50") >= 0) {
        cmd_speed = 127;  // 50% of 255
        go_forward(cmd_speed);
        current_state = "SPEED_50";
    } else if (body.indexOf("SPEED_100") >= 0) {
        cmd_speed = 255;
        go_forward(cmd_speed);
        current_state = "SPEED_100";
    } else if (body.indexOf("LEFT") >= 0) {
        turn_left(cmd_speed);
        current_state = "TURN_LEFT";
    } else if (body.indexOf("RIGHT") >= 0) {
        turn_right(cmd_speed);
        current_state = "TURN_RIGHT";
    } else if (body.indexOf("REVERSE") >= 0) {
        go_backward(cmd_speed);
        current_state = "REVERSE";
    } else {
        server.send(400, "text/plain", "Unknown command");
        return;
    }

    server.send(200, "application/json", "{\"ok\":true,\"state\":\"" + current_state + "\"}");
}

// helper: extract first integer after a keyword position in a string
int extract_number(String &s, int start_pos) {
    int i = start_pos;
    // skip to first digit or minus sign
    while (i < (int)s.length() && s[i] != '-' && (s[i] < '0' || s[i] > '9')) i++;
    if (i >= (int)s.length()) return 0;
    int end = i + 1;
    while (end < (int)s.length() && (s[end] >= '0' && s[end] <= '9')) end++;
    return s.substring(i, end).toInt();
}

void handle_not_found() {
    send_cors();
    server.send(404, "text/plain", "Not found. Try /status or /drive?left=100&right=100");
}

// ─── Register all routes ────────────────────────────────────────────────────
void setup_server() {
    server.on("/",        HTTP_GET,  handle_root);
    server.on("/status",  HTTP_GET,  handle_status);
    server.on("/drive",   HTTP_GET,  handle_drive);
    server.on("/go",      HTTP_GET,  handle_go);
    server.on("/stop",    HTTP_GET,  handle_stop);
    server.on("/slow",    HTTP_GET,  handle_slow);
    server.on("/reverse", HTTP_GET,  handle_reverse);
    server.on("/left",    HTTP_GET,  handle_left);
    server.on("/right",   HTTP_GET,  handle_right);
    server.on("/command", HTTP_POST, handle_command);
    server.onNotFound(handle_not_found);

    server.begin();
    Serial.println("  ✅ Web server started on port " + String(SERVER_PORT));
    Serial.println();
}

// ─── Watchdog: stop motors if no commands for a while ────────────────────────
// Call this from loop(). If the laptop crashes or disconnects, the car stops.
void check_watchdog() {
    if (last_cmd_time > 0 && current_state != "STOPPED" && current_state != "IDLE") {
        unsigned long elapsed = millis() - last_cmd_time;
        if (elapsed > WATCHDOG_TIMEOUT_MS) {
            stop_motors();
            current_state = "WATCHDOG_STOP";
            Serial.println("  ⚠️ Watchdog: no command for 2s — motors stopped");
            last_cmd_time = 0;  // reset so we don't spam
        }
    }
}
