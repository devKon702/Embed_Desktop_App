import urllib.request
import numpy as np
import cv2

class UrlService:
    def __init__(self, hostname, path):
        self.url = f"http://{hostname}/{path}"

    def receive(self):
        img_resp = urllib.request.urlopen(self.url)
        img_np = np.array(bytearray(img_resp.read()),dtype=np.uint8)
        frame = cv2.imdecode(img_np,-1)
        return frame
