# ai_processor.py — Lane Detection + PID Steering for AI Car
# created by: claude + nityam | 2026-03-03
#
# Detects the dotted white centerline on a black track, computes a steering
# angle to keep the robot centered on that line.
#
# Pipeline:
#   BGR frame
#     → crop bottom 50% (ROI — road only, ignore background)
#     → grayscale → Gaussian blur → binary threshold (white line pops)
#     → morphology CLOSE (connect dotted segments into continuous blob)
#     → find contours → pick contour closest to image center
#     → compute centroid → error = centroid_x − image_center_x
#     → PID controller → steering angle (degrees)
#
# Uses kornia-rs (Rust) for grayscale + resize when available — fastest path.
# Falls back to OpenCV if not installed.
#
# Draws debug overlay: ROI box, detected line contour, centroid dot,
# center reference line, steering direction arrow.

import cv2
import numpy as np

# ── Try kornia-rs for fast grayscale/resize ─────────────────────────────────
try:
    import kornia_rs as K
    _KORNIA = True
except ImportError:
    _KORNIA = False


# ═════════════════════════════════════════════════════════════════════════════
#  TUNING — adjust for your track
# ═════════════════════════════════════════════════════════════════════════════
ROI_TOP_FRAC   = 0.50        # use bottom 50% of frame (road area)
THRESH_VALUE   = 200         # binary threshold (white line ≥ this → 255)
BLUR_KSIZE     = (5, 5)      # Gaussian blur kernel
MORPH_KSIZE    = 9            # morphology close kernel (connects dotted line)
MIN_CONTOUR_PX = 80          # ignore tiny noise blobs (< this many pixels)

# PID gains — start with P-only, tune D if oscillating
KP = 0.15                    # proportional — how aggressively to correct
KI = 0.0                     # integral — usually 0 for small bots
KD = 0.05                    # derivative — damps oscillation
MAX_STEER_DEG = 35.0         # clamp output (±degrees)

# overlay colors (BGR)
COL_ROI     = (255, 200, 0)  # cyan   — ROI boundary
COL_CONTOUR = (0, 255, 255)  # yellow — detected contour
COL_CENTER  = (0, 0, 255)    # red    — image center line
COL_DOT     = (0, 255, 0)    # green  — centroid dot
# ═════════════════════════════════════════════════════════════════════════════


class PID:
    """Minimal PID controller. # created by: claude + nityam | 2026-03-03"""

    def __init__(self, kp: float, ki: float, kd: float, limit: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.limit = limit
        self._integral = 0.0
        self._prev_err = 0.0

    def update(self, error: float) -> float:
        self._integral += error
        derivative = error - self._prev_err
        self._prev_err = error
        out = self.kp * error + self.ki * self._integral + self.kd * derivative
        return max(-self.limit, min(self.limit, out))

    def reset(self):
        self._integral = 0.0
        self._prev_err = 0.0


# single shared PID instance
_pid = PID(KP, KI, KD, MAX_STEER_DEG)


# ─────────────────────────────────────────────────────────────────────────────
def _to_gray(bgr: np.ndarray) -> np.ndarray:
    """BGR → single-channel grayscale. Uses kornia-rs if available."""
    if _KORNIA:
        try:
            # bgr_from_rgb swaps channels 0↔2 — works both ways (BGR→RGB or RGB→BGR)
            rgb = K.bgr_from_rgb(bgr)       # BGR→RGB
            g = K.gray_from_rgb(rgb)         # (H,W,1) uint8
            return g[:, :, 0]                # squeeze to (H,W)
        except Exception:
            pass
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)


# ─────────────────────────────────────────────────────────────────────────────
def process_frame(frame_bgr: np.ndarray):
    """
    Main entry point — called from video_stream.py each frame.

    Args:
        frame_bgr: (H,W,3) BGR uint8 from the camera stream

    Returns:
        display: (H,W,3) BGR uint8 — frame with debug overlay drawn
        steering: float | None — steering angle in degrees (+right / −left)

    # created by: claude + nityam | 2026-03-03
    """
    display = frame_bgr.copy()
    h, w = frame_bgr.shape[:2]

    # ── 1. ROI: bottom portion of frame (road only) ─────────────────────────
    roi_y = int(h * ROI_TOP_FRAC)
    roi = frame_bgr[roi_y:h, :]
    roi_h, roi_w = roi.shape[:2]

    # draw ROI boundary on display
    cv2.rectangle(display, (0, roi_y), (w - 1, h - 1), COL_ROI, 1)

    # ── 2. Grayscale → blur → threshold ─────────────────────────────────────
    gray = _to_gray(roi)
    blur = cv2.GaussianBlur(gray, BLUR_KSIZE, 0)
    _, mask = cv2.threshold(blur, THRESH_VALUE, 255, cv2.THRESH_BINARY)

    # ── 3. Morphology close — connect dotted line segments ───────────────────
    kernel = np.ones((MORPH_KSIZE, MORPH_KSIZE), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # ── 4. Find contours ────────────────────────────────────────────────────
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # pick contour closest to horizontal center (ignore side borders)
    center_x = roi_w // 2
    best_contour = None
    best_dist = float('inf')

    for c in contours:
        area = cv2.contourArea(c)
        if area < MIN_CONTOUR_PX:
            continue
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        dist = abs(cx - center_x)
        if dist < best_dist:
            best_dist = dist
            best_contour = c
            best_cx = cx
            best_cy = int(M["m01"] / M["m00"])

    # ── 5. Compute steering ─────────────────────────────────────────────────
    if best_contour is not None:
        # draw contour (shifted back to full-frame coords)
        shifted = best_contour.copy()
        shifted[:, :, 1] += roi_y
        cv2.drawContours(display, [shifted], -1, COL_CONTOUR, 2)

        # centroid dot
        dot_y = best_cy + roi_y
        cv2.circle(display, (best_cx, dot_y), 7, COL_DOT, -1)

        # center reference line
        cv2.line(display, (center_x, roi_y), (center_x, h), COL_CENTER, 1)

        # error: positive = line is right of center → steer right
        error = best_cx - center_x
        steering = _pid.update(error)

        # direction arrow
        arrow_x = center_x + int(error * 0.5)
        cv2.arrowedLine(display, (center_x, h - 20), (arrow_x, h - 20),
                        COL_DOT, 2, tipLength=0.3)

        return display, steering
    else:
        # no line detected — keep last steering, signal None
        _pid.reset()
        cv2.putText(display, "NO LINE DETECTED", (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return display, None