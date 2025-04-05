import grpc
from concurrent import futures


from bot.config import logger
from microservices.predict.proto.proto_age import predict_age_pb2_grpc
from microservices.predict.services.predict_age.predict_service import PredictAgeServicer



class Server_age:
    """
        Класс для создания и управления gRPC сервером для сервиса предсказания возраста.
    """
    def __init__(self):
        """
            Инициализация gRPC сервера с настройками и добавлением сервиса.
        """
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        predict_age_pb2_grpc.add_PredictAgeServicer_to_server(PredictAgeServicer(), self.server)

        # Настройка порта для сервера (50052)
        self.server.add_insecure_port('[::]:50052')
        logger.debug("Сервер проинициализирован")

    def start(self):
        """
            Запускает сервер на указанном порту.
        """
        self.server.start()
        logger.info("gRPC сервер запущен на порту 50052")

    def wait(self):
        """
            Блокирует основной поток, пока сервер работает (ожидает завершения работы сервера).
        """
        self.server.wait_for_termination()
        logger.info("gRPC сервер завершил работу")

    def stop(self):
        """
            Останавливает сервер.
        """
        self.server.stop(grace=False)
        logger.info("gRPC сервер остановлен")

def run_server_age(server_instance):
    """
        Функция для запуска gRPC сервера.

        :param server_instance: экземпляр класса Server_age
    """
    server_instance.start()
    server_instance.wait()

