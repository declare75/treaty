# Используем официальный образ Python
FROM python:3.9-slim

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . /app/

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 8000
EXPOSE 8000

# Запускаем сервер Django через gunicorn
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "your_project_name.wsgi:application"]
