import cv2
import grpc
import numpy as np

from iot_recognition_service.recognition import Recognizer
from .protos.entityrecognitionpb_pb2 import RecognizeRequest, RecognizeResponse, Entity
from .protos.entityrecognitionpb_pb2_grpc import EntityRecognitionServicer

class RecognitionService(EntityRecognitionServicer):
    def __init__(self, recognizer: Recognizer):
        self.recognizer = recognizer

    def Recognize(self, request: RecognizeRequest, context: grpc.ServicerContext) -> RecognizeResponse:
        try:
            img_nparray = np.frombuffer(request.image)
            decoded_image = cv2.imdecode(img_nparray, cv2.IMREAD_COLOR)
        except cv2.error as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        entities = self.recognizer.recognize_picture(decoded_image)
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
