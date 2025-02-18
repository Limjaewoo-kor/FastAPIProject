import requests
from bs4 import BeautifulSoup
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET  # ✅ 환경 변수 가져오기


def fetch_tistory_content(url: str):
    """ 특정 Tistory 블로그 URL에서 본문 크롤링 """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": "페이지를 가져올 수 없음", "status_code": response.status_code}

        soup = BeautifulSoup(response.text, "html.parser")

        # Tistory 블로그 본문은 다양한 태그에 있을 수 있음 (여러 패턴 확인)
        content_div = soup.select_one("div.article_view, div.tt_article_useless_p_margin, div#content")

        if content_div:
            return {"url": url, "content": content_div.get_text(strip=True)}
        else:
            return {"error": "본문을 찾을 수 없음", "url": url}

    except Exception as e:
        return {"error": f"크롤링 중 오류 발생: {str(e)}"}


def fetch_tistory_blog_content(url: str):
    """ 티스토리 블로그 본문 크롤링 """
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "본문을 가져올 수 없음", "url": url}

    soup = BeautifulSoup(response.text, "html.parser")

    # 🔹 티스토리 블로그 본문을 찾을 수 있는 태그들
    content_div = soup.select_one("div.article_view")  # 최신 티스토리 블로그
    if not content_div:
        content_div = soup.select_one("div.tt_article_useless_p_margin")  # 구버전 티스토리

    if content_div:
        return {"url": url, "content": content_div.get_text(strip=True)}

    return {"error": "본문을 찾을 수 없음", "url": url}




def search_tistory_blogs_api(query: str, max_results: int = 10):
    """ 네이버 API를 사용하여 티스토리 블로그 검색 """

    url = f"https://openapi.naver.com/v1/search/blog.json?query={query}+site:tistory.com&display={max_results}"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return [{"title": item["title"], "link": item["link"]} for item in data["items"]]
    else:
        return {"error": "네이버 API 호출 실패", "status_code": response.status_code}


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def search_tistory_blogs_selenium(query: str, max_results: int = 10):
    """ 티스토리 검색 결과를 Selenium으로 크롤링 """

    # 🔹 Chrome 브라우저 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    search_url = f"https://search.daum.net/search?w=blog&q={query}&site=tistory.com"

    driver.get(search_url)
    driver.implicitly_wait(5)

    results = []
    posts = driver.find_elements(By.CSS_SELECTOR, "a.f_link_b")

    for post in posts[:max_results]:
        title = post.text
        link = post.get_attribute("href")
        results.append({"title": title, "link": link})

    driver.quit()

    # 🔹 크롤링된 결과 확인 (디버깅)
    print(f"크롤링된 티스토리 검색 결과: {results}")

    return results
