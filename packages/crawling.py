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


def get_news_info(url: str):
    driver.get(url)

    driver.implicitly_wait(
        2
    )  # 2초 안에 웹페이지를 load하면 바로 넘어가거나, 2초를 기다림

    # 사전 준비

    title = driver.find_element(
        By.CLASS_NAME, "NewsEndMain_article_head_title__ztaL4"
    ).text
    content = driver.find_element(By.CLASS_NAME, "_article_content").text
    content = re.sub(r"\n", " ", content)

    email_pattern = r"[a-zA-Z0-9._+-]+@[a-zA-Z0-9.]"
    email_text = driver.find_element(
        By.CLASS_NAME, "NewsEndMain_article_journalist_info__Cdr3D"
    ).text
    email = re.findall(email_pattern, email_text)[0]

    reporter_pattern = r"[^ㄱ-ㅎ가-힣]"
    reporter_text = driver.find_element(
        By.XPATH, '//*[@id="content"]/div[1]/div/div[1]/div/div[2]/div[1]/span'
    ).text

    reporter = re.sub(reporter_pattern, "", reporter_text).strip()

    press = driver.find_element(
        By.XPATH, '//*[@id="content"]/div[1]/div/div[1]/div/div[1]/a/img'
    ).get_attribute("alt")

    # date = driver.find_element(By.CLASS_NAME, "NewsEndMain_article_date__20A4F").text
    date = driver.find_element(
        By.XPATH,
        '//*[@id="content"]/div[1]/div/div[1]/div/div[1]/div[2]/div[1]/div[2]/em',
    ).text
    date = convert_date(date)

    return {
        "title": title,
        "content": content,
        "date": date,
        "reporter": reporter,
        "email": email,
        "press": press,
    }


def crawl(url: str, chromedriver_path: str = "/usr/bin/chromedriver"):
    set_chromedriver(chromedriver_path)
    info = get_news_info(url)
    return info
