# video_stream.py — Phone Camera Stream Receiver
# created by: claude + nityam | 2026-02-27 8:15 PM IST
#
# Captures live MJPEG video stream from phone running "IP Webcam" app.
# App: https://play.google.com/store/apps/details?id=com.shenyaocn.android.WebCam
#
# HOW TO USE:
#   1. Install "IP Webcam" app on your phone (link above)
#   2. Open the app → tap "Start Server"
#   3. Note the IP address shown on screen (e.g. 192.168.1.50)
#   4. Make sure phone and laptop are on the SAME Wi-Fi network
#   5. Change PHONE_IP below to your phone's IP
#   6. Run: python video_stream.py
#   7. Press 'q' to quit

import cv2
from ultralytics import YOLO

model_path = "src/models/best.pt"

model = YOLO(model_path)
# ── CONFIG ──────────────────────────────────────────
PHONE_IP = "192.168.1.50"        # Change this to your phone's IP
PORT = "8080"                     # Default port for IP Webcam app
STREAM_URL = f"http://{PHONE_IP}:{PORT}/video"
WINDOW_NAME = "AI Car — Phone Stream"
# ────────────────────────────────────────────────────

def main():
    print(f"Connecting to stream: {STREAM_URL}")
    print("Make sure your phone and laptop are on the same Wi-Fi.\n")

    cap = cv2.VideoCapture(STREAM_URL)

    if not cap.isOpened():
        print("❌ Error: Could not open stream.")
        print("   → Check if the app is running on your phone")
        print(f"   → Check if {PHONE_IP} is correct (see app screen)")
        print("   → Check if both devices are on the same Wi-Fi")
        return

    print("✅ Stream connected! Press 'q' to quit.\n")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("⚠️  Failed to grab frame. Retrying...")
            continue
        result = model.predict(frame)
        
        for r in results:
        boxes = r.boxes
        for box in boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            print("Detected:", class_id, confidence)

        
    
        cv2.imshow(WINDOW_NAME, frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Stream closed.")

if __name__ == "__main__":
    main()
