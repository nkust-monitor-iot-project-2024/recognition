# IoT Monitor Recognition service

This is a Python project contains the gRPC server for recognizing the entities in the IoT pictures.

## Run

You may need to install [`rye`](https://rye-up.com) to run the server.

You also need to download a model in [GitHub](https://github.com/THU-MIG/yolov10/tree/main?tab=readme-ov-file#performance) and put it in the `model` folder.

Then, you can run the server by:

```rye
rye run iot-recognition-service
```

## Configuration

- `IOT_RECOGNITION_MODEL`: Specify the path to the model file. Default is `model/yolov10x.pt`.
- `IOT_RECOGNITION_DEVICE`: Specify the PyTorch device to run the model. Default is `cuda`.
- `IOT_RECOGNITION_SERVER_PORT`: Specify the path to the TLS certificate file. Default is `50051`.
- `IOT_RECOGNITION_SERVER_TLS_CERT`: Specify the path to the TLS certificate file. Default is empty (insecure).
- `IOT_RECOGNITION_SERVER_TLS_KEY`: Specify the path to the TLS key file. Default is empty (insecure).
- `IOT_RECOGNITION_SERVER_TLS_CA`: Specify the path to the CA key file. Default is empty (`require_client_auth=false`).

## License

This project is licensed under the AGPL-3.0-or-later license. See the [LICENSE](./LICENSE) file for details.