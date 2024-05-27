from genericpath import exists
import os
from pathlib import Path
from uuid import uuid4

import cv2

from iot_recognition_service.recognition import Recognizer


def main() -> int:
    device = os.getenv("IOT_RECOGNITION_DEVICE", "cuda")
    model = os.getenv("IOT_RECOGNITION_MODEL", "model/yolov10x.pt")

    imgs_dir = Path("imgs")
    imgs_dir.mkdir(exist_ok=True)

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

            with open(imgs_dir / f"out_{entity.label}_{uuid}.jpg", "wb") as f:
                f.write(entity.image)

    return 0
