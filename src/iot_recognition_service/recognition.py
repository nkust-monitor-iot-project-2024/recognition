from dataclasses import dataclass
import logging
from typing import Self

import cv2
from cv2.typing import MatLike
from numpy import ndarray
from torch import Tensor
from ultralytics import YOLOv10
from ultralytics.engine.results import Results


@dataclass(frozen=True)
class Entity:
    """Entity class for representing an object in an image."""
    label: str
    x1: float
    x2: float
    y1: float
    y2: float
    confidence: float
    image: bytes



class Recognizer:
    model: YOLOv10

    def __init__(self, model: YOLOv10, device: str):
        self.model = model
        self.device = device

    @classmethod
    def init_from_model_filename(cls, filename: str, device: str) -> Self:
        return cls(model=YOLOv10(filename), device=device)

    """Recognition class for recognizing objects in an image."""
    def recognize_picture(self, frame: MatLike) -> list[Entity]:
        """Recognize objects in an image."""
        results: list[Results] = self.model.predict(frame, device=self.device)
        if len(results) == 0:
            logging.warning("No Results detected in the image.")
            return []

        result = results[0]
        if result.boxes is None:
            logging.warning("No boxes detected in the image.")
            return []

        names = self.model.names
        entities = [
            box_tensor_to_entity(data, names, frame)
            for data in result.boxes.data
        ]

        return entities


def box_tensor_to_entity(box_tensor: Tensor | ndarray, names: list[str], frame: MatLike) -> Entity:
    x1 = int(box_tensor[0])
    y1 = int(box_tensor[1])
    x2 = int(box_tensor[2])
    y2 = int(box_tensor[3])
    confidence = float(box_tensor[4])
    label = names[int(box_tensor[5])]

    cropped_image = frame[y1:y2, x1:x2]
    ok, cropped_image_jpg = cv2.imencode('.jpg', cropped_image)
    if not ok:
        raise ValueError("Failed to encode the cropped image to JPG.")

    cropped_image_jpg_bytes = cropped_image_jpg.tobytes(order="C")

    return Entity(
        label=label,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
        confidence=confidence,
        image=cropped_image_jpg_bytes
    )

