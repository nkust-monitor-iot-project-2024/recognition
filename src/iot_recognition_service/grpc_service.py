import logging
import grpc

from opentelemetry import trace

from iot_recognition_service.recognition import Recognizer
from .protos.entityrecognitionpb_pb2 import RecognizeRequest, RecognizeResponse, Entity
from .protos.entityrecognitionpb_pb2_grpc import EntityRecognitionServicer

class RecognitionService(EntityRecognitionServicer):
    """The gRPC service for recognizing objects in an image."""

    logger = logging.getLogger(__name__)
    tracer = trace.get_tracer(__name__)

    def __init__(self, recognizer: Recognizer):
        self.recognizer = recognizer

    def Recognize(self, request: RecognizeRequest, context: grpc.ServicerContext) -> RecognizeResponse:
        with self.tracer.start_as_current_span("RecognitionService/Recognize") as span:
            span.add_event("recognize picture")
            try:
                entities = self.recognizer.recognize_picture(request.image)
            except ValueError as e:
                span.set_status(trace.StatusCode.ERROR, "User specifies a invalid argument")
                span.record_exception(e)

                context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Invalid argument: {e}")
            except RuntimeError as e:
                span.set_status(trace.StatusCode.ERROR, "Internal error")
                span.record_exception(e)

                context.abort(grpc.StatusCode.INTERNAL, str(e))
            span.add_event("done recognize picture")

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
