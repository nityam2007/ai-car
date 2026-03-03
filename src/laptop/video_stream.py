# video_stream.py — Low-Latency Phone Camera Stream Receiver + ESP32 Commander
# created by: claude + nityam | 2026-02-27 8:15 PM IST
# edited by: claude + nityam | 2026-02-28 — FPS/latency overlay, auth, manual MJPEG parser
# edited by: claude + nityam | 2026-03-03 — full rewrite: kornia-rs (Rust) + threaded pipeline
# edited by: claude + nityam | 2026-03-03 — added ESP32 motor command sending (tank drive)
#
# ── ARCHITECTURE (for minimum latency) ──────────────────────────────────────
#   Reader Thread ──► Queue(maxsize=2, drops stale) ──► Main Thread (display+AI)
#
# ── KORNIA-RS (Rust-backed, 2-5x faster than OpenCV for JPEG I/O) ───────────
#   K.decode_image_jpeg(bytes)       → numpy(H,W,3) RGB uint8
#   K.bgr_from_rgb(img)              → numpy(H,W,3) BGR (for cv2.imshow)
#   K.gray_from_rgb(img)             → numpy(H,W,1) grayscale
#   K.resize(img, (H,W), 'bilinear') → fast Rust resize
#
# ── STREAM SOURCE ───────────────────────────────────────────────────────────
#   IP Webcam app (Android) — MJPEG over HTTP
#   App: https://play.google.com/store/apps/details?id=com.shenyaocn.android.WebCam
#
# ── HOW TO USE ──────────────────────────────────────────────────────────────
#   1. Install IP Webcam app on phone → tap "Start Server"
#   2. Set PHONE_IP + PORT below to match app screen
#   3. Phone & laptop on SAME Wi-Fi
#   4. Run:  python src/laptop/video_stream.py
#   Keys:   q = quit  |  a = toggle AI overlay  |  s = save frame

import os
os.environ["OPENCV_GUI_BACKEND"] = "GTK"  # GTK more reliable than Qt on Linux

import cv2
import time
import threading
import queue
import numpy as np
import requests

# ── kornia-rs (Rust) — fast JPEG decode ─────────────────────────────────────
try:
    import kornia_rs as K
    KORNIA_OK = True
except ImportError:
    KORNIA_OK = False

# ── AI processor (lane detection + PID) — optional ──────────────────────────
try:
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ai_processor import process_frame
    AI_OK = True
except ImportError:
    AI_OK = False
    def process_frame(frame_bgr):
        """No-op fallback when ai_processor.py is not present."""
        return frame_bgr, None


# ═════════════════════════════════════════════════════════════════════════════
#  CONFIG — change these to match your setup
# ═════════════════════════════════════════════════════════════════════════════
PHONE_IP    = "192.168.16.195"     # shown on app screen
PORT        = "8081"               # default for IP Webcam
USERNAME    = ""                   # leave "" if no auth
PASSWORD    = ""                   # leave "" if no auth
STREAM_PATH = "/video"             # MJPEG endpoint

WINDOW_NAME = "AI Car — Stream"
SHOW_STATS  = True                 # FPS + latency bar at top
ENABLE_AI   = True                 # lane overlay on start (toggle: 'a')

# ── ESP32 Motor Controller ──────────────────────────────────────────────────
# Set to your ESP32's IP (shown on Serial Monitor after upload).
# Leave empty "" to disable sending commands (view-only mode).
ESP32_IP    = ""                   # e.g. "192.168.16.100" ← change this
ESP32_PORT  = "80"                 # default HTTP port
BASE_SPEED  = 150                  # PWM 0-255 — base speed for tank drive
SEND_HZ     = 10                   # max commands/sec to ESP32 (10 = smooth)

# latency knobs
CHUNK_SIZE  = 8192                 # bytes per HTTP read (bigger = fewer syscalls)
QUEUE_SIZE  = 2                    # frame buffer (small = always latest frame)
# ═════════════════════════════════════════════════════════════════════════════

# build URL
if USERNAME and PASSWORD:
    _STREAM_URL = f"http://{USERNAME}:{PASSWORD}@{PHONE_IP}:{PORT}{STREAM_PATH}"
else:
    _STREAM_URL = f"http://{PHONE_IP}:{PORT}{STREAM_PATH}"
