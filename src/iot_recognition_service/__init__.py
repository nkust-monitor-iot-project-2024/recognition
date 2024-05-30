from concurrent import futures
import logging
import os
import grpc
from grpc_reflection.v1alpha import reflection

from iot_recognition_service.grpc_service import RecognitionService
from iot_recognition_service.protos import entityrecognitionpb_pb2
from iot_recognition_service.telemetry import setup_telemetry

from .protos import entityrecognitionpb_pb2_grpc

from .recognition import Recognizer


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    setup_telemetry()

    device = os.getenv("IOT_RECOGNITION_DEVICE", "cuda")
    model = os.getenv("IOT_RECOGNITION_MODEL", "model/yolov10x.pt")

    tls_key = os.getenv("IOT_RECOGNITION_SERVER_TLS_KEY")
    tls_cert = os.getenv("IOT_RECOGNITION_SERVER_TLS_CERT")
    tls_ca = os.getenv("IOT_RECOGNITION_SERVER_TLS_CA")

    server_port = os.getenv("IOT_RECOGNITION_SERVER_PORT", "50051")

    recognizer = Recognizer.init_from_model_filename(model, device)
    recognizer_grpc_service = RecognitionService(recognizer)

    server = grpc.server(
        thread_pool=futures.ThreadPoolExecutor(max_workers=8),
        compression=grpc.Compression.Gzip,
    )
    entityrecognitionpb_pb2_grpc.add_EntityRecognitionServicer_to_server(recognizer_grpc_service, server)
    reflection.enable_server_reflection((
        entityrecognitionpb_pb2.DESCRIPTOR.services_by_name["EntityRecognition"].full_name,
        reflection.SERVICE_NAME,
    ), server)

    if tls_cert and tls_key:
        logging.info("Running server with TLS certificate")

        with open(tls_key, "rb") as f:
            tls_key_data = f.read()
        with open(tls_cert, "rb") as f:
            tls_cert_data = f.read()

        if tls_ca:
            with open(tls_ca, "rb") as f:
                tls_ca_data = f.read()
        else:
            tls_ca_data = None

        server_credentials = grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=[(tls_key_data, tls_cert_data)],
            root_certificates=tls_ca_data,
            require_client_auth=tls_ca_data is not None
        )

        server.add_secure_port(f"[::]:{server_port}", server_credentials)
    else:
        logging.warn("Running server without TLS – insecure warning!!")
        server.add_insecure_port(f"[::]:{server_port}")

    logging.info(f"Server started on port {server_port}")

    server.start()
    server.wait_for_termination()

    return 0
