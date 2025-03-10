
import grpc

from bot.config import logger
from bot.clients.proto_age import  predict_age_pb2, predict_age_pb2_grpc


def get_predict(image_path):
    """
        Функция для отправки изображения на сервер для предсказания возраста.

        :param image_path: Путь к изображению, которое будет отправлено на сервер
        :return: Ответ от сервера с результатами предсказания возраста
    """
    logger.debug("Запуск клиента")

    # Устанавливаем соединение с сервером, расположенным на localhost:50052
    channel = grpc.insecure_channel('predict_age1:50051')
    stub = predict_age_pb2_grpc.PredictAgeStub(channel)
    logger.debug("Соединение с сервером установлено")

    # Читаем изображение из файла
    try:
        with open(image_path, 'rb') as image_file:
            image_bytes = image_file.read()
    except FileNotFoundError:
        print(f"Файл {image_path} не найден. Пожалуйста, убедитесь, что файл существует.")
        return

    logger.debug(f"Отправляем изображение размером {len(image_bytes)} байт")
    # Формируем запрос

    request =  predict_age_pb2.ImageRequest(image_data=image_bytes)
    logger.debug("Отправляем запрос на сервер...")

    # Отправляем запрос и получаем ответ
    response = stub.PredictAge(request)
    logger.debug("Ответ получен")
    return  response

