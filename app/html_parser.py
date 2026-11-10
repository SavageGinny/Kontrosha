
import re
from bs4 import BeautifulSoup


class HTMLParser():

    def __init__(self, parsed_text):

        self.soup = BeautifulSoup(parsed_text, "html.parser")
        self.text = self.soup.get_text(separator=" ", strip=True)


    def href_urls(self):
        """1. Извлечение всех URL из атрибутов href"""
        return sorted({
            tag["href"]
            for tag in self.soup.find_all(href=True)
        })

    def src_urls(self):
        """2. Извлечение всех URL из атрибутов src"""
        return sorted({
            tag["src"]
            for tag in self.soup.find_all(src=True)
        })


    def anchor_text(self):
        """3. Извлечение текста внутри тегов <a> (анкоры ссылок)"""
        return [
            tag.get_text(" ", strip=True)
            for tag in self.soup.find_all("a")
            if tag.get_text(strip=True)
        ]

    def classes(self):
        """4. Извлечение уникальных атрибутов class и их значений"""
        return sorted({
            (tag.name, tuple(tag.get("class")))
            for tag in self.soup.find_all(class_=True)
        })

    def meta_tags(self):
        """5. Извлечение мета-тегов (description и keywords)"""
        result = {}

        for tag in self.soup.find_all("meta"):
            name = tag.get("name", "").lower()

            if name in ("description", "keywords"):
                result[name] = tag.get("content", "")

        return result


    def data_attributes(self):
        """6. Извлечение всех атрибутов, начинающихся с (data-*)"""
        result = []

        for tag in self.soup.find_all(True):

            data = {
                name: value
                for name, value in tag.attrs.items()
                if name.startswith("data-")
            }

            if data:
                result.append({
                    "tag": tag.name,
                    "attributes": data
                })

        return result

    def scripts_and_styles(self):
        """7. Извлечение CSS-стилей и JavaScript-скриптов"""

        # Извлекаем уникальные значения атрибутов style.
        styles = sorted({
            tag["style"]
            for tag in self.soup.find_all(style=True)
        })

        # Извлекаем внешние скрипты и содержимое встроенных.
        scripts = list(dict.fromkeys(
            tag.get("src") or tag.get_text(strip=True)
            for tag in self.soup.find_all("script")
            if tag.get("src") or tag.get_text(strip=True)
        ))

        return {
            "styles": styles,
            "scripts": scripts
        }
    def contacts(self):
        """8. Поиск телефонных номеров и email в тексте"""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        phone_pattern = r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)"
        emails = sorted(set(re.findall(email_pattern, self.text)))
        phones = sorted(set(re.findall(phone_pattern, self.text)))
        return {
            "emails": emails,
            "phones": phones
        }

    def all(self):
        return {
            "1. URL из атрибутов href": self.href_urls(),
            "2. URL из атрибутов src": self.src_urls(),
            "3. Текст внутри тегов <a>": self.anchor_text(),
            "4. Атрибуты class и их значения": self.classes(),
            "5. Мета-теги description и keywords": self.meta_tags(),
            "6. Атрибуты data-*": self.data_attributes(),
            "7. Содержимое тегов <script> и <style>": self.scripts_and_styles(),
            "8. Телефоны и email": self.contacts()
        }
