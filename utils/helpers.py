import numpy as np
import cv2

def image_to_bytes(image, extension = ".jpg"):
    image_data = np.array(image, dtype=np.uint8)
    _, image_data = cv2.imencode(extension, image)
    image_bytes = image_data.tobytes()
    return image_bytes

def bytes_to_image(image_bytes):
    image_np = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    return image

def bgr_2_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def equalizeHist_filter(image):
    return cv2.equalizeHist(image)


