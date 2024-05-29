# IoT Monitor Recognition service

This is a Python project contains the gRPC server for recognizing the entities in the IoT pictures.

## Run

You may need to install [`rye`](https://rye-up.com) to run the server.

You also need to download a model in [GitHub](https://github.com/THU-MIG/yolov10/tree/main?tab=readme-ov-file#performance) and put it in the `model` folder.

You also need to generate the Python code from the proto file by:

```sh
task generate
```

Then, you can run the server by:

```sh
rye run iot-recognition-service
```

## Configuration

- `IOT_RECOGNITION_MODEL`: Specify the path to the model file. Default is `model/yolov10x.pt`.
- `IOT_RECOGNITION_DEVICE`: Specify the PyTorch device to run the model. Default is `cuda`.
- `IOT_RECOGNITION_SERVER_PORT`: Specify the path to the TLS certificate file. Default is `50051`.
- `IOT_RECOGNITION_SERVER_TLS_CERT`: Specify the path to the TLS certificate file. Default is empty (insecure).
- `IOT_RECOGNITION_SERVER_TLS_KEY`: Specify the path to the TLS key file. Default is empty (insecure).
- `IOT_RECOGNITION_SERVER_TLS_CA`: Specify the path to the CA key file. Default is empty (`require_client_auth=false`).
- `IOT_RECOGNITION_EXPORTER_CONSOLE`: Specify whether to export the traces to the console. Default is `false`. Set `true` forces the exporter to export the traces to the console.
- `OTEL_EXPORTER_OTLP_ENDPOINT`: Specify the OTLP HTTP endpoint (for example, the [Grafana Alloy](https://grafana.com/oss/alloy-opentelemetry-collector/) endpoint). Default is `localhost:4318`.

## License

This project is licensed under the AGPL-3.0-or-later license. See the [LICENSE](./LICENSE) file for details.
