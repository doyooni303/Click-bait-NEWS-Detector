import warnings

warnings.filterwarnings(action="ignore")

import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


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


def get_news_info(
    url: str,
    category: str,
):
    driver.get(url)

    driver.implicitly_wait(
        2
    )  # 2초 안에 웹페이지를 load하면 바로 넘어가거나, 2초를 기다림
    # 사전 준비
    email_pattern = (
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"  # 이메일 정규표현식
    )
    reporter_pattern = r"[ㄱ-힣]{2,4}"  # 기자 이름 정규표현식

    if category in ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학"]:
        class_dict = {
            "title": "media_end_head_head_title",
            "content": "_article_content",
            "email_reporter": "byline",
        }
        # title = _get_class_info(driver, class_dict["title"])
        # content = _get_class_info(driver, class_dict["content"])
        title = driver.find_element(By.CLASS_NAME, "media_end_head_title").text
        content = driver.find_element(By.CLASS_NAME, "_article_content").text
        email_text = driver.find_element(
            By.CLASS_NAME, class_dict["email_reporter"]
        ).text
        email = re.findall(email_pattern, email_text)[0]
        reporter = re.findall(reporter_pattern, email_text)[0]

        press = driver.find_element(
            By.CLASS_NAME, "media_journalistcard_summary_press_img"
        ).get_attribute("alt")

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

    elif category in ["스포츠", "연예"]:
        class_dict = dict(
            title="NewsEndMain_article_head_title__ztaL4",
            content="_article_content",
            email_reporter="NewsEndMain_article_journalist_info__Cdr3D",
        )
        title, content = _get_class_info(driver, class_dict["title"]), _get_class_info(
            driver, class_dict["content"]
        )

        email_text = driver.find_element(
            By.CLASS_NAME, class_dict["email_reporter"]
        ).text
        email = re.findall(email_pattern, email_text)[0]
        reporter = re.findall(reporter_pattern, email_text)[0]

        if category == "스포츠":
            press = (
                driver.find_element(
                    By.CLASS_NAME, "NewsEndMain_comp_article_main_news__0RmSO"
                )
                .find_element(By.CLASS_NAME, "NewsEndMain_image_media__rTvT1")
                .get_attribute("alt")
            )
            date_results = driver.find_elements(
                By.CLASS_NAME, "NewsEndMain_date__xjtsQ"
            )
            if len(date_results) > 1:
                date = date_results[1].text
            else:
                date = date_results[0].text
            date = convert_date(date)
        else:
            press = driver.find_element(
                By.CLASS_NAME, "NewsEndMain_highlight__HWvAi"
            ).text
            date_results = driver.find_elements(By.CLASS_NAME, "date")
            if len(date_results) > 1:
                date = date_results[1].text
            else:
                date = date_results[0].text
            date = convert_date(date)

    return {
        "title": title,
        "content": content,
        "press": press,
        "date": date,
        "reporter": reporter,
        "email": email,
    }


def crawl(
    url: str, category: str = None, chromedriver_path: str = "/usr/bin/chromedriver"
):
    set_chromedriver(chromedriver_path)
    info = get_news_info(url, category)
    return info
