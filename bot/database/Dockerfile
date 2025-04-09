# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app/database

# Копируем файл зависимостей и устанавливаем их
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код в контейнер
COPY . .

# Команда, которая будет выполнена при старте контейнера
CMD ["python", "database_instance.py"]
