import warnings

warnings.filterwarnings(action="ignore")

import json
import logging
import re
import time
from typing import List

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def set_chromedriver(path: str = "/usr/bin/chromedriver"):
    global driver
    # 크롬 드라이버 사용
    service = Service(executable_path=path)  # selenium 최근 버전은 이렇게 해야함.

    # 이런 것 때문에 기술문서를 보면서 코딩해야하고 영어도 잘해야함. (by. 스터디 팀장님)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options, service=service)


def convert_date(date):
    ymd, dn, hm = date.split(" ")
    ymd = ymd[:-1].replace(".", "-")
    hours = 12 if dn == "오후" else 0
    h = int(hm.split(":")[0]) + hours
    m = hm.split(":")[1]
    return f"{ymd} {h}:{m}"


def _get_class_info(
    driver,
    class_name,
):
    return driver.find_element(By.CLASS_NAME, class_name).text


def get_news_info(url: str, category: str):
    """
    Extract news information from URL with improved error handling.
    """
    driver.get(url)
    driver.implicitly_wait(5)

    # Regular expressions
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
    reporter_pattern = r"[ㄱ-힣]{2,4}"

    # Initialize default values
    title = ""
    content = ""
    press = "Unknown"
    date = ""
    reporter = "None"
    email = "None"

    try:
        if category in ["정치", "경제", "사회", "생활/문화", "IT/과학", "세계"]:
            # Regular news
            try:
                title = driver.find_element(By.CLASS_NAME, "media_end_head_title").text
                content = driver.find_element(By.CLASS_NAME, "_article_content").text

                # Reporter info
                try:
                    email_text = driver.find_element(By.CLASS_NAME, "byline").text
                    email_matches = re.findall(email_pattern, email_text)
                    reporter_matches = re.findall(reporter_pattern, email_text)

                    email = email_matches[0] if email_matches else "None"
                    reporter = reporter_matches[0] if reporter_matches else "None"
                except Exception as e:
                    logging.warning(f"Error extracting reporter info: {str(e)}")

                # Press info
                try:
                    press_element = driver.find_element(
                        By.CLASS_NAME, "media_end_head_top_logo_text"
                    )
                    press = press_element.get_attribute("alt") or "Unknown"
                except Exception as e:
                    logging.warning(f"Error extracting press info: {str(e)}")

                # Date info
                try:
                    date_results = driver.find_elements(
                        By.CLASS_NAME, "media_end_head_info_datestamp_bunch"
                    )
                    if len(date_results) > 1:
                        date = driver.find_element(
                            By.CLASS_NAME, "_ARTICLE_MODIFY_DATE_TIME"
                        ).get_attribute("data-modify-date-time")
                    else:
                        date = driver.find_element(
                            By.CLASS_NAME, "_ARTICLE_DATE_TIME"
                        ).get_attribute("data-date-time")
                except Exception as e:
                    logging.warning(f"Error extracting date: {str(e)}")
                    date = "Unknown"

            except Exception as e:
                logging.error(f"Error extracting regular news content: {str(e)}")
                raise

        elif category in ["스포츠", "연예"]:
            # Sports and Entertainment news
            class_dict = {
                "title": "NewsEndMain_article_head_title__ztaL4",
                "content": "_article_content",
                "email_reporter": "NewsEndMain_article_journalist_info__Cdr3D",
            }

            try:
                title = _get_class_info(driver, class_dict["title"])
                content = _get_class_info(driver, class_dict["content"])

                # Reporter info
                try:
                    email_text = driver.find_element(
                        By.CLASS_NAME, class_dict["email_reporter"]
                    ).text
                    email_matches = re.findall(email_pattern, email_text)
                    reporter_matches = re.findall(reporter_pattern, email_text)

                    email = email_matches[0] if email_matches else "None"
                    reporter = reporter_matches[0] if reporter_matches else "None"
                except Exception as e:
                    logging.warning(f"Error extracting reporter info: {str(e)}")

                # Category specific handling
                if category == "스포츠":
                    try:
                        press = (
                            driver.find_element(
                                By.CLASS_NAME,
                                "NewsEndMain_comp_article_main_news__0RmSO",
                            )
                            .find_element(
                                By.CLASS_NAME, "NewsEndMain_image_media__rTvT1"
                            )
                            .get_attribute("alt")
                        ) or "Unknown"

                        date_results = driver.find_elements(
                            By.CLASS_NAME, "NewsEndMain_date__xjtsQ"
                        )
                        date = (
                            date_results[1].text
                            if len(date_results) > 1
                            else date_results[0].text
                        )
                        date = convert_date(date)
                    except Exception as e:
                        logging.warning(
                            f"Error extracting sports specific info: {str(e)}"
                        )
                else:  # Entertainment
                    try:
                        press = (
                            driver.find_element(
                                By.CLASS_NAME, "NewsEndMain_highlight__HWvAi"
                            ).text
                            or "Unknown"
                        )

                        date_results = driver.find_elements(By.CLASS_NAME, "date")
                        date = (
                            date_results[1].text
                            if len(date_results) > 1
                            else date_results[0].text
                        )
                        date = convert_date(date)
                    except Exception as e:
                        logging.warning(
                            f"Error extracting entertainment specific info: {str(e)}"
                        )

            except Exception as e:
                logging.error(
                    f"Error extracting sports/entertainment content: {str(e)}"
                )
                raise

        # Validate required fields
        if not title or not content:
            raise ValueError("Required fields (title/content) missing")

        return {
            "title": title,
            "content": content,
            "press": press or "Unknown",
            "date": date or "Unknown",
            "reporter": reporter,
            "email": email,
        }

    except Exception as e:
        logging.error(f"Error processing URL {url}: {str(e)}")
        raise


