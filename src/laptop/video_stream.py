import cv2
import numpy as np
import kornia_rs as K

ROI_FRAC = 0.65
THRESH = 200

KP = 0.25
KD = 0.08
MAX_STEER = 35.0

class Controller:
    def __init__(self):
        self.prev_error = 0.0

    def update(self, error):
        derivative = error - self.prev_error
        self.prev_error = error
        steer = KP * error + KD * derivative
        return max(-MAX_STEER, min(MAX_STEER, steer))

_ctrl = Controller()

def process_frame(frame_bgr):
    h, w = frame_bgr.shape[:2]
    roi_y = int(h * ROI_FRAC)
    roi = frame_bgr[roi_y:h, :]

    rgb = K.bgr_from_rgb(roi)
    gray = K.gray_from_rgb(rgb)[:, :, 0]

    binary = (gray > THRESH).astype(np.uint8) * 255

    col_sum = np.sum(binary, axis=0)
    total = np.sum(col_sum)

    display = frame_bgr.copy()

    if total < 1000:
        _ctrl.prev_error = 0.0
        cv2.putText(display, "NO LINE", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return display, None

    xs = np.arange(w)
    lane_center = int(np.sum(xs * col_sum) / total)
    frame_center = w // 2

    error = lane_center - frame_center
    steering = _ctrl.update(error)

    cv2.line(display, (frame_center, roi_y), (frame_center, h), (0, 0, 255), 2)
    cv2.circle(display, (lane_center, h - 30), 8, (0, 255, 0), -1)
    cv2.arrowedLine(display,
                    (frame_center, h - 10),
                    (frame_center + int(error * 0.5), h - 10),
                    (255, 255, 0), 2, tipLength=0.3)

    cv2.putText(display, f"STEER: {steering:.2f}",
                (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (255, 255, 255), 2)

    return display, steering

def main():
    cap = cv2.VideoCapture("http://10.22.215.84:8080/video")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            display, steering = process_frame(frame)

            if steering is not None:
                print(f"Steer: {steering:.2f}")

            cv2.imshow("Lane Tracking", display)

            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()