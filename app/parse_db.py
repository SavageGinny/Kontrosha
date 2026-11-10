
import csv


class DatabaseParser():

    def __init__(self, parsed_text):
        reader = csv.DictReader(
            parsed_text.splitlines(),
            delimiter=";",
            quotechar='"'
        )

        self.records = list(reader)

    def surnames(self):
        """1. Извлечь все фамилии сотрудников"""
        return sorted({
            r["last_name"] for r in self.records
            if r.get("last_name")
        })

    
    def domain_emails(self):
        """2. Найти email-адреса в определенном домене"""
        return sorted({
            r["email"] for r in self.records
            if r.get("email", "").lower().endswith("@company.com")
        })

    def phones(self):
        """3. Извлечь номера телефонов"""
        return sorted({
            r["phone"] for r in self.records
            if r.get("phone")
        })

    def employees_by_department(self):
        """4. Найти сотрудников определенного отдела"""
        departments = sorted({
            r["department"] for r in self.records
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
        """5. Извлечь навыки (skills) и разбить их по запятым"""
        return {
            f'{r["last_name"]} {r["first_name"]}': [
                skill.strip()
                for skill in r.get("skills", "").split(",")
                if skill.strip()
            ]
            for r in self.records
        }

    def high_salary(self):
        """6. Найти сотрудников с зарплатой выше 150000"""
        return [
            f'{r["last_name"]} {r["first_name"]}: {r["salary"]}'
            for r in self.records
            if r.get("salary") and float(r["salary"]) > 150000
        ]

    # 
    def hire_dates(self):
        """7. Извлечь даты приема на работу"""
        return {
            f'{r["last_name"]} {r["first_name"]}': r["hire_date"]
            for r in self.records
            if r.get("hire_date")
        }

    # 
    def managers(self):
        """8. Найти руководителей (где manager_id = "NULL")"""
        return [
            f'{r["last_name"]} {r["first_name"]} ({r["position"]})'
            for r in self.records
            if r.get("manager_id", "").strip().upper() == "NULL"
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
