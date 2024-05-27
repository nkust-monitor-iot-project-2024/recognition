import os
from uuid import uuid4
from ultralytics import YOLOv10
import cv2

from .recognition import Recognizer

def main() -> int:
    device = os.getenv("IOT_RECOGNITION_DEVICE", "cuda")
    model = os.getenv("IOT_RECOGNITION_MODEL", "model/yolov10x.pt")

    cv2.namedWindow('YOLO', cv2.WINDOW_NORMAL)

    recognizer = Recognizer.init_from_model_filename(model, device)
    cap = cv2.VideoCapture(0)
    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        entities = recognizer.recognize_picture(frame)
        for entity in entities:
            uuid = uuid4()

            print(f"Detected entity: {entity.label} (at {entity.x1}, {entity.y1}, {entity.x2}, {entity.y2}), confidence={entity.confidence}, uuid={uuid}")

            with open(f"imgs/out_{entity.label}_{uuid}.jpg", "wb") as f:
                f.write(entity.image)
