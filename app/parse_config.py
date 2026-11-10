import re


class ConfigParser():

    def __init__(self, parsed_text):
        """
        1. Извлечь названия всех секций (в квадратных скобках)
        +
        инциализирует класс. Сделал так, так как pairs используется во многих заданиях
        """
        self.parsed_text = parsed_text

        self.pairs = {}
        for line in self.parsed_text.splitlines():
            line = line.strip()
            if not line or line.startswith(";") or line.startswith("["):
                continue
            match = re.match(r"^([A-Za-z_][\w.-]*)\s*=\s*(.*?)\s*$", line)
            if match:
                self.pairs[match.group(1)] = match.group(2).strip().strip('"')

    def sections(self):
        """2. Найти все пары "ключ = значение"""
        return re.findall(r"^\s*\[([^\]]+)\]\s*$", self.parsed_text, re.M)

    def secret_values(self):
        """3. Извлечь значения для конкретных ключей (пароли, API-ключи)"""
        return {
            key: value for key, value in self.pairs.items()
            if re.search(r"password|secret|api[_-]?key|token", key, re.I)
        }

    def comments(self):
        """4. Найти закомментированные строки (начинающиеся с ;)"""
        return [
            line.strip() for line in self.parsed_text.splitlines()
            if line.strip().startswith(";")
        ]

    def versions(self):
        """5. Извлечь версии программного обеспечения"""
        return {
            key: value for key, value in self.pairs.items()
            if "version" in key.lower()
            or re.fullmatch(r"\d+\.\d+(?:\.\d+)?", value)
        }

    def database_settings(self):
        """6. Найти настройки, связанные с базами данных"""
        return {
            key: value for key, value in self.pairs.items()
            if re.search(r"database|(^|_)db(_|$)|postgres|mysql|mongo|sql|replica|primary_host", key, re.I)
        }
    
    def external_urls(self):
        """7.	Извлечь URL внешних сервисов"""
        return {
            key: value for key, value in self.pairs.items()
            if re.match(r"https?://", value, re.I)
        }

    def numeric_values(self):
        """8.A Найти числовые значения"""
        return {
            key: value for key, value in self.pairs.items()
            if re.fullmatch(r"-?\d+(?:\.\d+)?", value)
        }

    def numeric_ranges(self):
        """8.Б Найти числовые диапозоны"""
        return re.findall(
            r"(?<![\w.])-?\d+(?:\.\d+)?\s*(?:-|–|—|до)\s*-?\d+(?:\.\d+)?",
            self.parsed_text,
            re.I,
        )

    def all(self):

        return {
            "1. Названия секций": self.sections(),
            "2. Все пары «ключ = значение»": {
                key: value for key, value in self.pairs.items()
            },
            "3. Пароли, API-ключи и другие секреты": self.secret_values(),
            "4. Закомментированные строки": self.comments(),
            "5. Версии программного обеспечения": self.versions(),
            "6. Настройки баз данных": self.database_settings(),
            "7. URL внешних сервисов": self.external_urls(),
            "8а. Числовые значения": self.numeric_values(),
            "8б. Числовые диапазоны": self.numeric_ranges(),
        }