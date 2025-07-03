# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем зависимости для работы с видео, PIL и FastAPI
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Необходимые системные библиотеки, а именно из пакета GTK (glib)
# Для Debain
RUN apt install libglib2.0-0
RUN apt install libglib2.0-dev

# Создаём рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY ./app /app

# Устанавливаем зависимости из requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт
EXPOSE 8000

# Запускаем сервер
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]