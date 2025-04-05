import grpc
from concurrent import futures


from bot.config import logger
from microservices.predict.proto.proto_disease import predict_disease_pb2_grpc
from microservices.predict.services.detect_disease.predict_service import PredictDiseaseServicer



class Server_disease:
    """
        Класс для создания и управления gRPC-сервером для сервиса предсказания заболеваний.
    """

    def __init__(self):
        # Создание gRPC-сервера с использованием пула потоков (до 10 одновременно)
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        # Регистрируем реализацию gRPC-сервиса (PredictDiseaseServicer) на сервере
        predict_disease_pb2_grpc.add_PredictDiseaseServicer_to_server(PredictDiseaseServicer(), self.server)

        # Настраиваем порт, на котором будет работать сервер (50051)
        self.server.add_insecure_port('[::]:50051')
        logger.debug("Сервер проинициализирован")

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

def run_server_disease(server_instance):
    """
        Функция для запуска сервера. Сначала запускает, затем ожидает завершения.

        :param server_instance: экземпляр класса Server_disease
    """
    server_instance.start()
    server_instance.wait()

