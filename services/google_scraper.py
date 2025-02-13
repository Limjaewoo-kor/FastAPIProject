import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def search_tistory_google(query: str, max_results: int = 10):
    """ Google 검색을 통해 Tistory 블로그 상위 포스팅 URL 가져오기 """

    # Chrome 드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 화면 없이 실행 (리소스 절약)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")  # 크롤링 감지 방지
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # 최신 User-Agent

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Google 검색 URL
    search_url = f"https://www.google.com/search?q={query}+site:tistory.com"
    driver.get(search_url)

    # 추가 대기 시간 (Google 차단 방지)
    time.sleep(3)  # 🔥 Google 차단을 방지하기 위해 3초 대기

    # 검색 결과가 완전히 로딩될 때까지 대기
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.yuRUbf a")))
    except:
        driver.quit()
        return {"error": "검색 결과를 가져올 수 없음 (요소 미발견)"}

    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()  # 드라이버 종료

    results = []

    # Google 검색 결과에서 블로그 제목 & 링크 가져오기
    for g in soup.select("div.yuRUbf")[:max_results]:  # 🔥 최신 Google 검색 결과 태그
        title_tag = g.select_one("h3")
        link_tag = g.select_one("a")

        if title_tag and link_tag:
            title = title_tag.get_text()
            link = link_tag["href"]
            results.append({"title": title, "link": link})

    return results
