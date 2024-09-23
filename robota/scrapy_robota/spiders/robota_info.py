import json
import re
from time import sleep
from datetime import datetime, timedelta
from typing import Generator

import scrapy
from scrapy.http import Response, HtmlResponse
from selenium import webdriver

SKILLS_PATH = "../robota/scrapy_robota/skills.json"
ROLES_PATH = "../robota/scrapy_robota/roles.json"
ROLE_LEVELS_PATH = "../robota/scrapy_robota/role_levels.json"
CITIES_PATH = "../robota/scrapy_robota/cities.json"


def load_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


SKILLS = load_json_file(SKILLS_PATH)
ROLES = load_json_file(ROLES_PATH)
ROLE_LEVELS = load_json_file(ROLE_LEVELS_PATH)
CITIES = load_json_file(CITIES_PATH)


class RobotaSpider(scrapy.Spider):
    name = "robota"
    allowed_domains = ["robota.ua"]
    start_urls = ["https://robota.ua/ru/zapros/python/ukraine"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: any) -> None:
        self.driver.quit()

    @staticmethod
    def calculate_date(publish_time: str) -> str:
        now = datetime.now()
        match = re.search(
            r"(\d+)\s*(день|дня|дней|дні|днів|час|часа|година|години|неделя|недели|тиждень|тижні|месяц|місяць)",
            publish_time
        )
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
        for role, translations in ROLE_LEVELS.items():
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
        return ", ".join([skill for skill in SKILLS if re.search(rf'\b{skill}\b', description, re.IGNORECASE)])

    @staticmethod
    def clean_title(title: str) -> str:
        for role, translations in ROLES.items():
            if any(translation.lower() in title.lower() for translation in translations):
                return role

        return "No information"

    @staticmethod
    def translate_city(city: str) -> str:
        for english_city, city_variants in CITIES.items():
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
            "title": (
                self.clean_title(title).strip() if title else "No information"
            ),
            "company": (
                company.strip() if company else "No information"
            ),
            "location": (
                self.translate_city(location_city.strip()) if location_city else "No information"
            ),
            "experience": (
                self.detect_experience_level(experience_text, title).strip() if experience_text else "No information"
            ),
            "technologies": (
                self.detect_skills(technologies).strip()
            ),
            "date_posted": (
                self.calculate_date(date_posted_text).strip() if date_posted_text else "No information"
            ),
        }
