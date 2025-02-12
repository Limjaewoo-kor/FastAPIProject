from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from services.html_scraper import fetch_blog_content
from services.rss_scraper import fetch_rss_feed
from services.text_analyzer import extract_keywords, analyze_sentiment, analyze_sentiment_kcbert
from services.google_scraper import search_tistory_google
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import base64

app = FastAPI()

#  Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")

#  시스템 내 한글 폰트 목록 가져오기
font_list = [f.name for f in fm.fontManager.ttflist]
print(font_list)  # 사용 가능한 폰트 출력

#  한글 폰트 설정
plt.rc('font', family='Malgun Gothic')  # Windows: 맑은 고딕
# plt.rc('font', family='AppleGothic')  # Mac: 애플고딕
# plt.rc('font', family='NanumGothic')  # Linux: 나눔고딕

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

@app.get("/")
def home():
    """ 메인 페이지 """
    return {"message": "블로그 분석 서비스 (FastAPI + Jinja2)"}


@app.get("/dashboard/")
def dashboard(request: Request, url: str):
    """ 블로그 분석 대시보드 """
    # http://127.0.0.1:8000/dashboard/?url=https://lcoding.tistory.com/199
    data = fetch_blog_content(url)
    if "error" in data:
        return {"error": "크롤링 실패"}

    #  키워드 분석
    keywords = extract_keywords(data["content"], top_n=5)

    #  감성 분석
    # sentiment = analyze_sentiment(data["content"])
    sentiment = analyze_sentiment_kcbert(data["content"])

    #  키워드 차트 생성
    fig, ax = plt.subplots()
    words = [kw for kw in keywords]
    scores = [i+1 for i in range(len(keywords))]
    ax.barh(words, scores, color='skyblue')
    plt.xlabel("중요도")
    plt.ylabel("키워드")
    plt.title("키워드 분석")

    #  차트를 Base64로 변환하여 HTML에서 사용 가능하게 변환
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "url": url,
        "title": data["title"],
        "content": data["content"][:500],  # 본문 미리보기 (500자)
        "keywords": keywords,
        "sentiment": sentiment,
        "chart_data": chart_data
    })



#RSS 크롤링 API
@app.get("/rss/")
def get_rss_feed(url: str, limit: int = 5):
    """ RSS 피드 데이터를 가져오는 API """
    # http://127.0.0.1:8000/rss/?url=https://techcrunch.com/feed/&limit=3
    data = fetch_rss_feed(url, limit)
    return {"status": "success", "data": data}


#티스토리 블로그 크롤링 API
@app.get("/blog-content/")
def get_blog_content(url: str):
    """ 특정 블로그 URL에서 제목과 본문을 가져오는 API """
    # http://127.0.0.1:8000/blog-content/?url=https://lcoding.tistory.com/199
    data = fetch_blog_content(url)
    return {"status": "success", "data": data}


#  키워드 분석 API (TF-IDF)
@app.get("/analyze-keywords/")
def get_keywords(url: str, top_n: int = 5):
    # http://127.0.0.1:8000/analyze-keywords/?url=https://lcoding.tistory.com/199&top_n=5
    data = fetch_blog_content(url)  # 블로그 본문 가져오기
    if "error" in data:
        return data

    keywords = extract_keywords(data["content"], top_n)
    return {"status": "success", "keywords": keywords}


# 감성 분석 API [감성 단어 기반 점수 계산]
@app.get("/analyze-sentiment/")
def get_sentiment(url: str):
    # http://127.0.0.1:8000/analyze-sentiment/?url=https://lcoding.tistory.com/199
    data = fetch_blog_content(url)  # 블로그 본문 가져오기
    if "error" in data:
        return data

    sentiment = analyze_sentiment(data["content"])
    return {"status": "success", "sentiment": sentiment}









#  KcBERT 감성 분석 API 추가 [문맥을 이해하는 딥러닝 모델]
@app.get("/analyze-sentiment-kcbert/")
def get_sentiment_kcbert(url: str):
    """ KcBERT 감성 분석 API """
    # http://127.0.0.1:8000/analyze-sentiment/?url=https://lcoding.tistory.com/199
    # https://blogdiary0525.tistory.com/65 짜증예시url
    # https://blogfindhappy.tistory.com/1 긍정예시url
    data = fetch_blog_content(url)  # 블로그 본문 가져오기
    if "error" in data:
        return data

    sentiment = analyze_sentiment_kcbert(data["content"])
    return {"status": "success", "sentiment": sentiment}



@app.get("/search-tistory-google/")
def search_tistory_google_api(query: str):
    """ Google 검색을 통해 Tistory 블로그 상위 10개 포스팅 검색 """
    results = search_tistory_google(query)
    return {"status": "success", "data": results}

