
import grpc

from bot.config import logger
from microservices.predict.proto  import predict_disease_pb2
from microservices.predict.proto import predict_disease_pb2_grpc

from .model import *

class PredictDiseaseServicer(predict_disease_pb2_grpc.PredictDiseaseServicer):
    def __init__(self):
        self.model = load_model()
        logger.info("Модель успешно загружена на сервер")

    def DetectDisease(self, request, context):
        try:
            logger.info("Сервер успешно получил изображение")
            results = get_predict(self.model, request.image_data)

            # Обработка результатов
            if len(results[0]) == 0:
                logger.info("Модель не обнаружила никаких симптомов")
                return predict_disease_pb2.DetectionResponse(image=request.image, report="Объекты не обнаружены")

            logger.info("Формирование аннотированного изображения и отчета")
            annotated_bytes = get_annotation(results)
            report = get_report(results)

            return predict_disease_pb2.DetectionResponse(image=annotated_bytes, report=report)

        except Exception as e:
            # Логируем ошибку
            logger.error(f"Error: {str(e)}")
            # Отправляем клиенту понятное сообщение
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Image processing failed: {str(e)}")
