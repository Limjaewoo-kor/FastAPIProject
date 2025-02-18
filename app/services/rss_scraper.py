import feedparser


def fetch_rss_feed(url: str, limit: int = 5):
    """ 주어진 RSS URL에서 최신 블로그 글을 가져오는 함수 """
    feed = feedparser.parse(url)

    results = []
    for entry in feed.entries[:limit]:  # 최신 limit개 데이터 가져오기
        results.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })

    return results
