# Data Parser — FastAPI

## Запуск

1. Создайте виртуальное окружение (необязательно, но рекомендуется):

   ```bash
   python -m venv .venv
   ```

2. Активируйте его:

   Windows:
   ```bash
   .venv\\Scripts\\activate
   ```

   Linux / macOS:
   ```bash
   source .venv/bin/activate
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Запустите приложение из корневой папки проекта:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Откройте в браузере http://127.0.0.1:8000

## Структура

- `app/main.py` — маршруты FastAPI и запуск парсеров.
- `app/parse_*.py` — классы парсеров.
- `app/templates/` — HTML-шаблоны страниц.
- `app/static/style.css` — оформление.
- `data/` — исходные файлы для анализа.

## Замена исходных файлов

Пути задаются в словаре `SOURCE_FILES` в `app/main.py`.
Если заменяете исходники, сохраните имена файлов или измените соответствующие пути.
