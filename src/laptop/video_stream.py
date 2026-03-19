import cv2
import numpy as np
from ultralytics import YOLO

ROI_FRAC = 0.65
THRESH = 200
KP, KD = 0.25, 0.08
MAX_STEER = 35.0
YOLO_SKIP_FRAMES = 5 
DETECTION_SIZE = 320 

SIGN_CONFIG = {
    "stop sign": {"color": (0, 0, 255), "dist_factor": 4000},
    "30_speed":  {"color": (0, 255, 0), "dist_factor": 3500},
    "40_speed":  {"color": (255, 255, 0), "dist_factor": 3500},
    "parking":   {"color": (255, 0, 255), "dist_factor": 5000}
}

model = YOLO("D:\\ai car\\ai-car\\src\\laptop\\models\\best.pt")

class Controller:
    def __init__(self):
        self.prev_error = 0.0
    def update(self, error):
        derivative = error - self.prev_error
        self.prev_error = error
        return max(-MAX_STEER, min(MAX_STEER, (KP * error) + (KD * derivative)))

_ctrl = Controller()
frame_count = 0
last_detections = []

def process_frame(frame):
    global frame_count, last_detections
    h, w = frame.shape[:2]
    active_sign_label = None
    
    if frame_count % YOLO_SKIP_FRAMES == 0:
        results = model(frame, imgsz=DETECTION_SIZE, verbose=False, conf=0.4, device='cpu')
        last_detections = []
        for r in results:
            for box in r.boxes:
                label = model.names[int(box.cls[0])]
                print(label)
                if label in SIGN_CONFIG:
                    last_detections.append({
                        "box": box.xyxy[0].cpu().numpy(),
                        "label": label
                    })
    
    frame_count += 1

    for det in last_detections:
        label = det["label"]
        coords = det["box"]
        config = SIGN_CONFIG[label]
        active_sign_label = label
        
        x1, y1, x2, y2 = map(int, coords)
        box_width = x2 - x1
        distance = config["dist_factor"] / box_width if box_width > 0 else 0
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), config["color"], 2)
        cv2.putText(frame, f"{label.upper()} {distance:.1f}cm", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, config["color"], 2)

    roi_y = int(h * ROI_FRAC)
    gray = cv2.cvtColor(frame[roi_y:, :], cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, THRESH, 255, cv2.THRESH_BINARY)
    col_sum = np.sum(binary, axis=0)
    total = np.sum(col_sum)

    steering = None
    if total > 1000:
        lane_center = int(np.sum(np.arange(w) * col_sum) / total)
        steering = _ctrl.update(lane_center - (w // 2))
        cv2.line(frame, (w//2, h), (w//2 + int(steering*2), h-50), (255, 0, 0), 3)
        cv2.putText(frame, f"STEER: {steering:.1f}", (20, h-20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    else:
        _ctrl.prev_error = 0.0

    return frame, steering, active_sign_label

def main():
    cap = cv2.VideoCapture("http://10.134.160.209:8080/video")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    while True:
        ret, frame = cap.read()
        if not ret: break

        display, steering, sign = process_frame(frame)

        if sign:
            print(f"SIGN: {sign.upper()} | Steer: {steering if steering else 0:.2f}")
            pass
        elif steering is not None:
            print(f"Steer: {steering:.2f}")

        cv2.imshow("AI Car Dashboard", display)
        if cv2.waitKey(1) & 0xFF == 27: break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()