# utils.py
import numpy as np
import cv2
from PIL import Image

def preprocess(img):
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    resize = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    process_img = cv2.adaptiveThreshold(resize, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 61, 11)
    return process_img
