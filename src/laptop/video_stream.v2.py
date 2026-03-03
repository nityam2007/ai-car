# video_stream.py — Phone Camera Stream Receiver
# created by: claude + nityam | 2026-02-27 8:15 PM IST
# edited by: claude + nityam | 2026-02-28 — added FPS counter + latency display for testing
# edited by: claude + nityam | 2026-02-28 — fixed MJPEG: manual byte-stream parser (works where cv2.VideoCapture fails)
# edited by: claude + nityam | 2026-02-28 — fixed 401 auth: app needs username/password (Basic Auth)
#
# Captures live MJPEG video stream from phone running "IP Webcam" app.
# App: https://play.google.com/store/apps/details?id=com.shenyaocn.android.WebCam
#
# NOTE: cv2.VideoCapture can fail on raw MJPEG streams even though VLC plays them fine.
#       This script reads the MJPEG byte stream directly and decodes each JPEG frame manually.
#
# HOW TO USE:
#   1. Install "IP Webcam" app on your phone (link above)
#   2. Open the app → tap "Start Server"
#   3. Note the IP address shown on screen (e.g. 192.168.1.50)
#   4. Make sure phone and laptop are on the SAME Wi-Fi network
#   5. Change PHONE_IP below to your phone's IP
#   6. Run: python video_stream.py
#   7. Press 'q' to quit

import os
os.environ["QT_QPA_FONTDIR"] = "/usr/share/fonts"  # suppress Qt font warnings
os.environ["OPENCV_GUI_BACKEND"] = "GTK"            # use GTK instead of Qt (more reliable on Linux)

import cv2
import time
import urllib.request
import numpy as np

# ── CONFIG ──────────────────────────────────────────
PHONE_IP = "192.168.16.198"       # Change this to your phone's IP
PORT = "8081"                     # Default port for IP Webcam app
USERNAME = ""                     # App username (leave "" if no auth)
PASSWORD = ""                     # App password (leave "" if no auth)
STREAM_PATH = "/video"            # Stream endpoint
WINDOW_NAME = "AI Car — Phone Stream"
SHOW_STATS = True                 # Show FPS + latency on screen (True/False)
# ────────────────────────────────────────────────────

# Build URL with or without auth
if USERNAME and PASSWORD:
    STREAM_URL = f"http://{USERNAME}:{PASSWORD}@{PHONE_IP}:{PORT}{STREAM_PATH}"
else:
    STREAM_URL = f"http://{PHONE_IP}:{PORT}{STREAM_PATH}"

STREAM_URL_DISPLAY = f"http://{PHONE_IP}:{PORT}{STREAM_PATH}"  # for printing (no password)

def try_opencv(url):
    """Try normal OpenCV capture first (works for some streams)."""
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            return cap
    cap.release()
    return None

