from time import sleep
import re
import scrapy
from selenium import webdriver
from typing import Generator
from scrapy.http import Response, HtmlResponse
from datetime import datetime, timedelta


class RobotaSpider(scrapy.Spider):
    name = "robota"
    allowed_domains = ["robota.ua"]
    start_urls = ["https://robota.ua/ru/zapros/python/ukraine"]

    ROLES = {
        "Python Developer": [
            "Python Developer", "Розробник Python", "Разработчик Python", "Python-програміст", "Python Engineer",
            "Developer Python", "Разработка на Python", "Python програмист"
        ],
        "Data Analyst": [
            "Data Analyst", "Аналітик", "Аналитик", "Дата аналітик", "Аналітик даних", "Аналитик данных",
            "Data Analytics", "Аналитик по данным", "Аналітик даних"
        ],
        "Data Scientist": [
            "Data Scientist", "Науковець з даних", "Ученый данных", "Scientist Data", "Data Researcher",
            "Специалист по данным", "Фахівець з даних"
        ],
        "Machine Learning Engineer": [
            "Machine Learning Engineer", "Інженер з машинного навчання", "Инженер машинного обучения",
            "ML Engineer", "Специалист по машинному обучению", "Фахівець з машинного навчання"
        ],
        "Backend Developer": [
            "Backend Developer", "Розробник бекенда", "Разработчик бекенда", "Backend Engineer",
            "Backend программист", "Програміст бекенду"
        ],
        "Full Stack Developer": [
            "Full Stack Developer", "Розробник повного стека", "Разработчик полного стека", "Fullstack Developer",
            "Full Stack Engineer", "Fullstack програміст"
        ],
        "Technical Support": [
            "Technical Support", "Технічна підтримка", "Техническая поддержка", "Support Engineer",
            "Техподдержка", "Спеціаліст з підтримки"
        ],
        "Game Mathematician": [
            "Game Mathematician", "Математик игры", "Гейм-математик", "Спеціаліст з ігрової математики",
            "Игровой математик", "Математик геймдизайну"
        ],
        "Data Engineer": [
            "Data Engineer", "Інженер з даних", "Инженер данных", "Data Infrastructure Engineer",
            "Инженер по данным", "Інженер інфраструктури даних"
        ],
        "DevOps Engineer": [
            "DevOps Engineer", "Інженер DevOps", "Инженер DevOps", "DevOps специалист", "Спеціаліст DevOps",
            "DevOps Архітектор"
        ],
        "Software Engineer": [
            "Software Engineer", "Програміст", "Программист", "Розробник ПЗ", "Software Developer",
            "Software Specialist", "Фахівець з ПЗ"
        ],
        "Research Engineer": [
            "Research Engineer", "Інженер-дослідник", "Инженер-исследователь", "Науковий інженер",
            "Research Specialist", "Фахівець-дослідник"
        ],
        "System Architect": [
            "System Architect", "Архітектор систем", "Архитектор систем", "Системний архітектор",
            "Системный архитектор", "Solution Architect"
        ],
        "Cloud Engineer": [
            "Cloud Engineer", "Інженер хмарних технологій", "Инженер облачных технологий",
            "Cloud Specialist", "Фахівець з хмарних систем", "Специалист по облачным технологиям"
        ],
        "Data Architect": [
            "Data Architect", "Архітектор даних", "Архитектор данных", "Architect Data",
            "Архитектор по данным", "Фахівець з архітектури даних"
        ],
        "Solution Architect": [
            "Solution Architect", "Архітектор рішень", "Архитектор решений", "Solution Engineer",
            "Архітектор бізнес-рішень", "Спеціаліст з архітектури рішень"
        ],
        "Security Engineer": [
            "Security Engineer", "Інженер з безпеки", "Инженер по безопасности", "Security Specialist",
            "Фахівець з кібербезпеки", "Специалист по безопасности"
        ],
        "Network Engineer": [
            "Network Engineer", "Інженер мережі", "Сетевой инженер", "Network Specialist",
            "Фахівець з мереж", "Специалист по сетям"
        ],
        "AI Engineer": [
            "AI Engineer", "Інженер зі штучного інтелекту", "Инженер по искусственному интеллекту",
            "Artificial Intelligence Engineer", "Фахівець зі штучного інтелекту", "AI Developer"
        ],
        "Mentor": [
            "викладач", "преподаватель", "teacher", "instructor", "ментор", "наставник", "mentor", "Mentor"
        ]
    }

    ROLE_LEVELS = {
        "Intern": ["Intern", "Стажер", "Стажування", "Интерн", "Trainee", "Початківець"],
        "Junior": ["Junior", "Младший", "Молодший", "Джуніор", "Джун", "Junior Developer", "Начинающий"],
        "Middle": ["Middle", "Средний", "Середній", "Мідл", "Mid-level", "Middle Developer"],
        "Senior": ["Senior", "Старший", "Сеньор", "Сеньйор", "Senior Developer", "Ведущий", "Lead", "Experienced"],
        "Lead": ["Lead", "Лід", "Ведущий", "Head", "Team Lead", "Тимлид"],
        "Principal": ["Principal", "Главный", "Провідний", "Principal Engineer", "Principal Developer"],
        "Mentor": ["Mentor", "Наставник", "Ментор", "Инструктор", "Instructor"],
    }

    SKILLS = [
        "Python", "WSL", "SQL", "REST", "API", "Docker", "Linux", "Django", "Postrgresql", "Artificial Learning",
        "Js", "Machine Learning", "React", "OOP", "Flask", "NoSQL", "networking", "HTML", "CSS", "DRF", "FastAPI",
        "FullStack", "asyncio", "GraphQL", "algorithms", "MongoDB", "microservice", "Tableau"
    ]

    CITIES = {
        "Kyiv": ["Киев", "Київ"],
        "Lviv": ["Львов", "Львів"],
        "Kharkiv": ["Харьков", "Харків"],
        "Dnipro": ["Днепр", "Дніпро"],
        "Odesa": ["Одесса", "Одеса"],
        "Ivano-Frankivsk": ["Ивано-Франковск", "Івано-Франківськ"],
        "Vinnytsia": ["Винница", "Вінниця"],
        "Ternopil": ["Тернополь", "Тернопіль"],
        "Chernivtsi": ["Черновцы", "Чернівці"],
        "Sumy": ["Сумы", "Суми"],
        "Rivne": ["Ровно", "Рівне", "Ровно, Ровенская область"],
        "Lutsk": ["Луцк", "Луцьк"],
        "Poltava": ["Полтава"],
        "Chernihiv": ["Чернигов", "Чернігів"],
        "Kropyvnytskyi": ["Кропивницкий", "Кропивницький"],
        "Zhytomyr": ["Житомир"],
        "Uzhhorod": ["Ужгород"],
        "Cherkasy": ["Черкассы", "Черкаси"],
        "Kryvyi Rih": ["Кривой Рог", "Кривий Ріг"],
        "Mykolaiv": ["Николаев", "Миколаїв"],
        "Mariupol": ["Мариуполь", "Маріуполь"],
        "Zaporizhzhia": ["Запорожье", "Запоріжжя"],
        "Kremenchuk": ["Кременчуг", "Кременчук"],
        "Bila Tserkva": ["Белая Церковь", "Біла Церква"],
        "Uman": ["Умань"],
        "Irpin": ["Ирпень", "Ірпінь"],
        "Vyshhorod": ["Вышгород", "Вишгород"],
        "Sloviansk": ["Славянск", "Слов'янськ"],
        "Brovary": ["Бровары", "Бровари"],
        "Kovel": ["Ковель"],
        "Khmelnitskyi": ["Хмельницкий", "Хмельницький"],
        "Mukachevo": ["Мукачево"],
        "Konotop": ["Конотоп"],
        "Drohobych": ["Дрогобыч", "Дрогобич"],
        "Morshyn": ["Моршин"],

        "Warsaw": ["Варшава", "Warszawa"],
        "Krakow": ["Краков", "Kraków"],
        "Wroclaw": ["Вроцлав", "Wrocław"],
        "Gdansk": ["Гданьск", "Gdańsk"],
        "Poznan": ["Познань", "Poznań"],
        "Lublin": ["Люблин", "Lublin"],
        "Katowice": ["Катовице", "Katowice"],
        "Lodz": ["Лодзь", "Łódź"],
        "Szczecin": ["Щецин", "Szczecin"],
        "Rzeszow": ["Жешув", "Rzeszów"],
        "Bydgoszcz": ["Быдгощ", "Bydgoszcz"],
        "Bialystok": ["Белосток", "Białystok"],
        "Opole": ["Ополе", "Opole"],
        "Tychy": ["Тыхы", "Tychy"],
        "Zielona Gora": ["Зелена Гура", "Zielona Góra"],
        "Gliwice": ["Гливице", "Gliwice"],
        "Gdynia": ["Гдыня", "Gdynia"],
        "Torun": ["Торунь", "Toruń"]
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: any) -> None:
        self.driver.quit()

    @staticmethod
    def calculate_date(publish_time: str) -> str:
        now = datetime.now()
        match = re.search(r"(\d+)\s*(день|дня|дней|дні|днів|час|часа|година|години|неделя|недели|тиждень|тижні|месяц|місяць)", publish_time)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            if "день" in unit:
                return (now - timedelta(days=value)).strftime("%Y-%m-%d")
            elif "час" in unit:
                return (now - timedelta(hours=value)).strftime("%Y-%m-%d")
            elif "неделя" in unit or "тиждень" in unit:
                return (now - timedelta(weeks=value)).strftime("%Y-%m-%d")
            elif "месяц" in unit or "місяць" in unit:
                return (now - timedelta(days=value * 30)).strftime("%Y-%m-%d")
        return "No information"

    @staticmethod
    def detect_experience_level(description: str, title_text: str) -> str:
        if not description and not title_text:
            return "No information"

        for role, translations in RobotaSpider.ROLE_LEVELS.items():
            if any(translation.lower() in title_text.lower() for translation in translations):
                return role

        match = re.search(r"досвід.*?(\d+)\s*(рік|роки|років|год|года|лет)", description, re.IGNORECASE)
        if match:
            years_of_experience = int(match.group(1))
            if years_of_experience < 2:
                return "Junior"
            elif 2 <= years_of_experience < 5:
                return "Middle"
            else:
                return "Senior"
        return "No information"

    @staticmethod
    def detect_skills(description: str) -> str:
        return ", ".join([skill for skill in RobotaSpider.SKILLS if re.search(rf'\b{skill}\b', description, re.IGNORECASE)])

    @staticmethod
    def clean_title(title: str) -> str:
        if not title:
            return "No information"

        for role, translations in RobotaSpider.ROLES.items():
            if any(translation.lower() in title.lower() for translation in translations):
                return role

        return "No information"

    @staticmethod
    def translate_city(city: str) -> str:
        for english_city, city_variants in RobotaSpider.CITIES.items():
            if city in city_variants:
                return english_city
        return "No information"

    def parse(self, response: scrapy.http.Response, **kwargs: any) -> Generator[scrapy.Request, None, None]:
        self.driver.get(response.url)
        sleep(5)

        selenium_response = HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding="utf-8")

        for vacancy in selenium_response.css("a.card::attr(href)"):
            detail_url = vacancy.get()
            self.log(f"Found vacancy URL: {detail_url}")
            yield selenium_response.follow(detail_url, callback=self.parse_vacancy_info)

        next_page = selenium_response.css("a.side-btn.next::attr(href)").get()
        if next_page:
            self.log(f"Found next page URL: {next_page}")
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

    def parse_vacancy_info(self, response: Response) -> Generator[dict, None, None]:
        self.driver.get(response.url)
        sleep(0.5)

        selenium_response = HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding="utf-8")

        title = selenium_response.css("h1[data-id='vacancy-title']::text").get()
        company = selenium_response.css("a[target='_blank'] > span::text").get()
        location_city = selenium_response.css("span[data-id='vacancy-city']::text").get()
        experience_text = selenium_response.css(".full-desc").get()
        date_posted_text = selenium_response.css("span.santa-typo-regular.santa-whitespace-nowrap::text").get()
        technologies = selenium_response.css(".full-desc").get()

        yield {
            "title": self.clean_title(title).strip() if title else "No information",
            "company": company.strip() if company else "No information",
            "location": self.translate_city(location_city.strip()) if location_city else "No information",
            "experience": self.detect_experience_level(experience_text, title).strip() if experience_text else "No information",
            "technologies": self.detect_skills(technologies).strip(),
            "date_posted": self.calculate_date(date_posted_text).strip() if date_posted_text else "No information",
        }