_DISPLAY_URL = f"http://{PHONE_IP}:{PORT}{STREAM_PATH}"


# ─────────────────────────────────────────────────────────────────────────────
#  ESP32 MOTOR COMMANDS — steering angle → tank drive → HTTP to ESP32
# ─────────────────────────────────────────────────────────────────────────────
_esp32_sess   = None
_last_send_t  = 0.0
_SEND_INTERVAL = 1.0 / max(1, SEND_HZ)
MAX_STEER_DEG  = 35.0              # must match ai_processor.MAX_STEER_DEG

def _init_esp32():
    """Set up persistent HTTP session for ESP32 commands."""
    global _esp32_sess
    if ESP32_IP:
        _esp32_sess = requests.Session()

def steering_to_tank(steering_deg: float, base: int = BASE_SPEED):
    """Convert PID steering angle to tank-drive (left, right) motor speeds.

    steering > 0 → turn right → left motors faster, right motors slower
    steering < 0 → turn left  → right motors faster, left motors slower

    Returns (left_speed, right_speed) each in range 0..255.
    # created by: claude + nityam | 2026-03-03
    """
    t = steering_deg / MAX_STEER_DEG          # normalize to [-1, +1]
    t = max(-1.0, min(1.0, t))
    left  = int(base * (1.0 + t))             # right turn → left goes faster
    right = int(base * (1.0 - t))             # right turn → right goes slower
    return max(0, min(255, left)), max(0, min(255, right))

def send_to_esp32(steering_deg: float):
    """Send tank-drive command to ESP32 (rate-limited, non-blocking).
    # created by: claude + nityam | 2026-03-03
    """
    global _last_send_t
    if not _esp32_sess or not ESP32_IP:
        return
    now = time.perf_counter()
    if now - _last_send_t < _SEND_INTERVAL:
        return                                # rate limit
    _last_send_t = now
    left, right = steering_to_tank(steering_deg)
    try:
        url = f"http://{ESP32_IP}:{ESP32_PORT}/drive?left={left}&right={right}"
        _esp32_sess.get(url, timeout=0.08)    # 80ms timeout — don't block display
    except Exception:
        pass                                  # fire-and-forget

def stop_esp32():
    """Send stop command to ESP32."""
    if not _esp32_sess or not ESP32_IP:
        return
    try:
        _esp32_sess.get(f"http://{ESP32_IP}:{ESP32_PORT}/stop", timeout=0.1)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
#  JPEG DECODE — kornia-rs fast path, OpenCV fallback
# ─────────────────────────────────────────────────────────────────────────────
def decode_jpeg(jpeg_bytes: bytes) -> np.ndarray:
    """JPEG bytes → BGR numpy array.
    kornia-rs decode is pure Rust (libjpeg-turbo), ~2x faster than cv2.imdecode.
    # edited by: claude + nityam | 2026-03-03
    """
    if KORNIA_OK:
        try:
            rgb = K.decode_image_jpeg(jpeg_bytes)   # (H,W,3) RGB
            bgr = K.bgr_from_rgb(rgb)               # (H,W,3) BGR
            return bgr
        except Exception:
            pass  # corrupt JPEG — fall through
    buf = np.frombuffer(jpeg_bytes, dtype=np.uint8)
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)


