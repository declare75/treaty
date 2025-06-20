# Веб-приложение «Репетитор»

«Репетитор» — это современное веб-приложение для поиска преподавателей, организации онлайн-занятий и общения через чат. Сервис обеспечивает удобный интерфейс, высокую производительность и безопасность в соответствии с отраслевыми стандартами.

## Возможности
- Регистрация и авторизация пользователей.
- Поиск преподавателей по фильтрам.
- Планирование и назначение занятий.
- Редактирование профиля пользователя.
- Асинхронный чат для общения.
- Видеоконференции в реальном времени.
- Оплата занятий с комиссией 10%.

## Архитектура
Приложение построено на трехуровневой архитектуре:
- **База данных**: SQLite3 для хранения данных пользователей, занятий и сообщений.
- **Бизнес-логика**: Реализована на Python с использованием:
  - **Django**: Обработка HTTP-запросов.
  - **Django Channels**: Асинхронный чат и поддержка видеозвонков.
  - **WebRTC**: Потоковая передача видео в реальном времени.
- **Интерфейс**: Разработан с использованием HTML, CSS и JavaScript.

Для повышения производительности реализованы индексы, а для безопасности — проверки прав доступа.

## Технологии
- **Backend**: Python, Django, Django Channels, WebRTC.
- **Frontend**: HTML, CSS, JavaScript.
- **Database**: SQLite3.


## Установка и запуск
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/declare75/treaty.git
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
3. Запустите сервер
   ```bash
   daphne treatyproj.asgi:application

## Ограничения использования
Коммерческое использование проекта или присвоение его авторства запрещено. Такие действия могут нарушать права интеллектуальной собственности и подлежат ответственности в соответствии со Статьей 146 Уголовного кодекса Российской Федерации (Нарушение авторских и смежных прав).

## Контакты 
Если у вас есть вопросы или предложения, свяжитесь со мной: egmaxim343@gmail.com.
##
### Translation into English
# Tutor Web Application

"Tutor" is a modern web application designed for finding tutors, scheduling online lessons, and communicating via chat. The service provides a user-friendly interface, high performance, and security in line with industry standards.

## Features
- User registration and authentication.
- Tutor search with filters.
- Lesson scheduling and management.
- Profile editing.
- Asynchronous chat for communication.
- Real-time video conferencing.
- Lesson payments with a 10% commission.

## Architecture
The application is built on a three-tier architecture:
- **Database**: SQLite3 for storing user data, lessons, and messages.
- **Business Logic**: Implemented in Python using:
  - **Django**: Handling HTTP requests.
  - **Django Channels**: Asynchronous chat and video call support.
  - **WebRTC**: Real-time video streaming.
- **Interface**: Developed using HTML, CSS, and JavaScript.

Indexes are implemented for performance optimization, and access control checks ensure security.

## Technologies
- **Backend**: Python, Django, Django Channels, WebRTC.
- **Frontend**: HTML, CSS, JavaScript.
- **Database**: SQLite3.

## Installation and Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/declare75/treaty.git
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Run server:
   ```bash
   daphne treatyproj.asgi:application
## Usage Restrictions
Commercial use of the project or claiming its authorship is prohibited. Such actions may violate intellectual property rights and are subject to liability under Article 146 of the Criminal Code of the Russian Federation (Violation of Copyright and Related Rights).

## Contact
For questions or suggestions, feel free to reach out: egmaxim343@gmail.com.
