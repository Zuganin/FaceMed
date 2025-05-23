import io
from collections import Counter

from ultralytics import YOLOWorld
from PIL import Image
import torch
import  numpy as np
import cv2

from detect_disease.config import logger


def load_model(path: str):
    """
       Метод загружает модель YOLOWorld и переносит её на доступное устройство (GPU или CPU).
    """
    # Определяем доступное устройство
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    logger.debug(f"Модель использует device: {device}")
    # Загружаем модель из указанного пути
    model = YOLOWorld(path).to(device)
    return model


def get_predict(model, image):
    """
        Выполняет предсказание на основе входного изображения с использованием переданной модели.

        :param model: Загруженная модель YOLOWorld
        :param image: Изображение в виде байтов
        :return: Результаты предсказания
    """
    # Преобразуем байты в RGB изображение с помощью PIL
    image = Image.open(io.BytesIO(image)).convert("RGB")
    # Конвертируем изображение в формат BGR для OpenCV
    image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # Выполняем инференс модели
    results = model.predict(
        image_np,
        conf=0.4,   # Порог уверенности предсказания
        imgsz=640,
        half=True   # Использование половинной точности (ускорение инференса)
    )
    return results

def get_annotation(results1, results2):
    """
        Создает аннотированное изображение на основе результатов модели.

        :param results: Результаты предсказания модели
        :return: Аннотированное изображение в байтах JPEG
    """
    # Объединяем изображения с нанесенными предсказаниями (боксы, подписи)
    annotated1 = results1[0].plot()
    annotated2 = results2[0].plot()
    combined_image = cv2.addWeighted(annotated1, 0.5, annotated2, 0.5, 0)
    # Кодируем изображение в JPEG формат и получаем массив байтов
    success, buffer = cv2.imencode('.jpg', combined_image)
    annotated_bytes = buffer.tobytes()
    logger.debug(f"Изображение аннотировано и сохранено")
    return annotated_bytes

def get_report(results1, results2):
    """
        Создает текстовый отчет на основе предсказанных классов.

        :param results: Результаты предсказания модели
        :return: Строка с перечислением найденных объектов и их количества
    """
    # Получаем список ID предсказанных классов
    class_ids1 = results1[0].boxes.cls.cpu().numpy().astype(int)
    class_names1 = [results1[0].names[id] for id in class_ids1]
    class_ids2 = results2[0].boxes.cls.cpu().numpy().astype(int)
    class_names2 = [results2[0].names[id] for id in class_ids2]
    class_counts = Counter(class_names1) + Counter(class_names2)

    # Формируем текстовый отчет
    report = "Примерные результаты диагностики:\n"
    for i, (name, count) in enumerate(class_counts.items(), 1):
        report += f"{i}. {name}: {count} шт.\n"
    logger.debug(f"Отчет сформирован")
    return report

def get_disease(results1 , results2):
    """
        Формирует упрощенный текстовый отчет для базы данных (без нумерации).

        :param results: Результаты предсказания модели
        :return: Строка с заболеваниями и их количеством
    """
    # Получаем ID классов из результатов
    class_ids1 = results1[0].boxes.cls.cpu().numpy().astype(int)
    class_names1 = [results1[0].names[id] for id in class_ids1]
    class_ids2 = results2[0].boxes.cls.cpu().numpy().astype(int)
    class_names2 = [results2[0].names[id] for id in class_ids2]
    class_counts = Counter(class_names1) + Counter(class_names2)

    # Формируем отчет заболеваний для базы данных
    disease = ""
    for i, (name, count) in enumerate(class_counts.items(), 1):
        disease += f"{name} : {count}\n"
    logger.debug(f"Заболевания сформированы")
    return disease