# ─────────────────────────────────────────────────────────────────────────────
#  READER THREAD — persistent HTTP, MJPEG byte-stream parser
# ─────────────────────────────────────────────────────────────────────────────
def reader_thread(url: str, fq: queue.Queue, stop: threading.Event):
    """Background daemon.
    Opens a persistent HTTP session (single TCP conn — no re-handshake per frame).
    Scans for JPEG markers FF D8 .. FF D9, decodes, pushes to queue.
    Drops stale frames when queue full — display always gets the latest.
    Auto-reconnects on error.
    # edited by: claude + nityam | 2026-03-03
    """
    sess = requests.Session()
    if USERNAME and PASSWORD:
        sess.auth = (USERNAME, PASSWORD)

    while not stop.is_set():
        try:
            print(f"  Connecting to {_DISPLAY_URL} ...")
            resp = sess.get(url, stream=True, timeout=5)
            resp.raise_for_status()
            print("  Connected — receiving frames.\n")

            buf = b''
            for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                if stop.is_set():
                    break
                buf += chunk

                # pull out every complete JPEG in the buffer
                while True:
                    s = buf.find(b'\xff\xd8')
                    if s == -1:
                        buf = b''   # no SOI — discard junk
                        break
                    elif s > 0:
                        buf = buf[s:]   # trim before SOI
                        s = 0
                    e = buf.find(b'\xff\xd9', 2)
                    if e == -1:
                        break   # wait for more data
                    jpg = buf[:e + 2]
                    buf = buf[e + 2:]

                    frame = decode_jpeg(jpg)
                    if frame is None or frame.size == 0:
                        continue

                    # always keep only latest — drop stale
                    try:
                        fq.put_nowait(frame)
                    except queue.Full:
                        try:
                            fq.get_nowait()
                        except queue.Empty:
                            pass
                        fq.put_nowait(frame)

        except Exception as exc:
            if not stop.is_set():
                print(f"  Stream error: {exc}")
                print("  Reconnecting in 1 s ...")
                time.sleep(1)

    print("  Reader thread stopped.")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN — display loop
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # banner
    print()
    print("=" * 55)
    print("   AI Car — Low-Latency Stream")
    print("=" * 55)
    dec = "kornia-rs (Rust/libjpeg-turbo)" if KORNIA_OK else "OpenCV (install kornia-rs for 2x speed)"
    ai  = "ai_processor loaded" if AI_OK else "ai_processor NOT found"
    esp = f"ESP32 at {ESP32_IP}:{ESP32_PORT}" if ESP32_IP else "DISABLED (set ESP32_IP to enable)"
    print(f"   Decoder : {dec}")
    print(f"   AI      : {ai}")
    print(f"   ESP32   : {esp}")
    print(f"   URL     : {_DISPLAY_URL}")
    print(f"   Keys    : q=quit  a=AI on/off  s=save  e=ESP32 stop")
    print("=" * 55)
    print()

    _init_esp32()

    fq   = queue.Queue(maxsize=QUEUE_SIZE)
    stop = threading.Event()

    t = threading.Thread(target=reader_thread, args=(_STREAM_URL, fq, stop),
                         daemon=True, name="mjpeg-reader")
    t.start()

    ai_on       = ENABLE_AI
    fps         = 0.0
    n_frames    = 0
    fps_clock   = time.perf_counter()
    save_idx    = 0

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    while True:
        # get frame (blocks up to 2 s so 'q' still works)
        try:
            frame = fq.get(timeout=2.0)
        except queue.Empty:
            print("  No frames for 2 s — is the phone app running?")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        t0 = time.perf_counter()

        # ── AI overlay ──
        if ai_on and AI_OK:
            display, steering = process_frame(frame)
            # send steering command to ESP32
            if steering is not None:
                send_to_esp32(steering)
        else:
            display  = frame
            steering = None

        # ── FPS calc ──
        n_frames += 1
        now = time.perf_counter()
        dt  = now - fps_clock
        if dt >= 0.5:
            fps       = n_frames / dt
            n_frames  = 0
            fps_clock = now

        proc_ms = (time.perf_counter() - t0) * 1000

        # ── Stats bar ──
        if SHOW_STATS:
            if display is frame:
                display = frame.copy()
            h, w = display.shape[:2]
            cv2.rectangle(display, (0, 0), (w, 28), (0, 0, 0), -1)
            tag = "rs" if KORNIA_OK else "cv2"
            txt = f"FPS:{fps:.1f}  Proc:{proc_ms:.0f}ms  [{tag}]"
            if steering is not None:
                txt += f"  Steer:{steering:+.1f}"
            cv2.putText(display, txt, (8, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1, cv2.LINE_AA)

        cv2.imshow(WINDOW_NAME, display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('a'):
            ai_on = not ai_on
            print(f"  AI overlay: {'ON' if ai_on else 'OFF'}")
            if not ai_on:
                stop_esp32()     # stop motors when AI is turned off
        elif key == ord('e'):
            stop_esp32()
            print("  ESP32: STOP sent")
        elif key == ord('s'):
            fn = f"capture_{save_idx:03d}.jpg"
            cv2.imwrite(fn, display)
            print(f"  Saved: {fn}")
            save_idx += 1

    stop.set()
    stop_esp32()               # stop motors on exit
    cv2.destroyAllWindows()
    print("\n  Stream closed.\n")


if __name__ == "__main__":
    main()
