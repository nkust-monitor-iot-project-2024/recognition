import logging
from tempfile import TemporaryFile
from traceback import print_exception
import cv2
import grpc
import numpy as np

from iot_recognition_service.recognition import Recognizer
from .protos.entityrecognitionpb_pb2 import RecognizeRequest, RecognizeResponse, Entity
from .protos.entityrecognitionpb_pb2_grpc import EntityRecognitionServicer

class RecognitionService(EntityRecognitionServicer):
    """The gRPC service for recognizing objects in an image."""

    def __init__(self, recognizer: Recognizer):
        self.recognizer = recognizer

    def Recognize(self, request: RecognizeRequest, context: grpc.ServicerContext) -> RecognizeResponse:
        try:
            entities = self.recognizer.recognize_picture(request.image)
        except ValueError as e:
            print_exception(e)
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except RuntimeError as e:
            print_exception(e)
            context.abort(grpc.StatusCode.INTERNAL, str(e))

        return RecognizeResponse(
            entities=(
                Entity(
                    label=entity.label,
                    x1=entity.x1,
                    x2=entity.x2,
                    y1=entity.y1,
                    y2=entity.y2,
                    confidence=entity.confidence,
                    image=entity.image,
                )
                for entity in entities
            )
        )
