import requests
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import io

PHONE_IP = "192.168.1.50"
PORT = "8080"
STREAM_URL = f"http://{PHONE_IP}:{PORT}/shot.jpg"

plt.ion()
fig, ax = plt.subplots()
img_display = None

while True:
    try:
        response = requests.get(STREAM_URL, timeout=1)
        image = Image.open(io.BytesIO(response.content))
        frame = np.array(image)

        if img_display is None:
            img_display = ax.imshow(frame)
            ax.axis("off")
        else:
            img_display.set_data(frame)

        plt.draw()
        plt.pause(0.001)

    except:
        continue

