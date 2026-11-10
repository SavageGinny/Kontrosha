from pathlib import Path


def read_file(path):
    """Читает текстовый файл. Пробует несколько распространённых кодировок."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Файл не найден: {path}")

    for encoding in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise UnicodeError(f"Не удалось определить кодировку файла: {path}")


def show(title, data):
    """Формирует блок результатов."""
    lines = [f"\n{'=' * 75}", title, "=" * 75]

    if data is None:
        lines.append("Ничего не найдено.")
    elif isinstance(data, dict):
        if not data:
            lines.append("Ничего не найдено.")
        else:
            for key, value in data.items():
                lines.append(f"\n{key}:")
                if isinstance(value, (list, tuple, set)):
                    if value:
                        lines.extend(f"  - {item}" for item in value)
                    else:
                        lines.append("  Ничего не найдено.")
                else:
                    lines.append(f"  {value}")
    elif isinstance(data, (list, tuple, set)):
        if data:
            lines.extend(f"- {item}" for item in data)
        else:
            lines.append("Ничего не найдено.")
    else:
        lines.append(str(data))

    return "\n".join(lines)