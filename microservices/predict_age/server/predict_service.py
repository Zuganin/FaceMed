import grpc

from microservices.predict_age.proto_age  import predict_age_pb2
from microservices.predict_age.proto_age import predict_age_pb2_grpc
from .model import *


class PredictAgeServicer(predict_age_pb2_grpc.PredictAgeServicer):
    """
        Класс-сервис, реализующий gRPC-интерфейс PredictAge.
        Обрабатывает запрос на предсказание возраста и пола с аннотацией изображения.
    """
    def PredictAge(self, request, context):
        """
            Метод gRPC-сервиса для обработки изображения и возврата результатов анализа.

            :param request: объект запроса с полем image_data (байтовое изображение)
            :param context: контекст gRPC-сессии (для отправки ошибок и метаданных)
            :return: PredictionResponse с аннотированным изображением и текстовым отчетом
        """
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