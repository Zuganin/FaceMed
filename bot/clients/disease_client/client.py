
import grpc

from bot.config import logger
from bot.clients.proto_disease import predict_disease_pb2, predict_disease_pb2_grpc


def get_predict(image_path):
    """
        Функция для отправки изображения на сервер для диагностики заболевания.

        :param image_path: Путь к изображению, которое будет отправлено на сервер
        :return: Ответ от сервера с результатами диагностики
    """
    logger.debug("Запуск клиента")
    # Устанавлcиваем соединение с сервером
    channel = grpc.insecure_channel('detect_disease1:50052')
    stub = predict_disease_pb2_grpc.PredictDiseaseStub(channel)
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
    request =  predict_disease_pb2.ImageRequest(image_data=image_bytes)
    logger.debug("Отправляем запрос на сервер...")
    # Отправляем запрос и получаем ответ
    response = stub.DetectDisease(request)
    logger.debug("Ответ получен")
    return  response

