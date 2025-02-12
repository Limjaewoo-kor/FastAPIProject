import requests
from bs4 import BeautifulSoup

def fetch_blog_content(url: str):
    """ 티스토리 블로그 URL에서 제목과 본문을 크롤링하는 함수 """
    headers = {"User-Agent": "Mozilla/5.0"}  # User-Agent 설정 (차단 방지)
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to fetch the page", "status_code": response.status_code}

    soup = BeautifulSoup(response.text, "html.parser")

    #  제목 가져오기 (메타 태그에서 추출)
    title_tag = soup.find("meta", property="og:title")
    title = title_tag["content"] if title_tag else "제목을 찾을 수 없음"

    #  본문 가져오기
    content_div = soup.find("div", class_="tt_article_useless_p_margin contents_style")
    content = content_div.get_text(strip=True) if content_div else "본문을 찾을 수 없음"

    return {
        "url": url,
        "title": title,
        "content": content
    }
