import io
from collections import Counter

from ultralytics import YOLOWorld
from PIL import Image
import torch
import  numpy as np
import cv2

from bot.config import logger


def load_model():
    # Инициализация модели (вынесена в глобальную область для однократной загрузки)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    # Путь к файлику модели
    model = YOLOWorld("microservices/models/Yolo_train_best.pt").to(device)
    return model


def get_predict(model, image):
    # Загрузка и преобразование изображения
    image = Image.open(io.BytesIO(image)).convert("RGB")
    image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # Инференс модели
    results = model.predict(
        image_np,
        conf=0.3,
        imgsz=640,
        half=True
    )
    return results

def get_annotation(results):
    # Визуализация и сохранение
    annotated = results[0].plot()
    # Кодируем изображение в JPEG формат и получаем массив байтов
    success, buffer = cv2.imencode('.jpg', annotated)
    annotated_bytes = buffer.tobytes()
    logger.debug(f"Изображение аннотировано и сохранено")
    return annotated_bytes

def get_report(results):
    # Получаем статистику по классам
    class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
    class_names = [results[0].names[id] for id in class_ids]
    class_counts = Counter(class_names)

    # Формируем текстовый отчет
    report = "Примерные результаты диагностики:\n"
    for i, (name, count) in enumerate(class_counts.items(), 1):
        report += f"{i}. {name}: {count} шт.\n"
    logger.debug(f"Отчет сформирован")
    return report