import requests
from bs4 import BeautifulSoup


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
