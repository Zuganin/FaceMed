
import grpc

from bot.config import logger
from microservices.predict.proto.proto_age  import predict_age_pb2
from microservices.predict.proto.proto_age import predict_age_pb2_grpc
from .model import *


class PredictAgeServicer(predict_age_pb2_grpc.PredictAgeServicer):

    def PredictAge(self, request, context):
        try:
            logger.info("Сервер успешно получил изображение")
            results = get_predict(request)

            # Обработка результатов
            if len(results[0]) == 0:
                logger.info("Модель не обнаружила никаких симптомов")
                return predict_age_pb2.PredictionResponse(image=request.image, report="Объекты не обнаружены")

            logger.info("Формирование аннотированного изображения и отчета")
            annotated_bytes = get_annotation(results, request)
            report = get_report(results)

            return predict_age_pb2.PredictionResponse(image=annotated_bytes, report=report)

        except Exception as e:
            # Логируем ошибку
            logger.error(f"Error: {str(e)}")
            # Отправляем клиенту понятное сообщение
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Image processing failed: {str(e)}")