import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


def search_naver_blogs_selenium(query: str, max_results: int = 10):
    """ 네이버 블로그 검색 결과 크롤링 (봇 감지 우회) """

    # 🔹 Undetected ChromeDriver 설정
    options = uc.ChromeOptions()
    options.headless = True  # 브라우저 창 없이 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("referer=https://www.naver.com/")  # 네이버에서 검색한 것처럼 보이게 함

    driver = uc.Chrome(options=options)

    search_url = f"https://search.naver.com/search.naver?where=post&query={query}"
    driver.get(search_url)

    time.sleep(3)  # 페이지 로딩 대기

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    results = []

    # 🔹 네이버 블로그 검색 결과에서 링크 & 제목 가져오기
    for item in soup.select("div.total_wrap")[:max_results]:
        title_tag = item.select_one("a.total_tit")
        if title_tag:
            title = title_tag.get_text()
            link = title_tag["href"]
            results.append({"title": title, "link": link})

    return results



def fetch_naver_blog_content_selenium(url: str):
    """ 네이버 블로그 본문 크롤링 (JavaScript 렌더링 대응) """

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저 창 없이 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)

    # 🔹 iframe 내부의 본문을 찾기 위해 3초 대기
    time.sleep(3)

    # 🔹 iframe이 있는 경우, 해당 iframe 내부 URL 가져오기
    try:
        iframe = driver.find_element(By.CSS_SELECTOR, "iframe#mainFrame")
        blog_url = iframe.get_attribute("src")
        driver.get("https://blog.naver.com" + blog_url)
        time.sleep(3)  # 새로운 페이지 로딩 대기
    except:
        pass  # iframe이 없는 경우 그대로 진행

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # 🔹 네이버 블로그 본문은 아래 태그들 중 하나에 있음
    content_div = soup.select_one("div.se-main-container")  # 최신 네이버 블로그
    if not content_div:
        content_div = soup.select_one("div#postViewArea")  # 구버전 네이버 블로그

    if content_div:
        return {"url": url, "content": content_div.get_text(strip=True)}

    return {"error": "본문을 찾을 수 없음", "url": url}
