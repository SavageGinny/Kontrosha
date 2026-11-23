import re

class HTMLParser():

    def __init__(self, parsed_text):
        self.text = re.sub(
            r'<!--.*?-->',
            '',
            parsed_text,
            flags=re.DOTALL
        )
        self.tag_pattern = re.compile(
            r'<([a-zA-Z][\w:-]*)\b((?:[^>"\']|"[^"]*"|\'[^\']*\')*)>',
            re.DOTALL
        )

        self.attr_pattern = re.compile(
            r'([\w:-]+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))'
        )

    def get_attributes(self, tag_text):
        """Вспомогательный метод для извлечения атрибутов HTML-тега"""
        attributes = {}

        for match in self.attr_pattern.finditer(tag_text):
            name = match.group(1).lower()
            value = next(
                (group for group in match.groups()[1:] if group is not None),
                ""
            )

            attributes[name] = value

        return attributes

    def href_urls(self):
        """Извлечение всех URL из атрибутов href"""
        return sorted({
            attributes["href"]
            for match in self.tag_pattern.finditer(self.text)
            if (attributes := self.get_attributes(match.group(2))).get("href")
        })

    def src_urls(self):
        """Извлечение всех URL из атрибутов src"""
        return sorted({
            attributes["src"]
            for match in self.tag_pattern.finditer(self.text)
            if (attributes := self.get_attributes(match.group(2))).get("src")
        })

    def anchor_text(self):
        """Извлечение текста внутри тегов <a>"""
        pattern = re.compile(
            r'<a\b((?:[^>"\']|"[^"]*"|\'[^\']*\')*)>(.*?)</a\s*>',
            re.DOTALL | re.IGNORECASE
        )

        result = []

        for match in pattern.finditer(self.text):
            text = re.sub(r'<[^>]+>', '', match.group(2))
            text = re.sub(r'\s+', ' ', text).strip()

            if text:
                result.append(text)

        return result

    def classes(self):
        """Извлечение уникальных атрибутов class и их значений"""
        return sorted({
            (
                match.group(1).lower(),
                tuple(attributes["class"].split())
            )
            for match in self.tag_pattern.finditer(self.text)
            if (attributes := self.get_attributes(match.group(2))).get("class")
        })

    def meta_tags(self):
        """Извлечение мета-тегов description и keywords"""
        result = {}

        for match in self.tag_pattern.finditer(self.text):
            if match.group(1).lower() != "meta":
                continue

            attributes = self.get_attributes(match.group(2))

            name = attributes.get("name", "").lower()

            if name in ("description", "keywords"):
                result[name] = attributes.get("content", "")

        return result

    def data_attributes(self):
        """Извлечение всех атрибутов, начинающихся с data-"""
        result = []

        for match in self.tag_pattern.finditer(self.text):
            tag_name = match.group(1).lower()
            attributes = self.get_attributes(match.group(2))

            data = {
                name: value
                for name, value in attributes.items()
                if name.startswith("data-")
            }

            if data:
                result.append({
                    "tag": tag_name,
                    "attributes": data
                })

        return result

    def scripts_and_styles(self):
        """Извлечение CSS-стилей и JavaScript-скриптов"""
        styles = sorted({
            attributes["style"]
            for match in self.tag_pattern.finditer(self.text)
            if (attributes := self.get_attributes(match.group(2))).get("style")
        })

        script_pattern = re.compile(
            r'<script\b((?:[^>"\']|"[^"]*"|\'[^\']*\')*)>(.*?)</script\s*>',
            re.DOTALL | re.IGNORECASE
        )

        scripts = []

        for match in script_pattern.finditer(self.text):
            attributes = self.get_attributes(match.group(1))
            script = attributes.get("src") or match.group(2).strip()

            if script:
                scripts.append(script)

        scripts = list(dict.fromkeys(scripts))

        return {
            "styles": styles,
            "scripts": scripts
        }

    def contacts(self):
        """Поиск телефонных номеров и email в тексте"""
        text = re.sub(
            r'<(script|style)\b[^>]*>.*?</\1\s*>',
            ' ',
            self.text,
            flags=re.DOTALL | re.IGNORECASE
        )

        text = re.sub(r'<[^>]+>', ' ', text)

        email_pattern = (
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        )

        phone_pattern = r'(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)'

        emails = sorted(set(re.findall(email_pattern, text)))
        phones = sorted(set(re.findall(phone_pattern, text)))

        return {
            "emails": emails,
            "phones": phones
        }

    
    def all(self):
        """Общий метод для получения результатов всех заданий"""
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
