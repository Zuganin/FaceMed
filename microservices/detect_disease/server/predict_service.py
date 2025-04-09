
import grpc

from bot.config import logger
from microservices.detect_disease.proto_disease  import predict_disease_pb2
from microservices.detect_disease.proto_disease import predict_disease_pb2_grpc

from .model import *

class PredictDiseaseServicer(predict_disease_pb2_grpc.PredictDiseaseServicer):
    """
        gRPC-сервис для обработки изображений и предсказания заболеваний.
        Реализует методы, определенные в .proto файле.
    """
    def __init__(self):
        self.model = load_model()
        logger.info("Модель успешно загружена на сервер")

    def DetectDisease(self, request, context):
        """
                Метод обработки gRPC-запроса с изображением. Возвращает аннотированное изображение и отчет.

                :param request: gRPC-запрос, содержащий изображение
                :param context: Контекст запроса (для обработки ошибок и статусов)
                :return: DetectionResponse с полями image (аннотированное изображение), report и disease
        """
        try:
            logger.info("Сервер успешно получил изображение")
            results = get_predict(self.model, request.image_data)

            logger.info("Формирование аннотированного изображения и отчета")
            annotated_bytes = get_annotation(results)
            # Обработка результатов
            if len(results[0]) == 0:
                logger.info("Модель не обнаружила никаких симптомов")
                return predict_disease_pb2.DetectionResponse(image=annotated_bytes, report="Не обнаружено никаких видимых симптомов!", disease="None")

            report = get_report(results)
            disease = get_disease(results)
            return predict_disease_pb2.DetectionResponse(image=annotated_bytes, report=report, disease=disease)

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            # Отправляем клиенту понятное сообщение
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Image processing failed: {str(e)}")
