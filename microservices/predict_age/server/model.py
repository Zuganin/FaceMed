import numpy as np
from deepface import DeepFace
import cv2

from bot.config import logger

def get_image(image_data):
    """
        Преобразует байты изображения в объект изображения OpenCV.

        :param image_data: байтовое представление изображения
        :return: изображение в формате OpenCV (numpy-массив)
    """
    nparr = np.frombuffer(image_data, np.uint8)
    # Декодируем изображение (цветное изображение)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def get_predict(request):
    """
        Выполняет анализ лица на изображении с помощью DeepFace.

        :param request: gRPC-запрос, содержащий байты изображения
        :return: результат анализа от DeepFace
    """
    img = get_image(request.image_data)
    logger.debug("Изображение успешно десериализовано")
    # Анализ изображения с DeepFace
    try:
        analysis = DeepFace.analyze(img, actions=['age', 'gender'], enforce_detection=False)
        return analysis
    except ValueError as e:
        if "Face could not be detected" in str(e):
            return "❌ Лицо не найдено на изображении"


def get_annotation(results, request):
    """
        Добавляет аннотацию на изображение — прямоугольник вокруг лица.

        :param results: результат анализа от DeepFace
        :param request: gRPC-запрос с изображением
        :return: изображение в байтах с нанесенной разметкой
    """
    img = get_image(request.image_data)

    # Рисуем квадрат на лице
    if 'region' in results[0]:
        face_location = results[0]['region']
        x, y, w, h = face_location['x'], face_location['y'], face_location['w'], face_location['h']
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    success, buffer = cv2.imencode('.jpg', img)
    annotated_bytes = buffer.tobytes()
    logger.debug(f"Изображение аннотировано и сохранено")
    return annotated_bytes


def get_report(results):
    """
        Формирует текстовый отчет по результатам анализа лица (возраст и пол).

        :param results: результат анализа от DeepFace
        :return: строка с кратким отчетом
    """
    # Получаем данные анализа
    age = results[0]['age']
    gender = results[0]['gender']

    age_range = f"{age - 2}–{age + 2}"

    gender_translation = {"Woman": "Женщина", "Man": "Мужчина"}
    dominant_gender = max(gender, key=gender.get)
    logger.debug(f"Отчет сформирован")
    return f"Возможный возраст: {age_range}\nВозможный пол: {gender_translation[dominant_gender]} ({round(gender[dominant_gender], 2)}%)"