def crawl(
    url: str, category: str = None, chromedriver_path: str = "/usr/bin/chromedriver"
):
    # Set up chrome driver and get info

    set_chromedriver(chromedriver_path)
    info = get_news_info(url, category)
    # logger.info(f"Crawl successful: {info}")/

    return info


# class URLExtractor:
#     def __init__(self, browser_type: str = "chrome"):
#         """
#         Initialize the URL extractor with specified browser.

#         Args:
#             browser_type (str): Type of browser to use ('chrome' or 'firefox')
#         """
#         self.setup_logging()
#         self.driver = self.setup_driver(browser_type)

#     def setup_logging(self):
#         """Configure logging settings"""
#         logging.basicConfig(
#             level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
#         )

#     def setup_driver(
#         self, browser_type: str = "chrome", path: str = "/usr/bin/chromedriver"
#     ):
#         """Set up and configure the WebDriver"""
#         try:
#             if browser_type.lower() == "chrome":
#                 # 크롬 드라이버 사용
#                 service = Service(
#                     executable_path=path
#                 )  # selenium 최근 버전은 이렇게 해야함.

#                 # 이런 것 때문에 기술문서를 보면서 코딩해야하고 영어도 잘해야함. (by. 스터디 팀장님)
#                 options = webdriver.ChromeOptions()
#                 options.add_argument("--headless")
#                 options.add_argument("--no-sandbox")
#                 options.add_argument("--disable-dev-shm-usage")
#                 return webdriver.Chrome(options=options, service=service)

#             elif browser_type.lower() == "firefox":
#                 options = webdriver.FirefoxOptions()
#                 options.add_argument("--headless")
#                 return webdriver.Firefox(options=options)
#             else:
#                 raise ValueError(f"Unsupported browser type: {browser_type}")
#         except Exception as e:
#             logging.error(f"Failed to initialize WebDriver: {str(e)}")
#             raise

#     # def click_load_more(self) -> bool:
#     #     try:
#     #         button = WebDriverWait(self.driver, 10).until(
#     #             EC.element_to_be_clickable((By.CSS_SELECTOR, "a.section_more_inner"))
#     #         )

#     #         self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
#     #         time.sleep(1)

#     #         try:
#     #             button.click()
#     #         except:
#     #             self.driver.execute_script("arguments[0].click();", button)

#     #         time.sleep(2)
#     #         return True

#     #     except Exception as e:
#     #         logging.info("No more content to load")
#     #         return False

#     def extract_urls(self, url: str, wait_time: int = 5) -> List[str]:
#         try:
#             self.driver.get(url)
#             logging.info("Navigated to the target URL")

#             # # Wait for initial content
#             # WebDriverWait(self.driver, wait_time).until(
#             #     EC.presence_of_element_located((By.CLASS_NAME, "sa_item"))
#             # )

#             # # Load all content
#             # while True:
#             #     initial_height = self.driver.execute_script(
#             #         "return document.body.scrollHeight"
#             #     )

#             #     if not self.click_load_more():
#             #         break

#             #     # Check if page height increased (new content loaded)
#             #     new_height = self.driver.execute_script(
#             #         "return document.body.scrollHeight"
#             #     )
#             #     if new_height <= initial_height:
#             #         break

#             # Extract URLs using specific selectors
#             urls = []

#             # Find all news article containers
#             article_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.sa_item")

#             logging.info(f"Found {len(article_elements)} articles")

#             for article in article_elements:
#                 # Get URL from either thumbnail or title link
#                 links = article.find_elements(
#                     By.CSS_SELECTOR, "a.sa_thumb_link, a.sa_text_title"
#                 )

#                 for link in links:
#                     href = link.get_attribute("href")
#                     if href and "news.naver.com/mnews/article" in href:
#                         urls.append(href)
#                         break  # Only take one URL per article

#             unique_urls = list(dict.fromkeys(urls))
#             logging.info(
#                 f"Successfully extracted {len(unique_urls)} unique article URLs"
#             )

