FROM python:3.11


# Рабочая директория
WORKDIR /app/detect_disease

# Копируем requirements.txt для установки зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Копируем весь проект
COPY . .

# Проверяем, что модель скопирована
RUN ls -l /app/detect_disease/

# Запуск приложения
CMD ["python", "main.py"]
