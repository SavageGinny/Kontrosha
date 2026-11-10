from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .filer import read_file
from .parse_logs import LogsParser
from .parse_config import ConfigParser
from .html_parser import HTMLParser
from .parse_db import DatabaseParser


# Корневая папка проекта: находим её относительно этого файла,
# поэтому приложение можно запускать из любой рабочей директории.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Пути к исходным файлам. При необходимости их можно поменять здесь.
SOURCE_FILES = {
    "logs": DATA_DIR / "logs.txt",
    "config": DATA_DIR / "config.txt",
    "html": DATA_DIR / "index.html",
    "database": DATA_DIR / "database.csv",
}

PARSERS = {
    "logs": {
        "title": "Логи веб-сервера",
        "subtitle": "HTTP-запросы, пользователи, статусы и User-Agent",
        "description": "Разбор access-логов веб-сервера.",
        "class": LogsParser,
        "icon": "⌁",
        "color": "blue",
    },
    "config": {
        "title": "Конфигурационный файл",
        "subtitle": "Секции, параметры, секреты и версии",
        "description": "Извлечение настроек из конфигурации.",
        "class": ConfigParser,
        "icon": "⚙",
        "color": "violet",
    },
    "html": {
        "title": "HTML-документ",
        "subtitle": "Ссылки, атрибуты, метаданные и контакты",
        "description": "Анализ HTML-страницы с помощью BeautifulSoup.",
        "class": HTMLParser,
        "icon": "</>",
        "color": "orange",
    },
    "database": {
        "title": "Выгрузка из базы данных",
        "subtitle": "Сотрудники, отделы, зарплаты и навыки",
        "description": "Обработка CSV-выгрузки сотрудников.",
        "class": DatabaseParser,
        "icon": "▦",
        "color": "green",
    },
}

app = FastAPI(
    title="Data Parser",
    description="Учебное приложение для просмотра результатов парсинга.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")


def get_parser_result(key: str):
    """Открывает исходный файл и запускает соответствующий парсер."""
    config = PARSERS[key]
    file_path = SOURCE_FILES[key]

    if not file_path.is_file():
        raise FileNotFoundError(f"Исходный файл не найден: {file_path}")

    source_text = read_file(file_path)
    parser = config["class"](source_text)
    return parser.all(), source_text


def count_items(value):
    """Подсчитывает количество элементов для небольшой сводки."""
    if isinstance(value, dict):
        return sum(count_items(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return len(value)
    return 1 if value not in (None, "") else 0


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    cards = []
    for key, config in PARSERS.items():
        file_path = SOURCE_FILES[key]
        cards.append({
            "key": key,
            **config,
            "filename": file_path.name,
            "exists": file_path.is_file(),
        })

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"cards": cards, "active": "home"},
    )


@app.get("/parser/{parser_key}", response_class=HTMLResponse)
async def parser_page(request: Request, parser_key: str):
    if parser_key not in PARSERS:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "Раздел не найден",
                "message": "Такого парсера нет в приложении.",
                "active": "",
            },
            status_code=404,
        )

    config = PARSERS[parser_key]
    file_path = SOURCE_FILES[parser_key]

    try:
        results, source_text = get_parser_result(parser_key)
        error = None
        total = sum(count_items(value) for value in results.values())
        source_size = len(source_text)
    except Exception as exc:
        results = {}
        error = str(exc)
        total = 0
        source_size = 0

    return templates.TemplateResponse(
        request=request,
        name="results.html",
        context={
            "key": parser_key,
            "config": config,
            "results": results,
            "error": error,
            "total": total,
            "source_size": source_size,
            "filename": file_path.name,
            "active": parser_key,
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