#             return unique_urls

#         except Exception as e:
#             logging.error(f"Error extracting URLs: {str(e)}")
#             return []

#     def close(self):
#         if self.driver:
#             self.driver.quit()
#             logging.info("WebDriver closed successfully")


class URLExtractor:
    # URL patterns for different sections
    URL_PATTERNS = {
        "news": r"https://news\.naver\.com/section/\d+",
        "entertainment": r"https://entertain\.naver\.com/now",
        "sports": r"https://sports\.news\.naver\.com/\w+/news/index\?isphoto=N",
    }

    def __init__(self, browser_type: str = "chrome"):
        self.setup_logging()
        self.driver = self.setup_driver(browser_type)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def setup_driver(
        self, browser_type: str = "chrome", path: str = "/usr/bin/chromedriver"
    ):
        try:
            if browser_type.lower() == "chrome":
                service = Service(executable_path=path)
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                return webdriver.Chrome(options=options, service=service)
            elif browser_type.lower() == "firefox":
                options = webdriver.FirefoxOptions()
                options.add_argument("--headless")
                return webdriver.Firefox(options=options)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

    def detect_url_type(self, url: str) -> str:
        """Detect the type of URL based on patterns"""
        for url_type, pattern in self.URL_PATTERNS.items():
            if re.match(pattern, url):
                return url_type
        raise ValueError(f"URL does not match any known pattern: {url}")

    def extract_urls_news(self, url: str, count_clicks: int = 3) -> List[str]:
        """Extract URLs from news section"""
        try:
            self.driver.get(url)
            meta_element = self.driver.find_element(
                By.CSS_SELECTOR,
                "#newsct > div.section_latest > div > div.section_latest_article._CONTENT_LIST._PERSIST_META",
            )

            urls = []
            click_count = 0

            # Initial articles
            article_links = self.driver.find_elements(
                By.CSS_SELECTOR, "a.sa_text_title._NLOG_IMPRESSION"
            )
            for link in article_links:
                href = link.get_attribute("href")
                if href and "news.naver.com/mnews/article" in href:
                    urls.append(href)

            # Click "더보기" button specified number of times
            while click_count < count_clicks:
                try:
                    button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (
                                By.CSS_SELECTOR,
                                "a.section_more_inner._CONTENT_LIST_LOAD_MORE_BUTTON",
                            )
                        )
                    )
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(2)

                    # Get new articles
                    article_links = self.driver.find_elements(
                        By.CSS_SELECTOR, "a.sa_text_title._NLOG_IMPRESSION"
                    )
                    for link in article_links:
                        href = link.get_attribute("href")
                        if href and "news.naver.com/mnews/article" in href:
                            urls.append(href)

                    click_count += 1
                except Exception as e:
                    logging.error(f"Error clicking more button: {str(e)}")
                    break

            return list(dict.fromkeys(urls))
        except Exception as e:
            logging.error(f"Error in news extraction: {str(e)}")
            return []

    def extract_urls_entertainment(self, url: str) -> List[str]:
        """Extract URLs from entertainment section"""
        try:
            self.driver.get(url)
            urls = []

            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#newsWrp ul"))
            )
            time.sleep(2)

            # Get articles using the exact querySelector path
            article_links = self.driver.find_elements(
                By.CSS_SELECTOR, "#newsWrp > ul > li > div > a"
            )

            for link in article_links:
                href = link.get_attribute("href")
                if href:
                    urls.append(href)

            logging.info(f"Found {len(urls)} entertainment URLs")
            return list(dict.fromkeys(urls))
        except Exception as e:
            logging.error(f"Error in entertainment extraction: {str(e)}")
            return []

    def extract_urls_sports(self, url: str) -> List[str]:
        """Extract URLs from sports section"""
        try:
            self.driver.get(url)
            urls = []

            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.news_list"))
            )
            time.sleep(2)

            # Get articles
            article_links = self.driver.find_elements(
                By.CSS_SELECTOR, "div.news_list a.title"
            )

            for link in article_links:
                href = link.get_attribute("href")
                if href:
                    urls.append(href)

            return list(dict.fromkeys(urls))
        except Exception as e:
            logging.error(f"Error in sports extraction: {str(e)}")
            return []

    def extract_urls(self, url: str, count_clicks: int = 3) -> List[str]:
        """Main method to extract URLs based on URL pattern"""
        url_type = self.detect_url_type(url)
        logging.info(f"Detected URL type: {url_type}")

        if url_type == "news":
            return self.extract_urls_news(url, count_clicks)
        elif url_type == "entertainment":
            return self.extract_urls_entertainment(url)
        elif url_type == "sports":
            return self.extract_urls_sports(url)
        else:
            raise ValueError(f"Unsupported URL type: {url_type}")

    def __del__(self):
        """Clean up WebDriver when done"""
        if hasattr(self, "driver"):
            self.driver.quit()
