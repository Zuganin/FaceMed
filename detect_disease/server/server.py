import os

import grpc
from concurrent import futures

from detect_disease.config import logger
from detect_disease.proto_disease import predict_disease_pb2_grpc
from detect_disease.server.predict_service import PredictDiseaseServicer


class Server_disease:
    """
        Класс для создания и управления gRPC-сервером для сервиса предсказания заболеваний.
    """

    def __init__(self):
        # Создание gRPC-сервера с использованием пула потоков (до 10 одновременно)
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        # Регистрируем реализацию gRPC-сервиса (PredictDiseaseServicer) на сервере
        predict_disease_pb2_grpc.add_PredictDiseaseServicer_to_server(PredictDiseaseServicer(), self.server)

        server_addres = f"{os.getenv('GRPC_HOST_LOCAL')}:{os.getenv('GRPC_PORT')}"
        # Настройка порта для сервера
        # self.server.add_insecure_port(server_addres)
        self.server.add_insecure_port(server_addres)
        logger.debug(f"Сервер проинициализирован на {server_addres}")

    def start(self):
        """
            Запускает gRPC-сервер.
        """
        self.server.start()
        logger.info("gRPC сервер запущен на порту 50051")

    def wait(self):
        """
            Блокирует основной поток, пока сервер работает (для поддержки работы в фоне).
        """

        self.server.wait_for_termination()
        logger.info("gRPC сервер завершил работу")

    def stop(self):
        """
            Останавливает gRPC-сервер.
        """
        self.server.stop(grace=False)
        logger.info("gRPC сервер остановлен")

    def run_server_disease(self):
        """
            Функция для запуска сервера. Сначала запускает, затем ожидает завершения.

            :param server_instance: экземпляр класса Server_disease
        """
        self.start()
        self.wait()

