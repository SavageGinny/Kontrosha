import re


class DatabaseParser():

    def __init__(self, parsed_text):
        """ Регулярное выражение для извлечения полей CSV"""
        
        self.field_pattern = re.compile(
            r'"((?:[^"]|"")*)"(?:;|$)'
        )

        lines = [
            line.strip()
            for line in parsed_text.splitlines()
            if line.strip()
        ]

        self.headers = self.parse_line(lines[0]) if lines else []

        self.records = []

        for line in lines[1:]:
            values = self.parse_line(line)

            if len(values) == len(self.headers):
                self.records.append(dict(zip(self.headers, values)))


    def parse_line(self, line):
        """Вспомогательный метод для извлечения полей одной строки"""
        return [
            match.group(1).replace('""', '"')
            for match in self.field_pattern.finditer(line)
        ]


    def surnames(self):
        """Извлечение всех фамилий сотрудников"""
        return sorted({
            r["last_name"]
            for r in self.records
            if r.get("last_name")
        })

    def domain_emails(self):
        """Поиск email-адресов в определенном домене"""
        return sorted({
            r["email"]
            for r in self.records
            if re.fullmatch(
                r'[^@\s]+@company\.com',
                r.get("email", ""),
                re.IGNORECASE
            )
        })

    def phones(self):
        """Извлечение номеров телефонов"""
        return sorted({
            r["phone"]
            for r in self.records
            if re.fullmatch(
                r'\+?[\d\s().-]+',
                r.get("phone", "")
            )
        })


    def employees_by_department(self):
        """Поиск сотрудников определенного отдела"""
        departments = sorted({
            r["department"]
            for r in self.records
            if r.get("department")
        })

        return {
            department: [
                f'{r["last_name"]} {r["first_name"]} ({r["position"]})'
                for r in self.records
                if r.get("department") == department
            ]
            for department in departments
        }

    
    def skills(self):
        """Извлечение навыков и разделение их по запятым"""
        return {
            f'{r["last_name"]} {r["first_name"]}': [
                skill.strip()
                for skill in re.split(r'\s*,\s*', r.get("skills", ""))
                if skill.strip()
            ]
            for r in self.records
        }

    def high_salary(self):
        """Поиск сотрудников с зарплатой выше 150000"""
        return [
            f'{r["last_name"]} {r["first_name"]}: {r["salary"]}'
            for r in self.records
            if re.fullmatch(r'\d+(?:\.\d+)?', r.get("salary", ""))
            and float(r["salary"]) > 150000
        ]

    def hire_dates(self):
        """Извлечение дат приема на работу"""
        return {
            f'{r["last_name"]} {r["first_name"]}': r["hire_date"]
            for r in self.records
            if re.fullmatch(
                r'\d{4}-\d{2}-\d{2}',
                r.get("hire_date", "")
            )
        }

    
    def managers(self):
        """Поиск руководителей (manager_id = "NULL")"""
        return [
            f'{r["last_name"]} {r["first_name"]} ({r["position"]})'
            for r in self.records
            if re.fullmatch(
                r'NULL',
                r.get("manager_id", "").strip(),
                re.IGNORECASE
            )
        ]

    def all(self):
        return {
            "1. Фамилии сотрудников": self.surnames(),
            "2. Email на домене @company.com": self.domain_emails(),
            "3. Номера телефонов": self.phones(),
            "4. Сотрудники по отделам": self.employees_by_department(),
            "5. Навыки сотрудников (разделены по запятым)": self.skills(),
            "6. Сотрудники с зарплатой выше 150000": self.high_salary(),
            "7. Даты приема на работу": self.hire_dates(),
            '8. Руководители (manager_id = "NULL")': self.managers(),
        }