def run_mjpeg_manual(url):
    """Read raw MJPEG byte stream and decode frames manually.
    This works when cv2.VideoCapture fails but VLC plays fine."""
    print(f"Connecting to MJPEG stream: {STREAM_URL_DISPLAY}")
    print("Make sure your phone and laptop are on the same Wi-Fi.\n")

    try:
        stream = urllib.request.urlopen(url, timeout=5)
    except Exception as e:
        print(f"❌ Error: Could not open stream. ({e})")
        print("   → Check if the app is running on your phone")
        print(f"   → Check if {PHONE_IP}:{PORT} is correct (see app screen)")
        print("   → Check if both devices are on the same Wi-Fi")
        print("   → Check USERNAME and PASSWORD in config (app may need auth)")
        return

    print("✅ Stream connected (MJPEG manual mode)! Press 'q' to quit.\n")

    buf = b''
    fps = 0
    frame_count = 0
    fps_timer = time.time()

    while True:
        t_start = time.time()

        # Read chunks and find JPEG start (FF D8) and end (FF D9) markers
        buf += stream.read(4096)
        start = buf.find(b'\xff\xd8')
        end = buf.find(b'\xff\xd9')

        if start != -1 and end != -1 and end > start:
            jpg = buf[start:end + 2]
            buf = buf[end + 2:]

            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            if frame is None:
                continue

            latency_ms = (time.time() - t_start) * 1000

            frame_count += 1
            elapsed = time.time() - fps_timer
            if elapsed >= 0.5:
                fps = frame_count / elapsed
                frame_count = 0
                fps_timer = time.time()

            if SHOW_STATS:
                stats_text = f"FPS: {fps:.1f}  |  Latency: {latency_ms:.0f}ms"
                cv2.rectangle(frame, (0, 0), (380, 32), (0, 0, 0), -1)
                cv2.putText(frame, stats_text, (10, 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()
    print("Stream closed.")

def run_opencv(cap):
    """Run with normal OpenCV VideoCapture."""
    print("✅ Stream connected (OpenCV mode)! Press 'q' to quit.\n")

    fps = 0
    frame_count = 0
    fps_timer = time.time()
    total_frames = 0

    fail_count = 0
    saved_debug_frame = False
    while True:
        t_start = time.time()
        ret, frame = cap.read()
        if not ret or frame is None:
            print(f"⚠️  Failed to grab frame #{total_frames + 1} (ret={ret}, frame={type(frame)}). Retrying...")
            fail_count += 1
            time.sleep(0.1)
            if fail_count >= 10:
                print("❌ Too many frame grab failures. Switching to manual MJPEG mode.")
                cap.release()
                cv2.destroyAllWindows()
                return 'switch_to_manual'
            continue
        if frame.size == 0:
            print(f"⚠️  Frame #{total_frames + 1} is empty (size=0). Skipping...")
            continue
        fail_count = 0
        total_frames += 1
        h, w = frame.shape[:2]
        print(f"  Frame #{total_frames}: {w}x{h} (type={type(frame)}, dtype={frame.dtype}, min={frame.min()}, max={frame.max()})")
        if not saved_debug_frame:
            cv2.imwrite("debug_frame.jpg", frame)
            print("  Saved first valid frame as debug_frame.jpg")
            saved_debug_frame = True
        latency_ms = (time.time() - t_start) * 1000
        frame_count += 1
        elapsed = time.time() - fps_timer
        if elapsed >= 0.5:
            fps = frame_count / elapsed
            frame_count = 0
            fps_timer = time.time()
        if SHOW_STATS:
            stats_text = f"FPS: {fps:.1f}  |  Latency: {latency_ms:.0f}ms"
            cv2.rectangle(frame, (0, 0), (380, 32), (0, 0, 0), -1)
            cv2.putText(frame, stats_text, (10, 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow(WINDOW_NAME, frame)
        cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    print("Stream closed.")

def main():
    print(f"Stream URL: {STREAM_URL_DISPLAY}")
    if USERNAME:
        print(f"Auth: using credentials (user: {USERNAME})")
    else:
        print("Auth: none (set USERNAME & PASSWORD in config if app needs login)")
    print()

    # edited by nityam, 2026-02-28: Only use HTTP for MJPEG, retry OpenCV once, note on ADB
    # NOTE: ADB over WiFi is not recommended for real-time video streaming. Use HTTP MJPEG for best performance. ADB is for device control/debugging, not live video.
    # Try OpenCV first, fall back to manual MJPEG parser
    if not STREAM_URL.startswith("http://") and not STREAM_URL.startswith("https://"):
        print(f"ERROR: Stream URL must be HTTP/HTTPS, got: {STREAM_URL}")
        return
    print("Trying OpenCV capture (HTTP MJPEG)...")
    cap = try_opencv(STREAM_URL)
    if not cap:
        print("OpenCV capture failed, retrying once...")
        cap = try_opencv(STREAM_URL)
    if cap:
        result = run_opencv(cap)
        if result == 'switch_to_manual':
            print("Switching to manual MJPEG mode after repeated OpenCV failures.\n")
            run_mjpeg_manual(STREAM_URL)
    else:
        print("OpenCV capture failed again — switching to manual MJPEG mode.\n")
        run_mjpeg_manual(STREAM_URL)

if __name__ == "__main__":
    main()
