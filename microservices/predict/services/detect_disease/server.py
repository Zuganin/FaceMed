import grpc
from concurrent import futures


from bot.config import logger
from microservices.predict.proto.proto_disease import predict_disease_pb2_grpc
from microservices.predict.services.detect_disease.predict_service import PredictDiseaseServicer



class Server_disease:
    def __init__(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        predict_disease_pb2_grpc.add_PredictDiseaseServicer_to_server(PredictDiseaseServicer(), self.server)
        self.server.add_insecure_port('[::]:50051')
        logger.debug("Сервер проинициализирован")

    def start(self):
        self.server.start()
        logger.info("gRPC сервер запущен на порту 50051")

    def wait(self):
        self.server.wait_for_termination()
        logger.info("gRPC сервер завершил работу")

    def stop(self):
        self.server.stop(grace=False)
        logger.info("gRPC сервер остановлен")

def run_server_disease(server_instance):
    server_instance.start()
    server_instance.wait()

