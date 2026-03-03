# video_stream.py — Low-Latency Phone Camera Stream Receiver
# created by: claude + nityam | 2026-02-27 8:15 PM IST
# edited by: claude + nityam | 2026-02-28 — FPS/latency overlay, auth, manual MJPEG parser
# edited by: claude + nityam | 2026-03-03 — full rewrite: kornia-rs (Rust) + threaded pipeline
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
PHONE_IP    = "192.168.16.198"     # shown on app screen
PORT        = "8081"               # default for IP Webcam
USERNAME    = ""                   # leave "" if no auth
PASSWORD    = ""                   # leave "" if no auth
STREAM_PATH = "/video"             # MJPEG endpoint

WINDOW_NAME = "AI Car — Stream"
SHOW_STATS  = True                 # FPS + latency bar at top
ENABLE_AI   = True                 # lane overlay on start (toggle: 'a')

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
    print(f"   Decoder : {dec}")
    print(f"   AI      : {ai}")
    print(f"   URL     : {_DISPLAY_URL}")
    print(f"   Keys    : q=quit  a=AI on/off  s=save")
    print("=" * 55)
    print()

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
        elif key == ord('s'):
            fn = f"capture_{save_idx:03d}.jpg"
            cv2.imwrite(fn, display)
            print(f"  Saved: {fn}")
            save_idx += 1

    stop.set()
    cv2.destroyAllWindows()
    print("\n  Stream closed.\n")


if __name__ == "__main__":
    main()
