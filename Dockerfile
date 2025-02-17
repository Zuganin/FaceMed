# Базовый образ Python
FROM python:3.10-alpine

# Создаем папку приложения
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Ставим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВЕСЬ проект
COPY . .

# Запускаем бота
CMD ["python", "main.py"]
