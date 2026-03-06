import cv2
import numpy as np
import kornia_rs as K
import time
from ultralytics import YOLO

ROI_FRAC = 0.65
THRESH = 200
KP = 0.25
KD = 0.08
MAX_STEER = 35.0
MODEL_PATH = "models/yolo26n.pt"
class Controller:
    def __init__(self):
        self.prev_error = 0.0

    def update(self, error):
        derivative = error - self.prev_error
        self.prev_error = error
        steer = KP * error + KD * derivative
        return max(-MAX_STEER, min(MAX_STEER, steer))

_ctrl = Controller()
_yolo = YOLO(MODEL_PATH)

def process_frame(frame_bgr):
    start_time = time.perf_counter()
    h, w = frame_bgr.shape[:2]
    
    yolo_results = _yolo(frame_bgr, verbose=False)[0]
    stop_detected = False
    
    for box in yolo_results.boxes:
        if int(box.cls[0]) == 11:
            stop_detected = True
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(frame_bgr, "STOP SIGN", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    roi_y = int(h * ROI_FRAC)
    roi = frame_bgr[roi_y:h, :]
    rgb = K.bgr_from_rgb(roi)
    gray = K.gray_from_rgb(rgb)[:, :, 0]
    binary = (gray > THRESH).astype(np.uint8) * 255
    col_sum = np.sum(binary, axis=0)
    total = np.sum(col_sum)

    display = frame_bgr.copy()
    steering = None

    if total < 1000:
        _ctrl.prev_error = 0.0
        cv2.putText(display, "NO LINE", (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        xs = np.arange(w)
        lane_center = int(np.sum(xs * col_sum) / total)
        frame_center = w // 2
        error = lane_center - frame_center
        steering = _ctrl.update(error)

        cv2.line(display, (frame_center, roi_y), (frame_center, h), (0, 0, 255), 2)
        cv2.circle(display, (lane_center, h - 30), 8, (0, 255, 0), -1)
        cv2.arrowedLine(display, (frame_center, h - 10),
                        (frame_center + int(error * 0.5), h - 10),
                        (255, 255, 0), 2, tipLength=0.3)

    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000

    cv2.putText(display, f"Latency: {latency_ms:.1f}ms", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    if stop_detected:
        cv2.putText(display, "STATUS: STOPPING", (20, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    elif steering is not None:
        cv2.putText(display, f"Steer: {steering:.2f}", (20, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return display, steering, latency_ms

def main():
    cap = cv2.VideoCapture("http://10.22.215.84:8080/video")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    prev_frame_time = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            display, steering, proc_latency = process_frame(frame)
            
            new_frame_time = time.perf_counter()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time

            cv2.putText(display, f"FPS: {int(fps)}", (20, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Lane Tracking & Stop Detection", display)

            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()