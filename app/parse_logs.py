import re
from collections import defaultdict


class LogsParser():

    def __init__(self, parsed_text):
        pattern = re.compile(
            r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+'
            r'-\s+(?P<user>\S+)\s+'
            r'\[[^\]]+\]\s+'
            r'"(?P<method>GET|POST|PUT|DELETE|PATCH)\s+'
            r'(?P<url>\S+)\s+HTTP/[^"]+"\s+'
            r'(?P<status>\d{3})\s+\d+\s+'
            r'"(?P<referer>[^"]*)"\s+'
            r'"(?P<agent>[^"]*)"'
        )
        self.records = [m.groupdict() for m in pattern.finditer(parsed_text)]

    def ips(self):
        """1. Извлечь IP-адресы всех запросов"""
        return sorted({r["ip"] for r in self.records})

    def users(self):
        """2. Найти аутентифицированных пользователей (имена в квадратных скобках)"""
        return sorted({r["user"] for r in self.records if r["user"] != "-"})

    def methods(self):
        """3. Извлечь методы HTTP-запросов (GET, POST, PUT, DELETE, PATCH)"""
        return sorted({r["method"] for r in self.records})

    def urls_with_query(self):
        """4. Найти URL с параметрами запроса (после ?)"""
        return sorted({
            r["url"] for r in self.records if "?" in r["url"]
        })

    def group(self):
        """5. Извлечь коды ответов и сгруппировать их по типам (2xx, 4xx, 5xx)"""
        status_groups = defaultdict(list)
        for record in self.records:
            status = record["status"]
            status_groups[f"{status[0]}xx"].append(status)

        return {
            group: f"{len(codes)} запрос(ов): {', '.join(codes)}"
            for group, codes in sorted(status_groups.items())
        }

    def agents(self):
        """6. Найти User-Agent строки браузеров и ботов"""
        user_agents = sorted({r["agent"] for r in self.records})
        browser_agents = [
            agent for agent in user_agents
            if not re.search(r"bot|crawler|spider|slurp", agent, re.I)
        ]
        bot_agents = [
            agent for agent in user_agents
            if re.search(r"bot|crawler|spider|slurp", agent, re.I)
        ]

        return {
            "browser_agents": browser_agents,
            "bot_agents": bot_agents
        }

    def referers(self):
        """7. Извлечь referer (источник перехода)"""
        return sorted({
            r["referer"] for r in self.records if r["referer"] != "-"
        })

    def api_requests(self):
        """8. Найти запросы к API (/api/v1/...)"""
        return sorted({
            r["url"] for r in self.records
            if re.match(r"^/api/v1(?:/|\?|$)", r["url"])
        })

    def all(self):

        return {
            "1. IP-адреса всех запросов": self.ips(),
            "2. Аутентифицированные пользователи": self.users(),
            "3. HTTP-методы": self.methods(),
            "4. URL с параметрами запроса": self.urls_with_query(),
            "5. Коды ответов по типам": self.group(),
            "6а. User-Agent браузеров": self.agents()["browser_agents"],
            "6б. User-Agent ботов": self.agents()["bot_agents"],
            "7. Referer": self.referers(),
            "8. Запросы к API (/api/v1/...)": self.api_requests(),
        }
