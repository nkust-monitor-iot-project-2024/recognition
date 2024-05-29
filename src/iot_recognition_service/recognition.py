from dataclasses import dataclass
import logging
import mimetypes
from typing import Self

import cv2
from cv2.typing import MatLike
import numpy as np
from numpy import ndarray
from torch import Tensor
from opentelemetry import trace, _logs
from opentelemetry.trace import SpanKind
from ultralytics import YOLOv10
from ultralytics.engine.results import Results


@dataclass(frozen=True)
class Entity:
    """Entity class for representing an object in an image.

    Properties:
        label: The label of the object. For humans, it is "person".
        x1: The lower x coordinate of the bounding box.
        x2: The higher x coordinate of the bounding box.
        y1: The lower y coordinate of the bounding box.
        y2: The higher y coordinate of the bounding box.
        confidence: The confidence of the object detection in range [0.0, 1.0].
        image: The cropped image of the object.
        image_mime: The MIME type of the image.
    """
    label: str
    x1: float
    x2: float
    y1: float
    y2: float
    confidence: float
    image: bytes
    image_mime: str



class Recognizer:
    """The high level wrapper of YOLOv10 for recognizing objects in an image."""

    logger = _logs.get_logger("recognizer")
    tracer = trace.get_tracer("recognizer")

    def __init__(self, model: YOLOv10, device: str):
        self.model = model
        self.device = device

    @classmethod
    def init_from_model_filename(cls, filename: str, device: str) -> Self:
        """Initialize the Recognizer from a model filename.

        Args:
            filename: The filename of the model.
            device: The Torch device to run the model on.
        """
        return cls(model=YOLOv10(filename), device=device)

    """Recognition class for recognizing objects in an image."""
    def recognize_picture(self, image: bytes, image_mime: str) -> list[Entity]:
        """Recognize objects in an image.

        Args:
            image: The image data as bytes.
            image_mime: The MIME type of the image.

        Returns:
            A list of Entity objects representing the objects detected in the image.

        Exceptions:
            ValueError: If the image is empty.
            ValueError: If the image cannot be decoded with cv2.
            ValueError: If the image cannot be converted to a numpy array.
            ValueError: If the cropped image cannot be encoded to the given fromat.
            RuntimeError: If an unknown error occurs.
        """

        with self.tracer.start_as_current_span("Recognizer.recognize_picture", kind=SpanKind.INTERNAL) as span:
            span.add_event("decoding picture")
            decoded_frame = decode_image(image, image_mime)

            span.add_event("start recognition by calling YOLO")
            results: list[Results] = self.model.predict(decoded_frame, device=self.device)
            if len(results) == 0:
                span.add_event("no results detected")

                span.set_status(trace.StatusCode.OK, "No Results detected in the image.")
                return []

            span.add_event("finding box in the recognition results")
            result = results[0]
            if result.boxes is None:
                span.add_event("no boxes detected")

                span.set_status(trace.StatusCode.OK, "No boxes detected in the image.")
                return []

            span.add_event("converting box tensor to entities")
            names = self.model.names
            entities = [
                box_tensor_to_entity(data, names, decoded_frame, image_mime)
                for data in result.boxes.data
            ]
            logging.info("Recognized entities: %s", [entity.label for entity in entities])
            span.add_event("recognized")

            return entities


def decode_image(image: bytes, mime: str) -> MatLike:
    """Decode an image from bytes to a numpy array.

    Args:
        image: The image data as bytes.
        mime: The MIME type of the image.

    Returns:
        The decoded image as a numpy array.

    Exceptions:
        ValueError: If the image is empty.
        ValueError: If the image MIME type is not one of PNG or JPEG.
        ValueError: If the image cannot be decoded with cv2.
        ValueError: If the image cannot be converted to a numpy array.
        RuntimeError: If an unknown error occurs.
    """

    if len(image) == 0:
        raise ValueError("No image is provided.")

    if mime not in ["image/jpeg", "image/png"]:
        raise ValueError("Invalid image MIME type.")

    try:
        img_nparray = np.frombuffer(image, dtype=np.uint8)
        return cv2.imdecode(img_nparray, cv2.IMREAD_COLOR)
    except cv2.error as e:
        raise ValueError("Failed to decode the image with cv2.") from e
    except np.exceptions as e:
        raise ValueError("Failed to convert the image to a numpy array.") from e
    except Exception as e:
        raise RuntimeError("Unknown error") from e


def box_tensor_to_entity(box_tensor: Tensor | ndarray, names: list[str], frame: MatLike, image_mime_to_encode: str) -> Entity:
    """Turn a box tensor returns by YOLO to the high-level Entity.

    Args:
        box_tensor: The box tensor (YOLO.predict().boxes[0])
        names: The names of the objects.
        frame: The frame from which the box tensor was extracted.
        image_mime_to_encode: The MIME type of the encoded image.

    Returns:
        The Entity object.

    Exceptions:
        ValueError: If the cropped image cannot be encoded to the given format.
        ValueError: If the image MIME type is not supported.
    """
    x1 = int(box_tensor[0])
    y1 = int(box_tensor[1])
    x2 = int(box_tensor[2])
    y2 = int(box_tensor[3])
    confidence = float(box_tensor[4])
    label = names[int(box_tensor[5])]

    cropped_image = frame[y1:y2, x1:x2]

    try:
        extension = mimetypes.guess_extension(image_mime_to_encode)
        if extension is None:
            raise ValueError("Unsupported image MIME type.")

        ok, cropped_image_encoded = cv2.imencode('.'+extension, cropped_image)
        assert ok
    except cv2.error as e:
        raise ValueError("Failed to encode the cropped image to JPG.") from e
    except AssertionError:
        raise ValueError("Failed to encode the cropped image to JPG.")

    cropped_image_jpg_bytes = cropped_image_encoded.tobytes(order="C")

    return Entity(
        label=label,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
        confidence=confidence,
        image=cropped_image_jpg_bytes,
        image_mime=image_mime_to_encode,
    )

