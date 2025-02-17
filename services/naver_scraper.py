import requests
import urllib.parse  # URL 인코딩을 위한 모듈
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET  # ✅ 환경 변수 가져오기


def search_naver_blogs_api(query: str, max_results: int = 10):
    """ 네이버 블로그 검색 API 사용 (Selenium 없이 크롤링) """

    encoded_query = urllib.parse.quote(query)  # 🔹 URL 인코딩 추가
    url = f"https://openapi.naver.com/v1/search/blog.json?query={encoded_query}&display={max_results}"

    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if "items" in data:  # 🔹 검색 결과가 존재하는지 확인
            return [{"title": item["title"], "link": item["link"]} for item in data["items"]]
    else:
        print(f"네이버 API 오류: {response.status_code}, {response.text}")  # 🔹 디버깅 로그 추가
        return {"error": "네이버 API 호출 실패", "status_code": response.status_code}

    return {"error": "네이버 API에서 검색 결과 없음"}



from bs4 import BeautifulSoup


def get_naver_blog_original_url(blog_url: str):
    """ 네이버 블로그의 원본 URL을 가져오기 (iframe 처리) """
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(blog_url, headers=headers)
    if response.status_code != 200:
        return blog_url  # 실패하면 기존 URL 반환

    soup = BeautifulSoup(response.text, "html.parser")

    # 🔹 iframe 내부의 원본 링크 가져오기
    iframe = soup.select_one("iframe#mainFrame")
    if iframe:
        original_url = "https://blog.naver.com" + iframe["src"]
        return original_url

    return blog_url  # iframe이 없으면 원래 URL 반환


def fetch_naver_blog_content(url: str):
    """ 네이버 블로그 본문 크롤링 (iframe 해결) """
    headers = {"User-Agent": "Mozilla/5.0"}

    # 🔹 원본 URL 가져오기
    real_url = get_naver_blog_original_url(url)

    response = requests.get(real_url, headers=headers)
    if response.status_code != 200:
        return {"error": "본문을 가져올 수 없음", "url": url}

    soup = BeautifulSoup(response.text, "html.parser")

    # 🔹 네이버 블로그 본문을 찾을 수 있는 태그들 (최신 & 구버전)
    content_div = soup.select_one("div.se-main-container")  # 최신 네이버 블로그
    if not content_div:
        content_div = soup.select_one("div#postViewArea")  # 구버전 네이버 블로그

    if content_div:
        return {"url": url, "content": content_div.get_text(strip=True)}

    return {"error": "본문을 찾을 수 없음", "url": url}
