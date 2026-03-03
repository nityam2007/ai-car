import cv2
import numpy as np
import requests



# ── CONFIG ──────────────────────────────────────────
PHONE_IP = "192.168.16.198"       # Change this to your phone's IP
PORT = "8081"                     # Default port for IP Webcam app
USERNAME = ""                     # App username (leave "" if no auth)
PASSWORD = ""                     # App password (leave "" if no auth)
STREAM_PATH = "/video"            # Stream endpoint
WINDOW_NAME = "AI Car — Phone Stream"
SHOW_STATS = True                 # Show FPS + latency on screen (True/False)
# ────────────────────────────────────────────────────



# PHONE_IP = "192.168.1.50"
# PORT = "8080"
STREAM_URL = f"http://{PHONE_IP}:{PORT}{STREAM_PATH}"
WINDOW_NAME = "AI Car — Phone Stream"



def main():
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    while True:
        try:
            response = requests.get(STREAM_URL, timeout=1)
            img_array = np.frombuffer(response.content, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if frame is None:
                continue

            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        except:
            continue

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()