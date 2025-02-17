from services.html_scraper import fetch_blog_content
from services.rss_scraper import fetch_rss_feed
from services.text_analyzer import extract_keywords, analyze_sentiment, analyze_sentiment_kcbert
from services.google_scraper import search_tistory_google
import matplotlib.font_manager as fm
import io
import base64
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import matplotlib.pyplot as plt
from models import SessionLocal, init_db
from services.naver_scraper import search_naver_blogs_api, fetch_naver_blog_content
from services.tistory_scraper import search_tistory_blogs_api, fetch_tistory_blog_content
from services.text_analyzer import extract_keywords, analyze_sentiment_kcbert
from fastapi import Depends
from sqlalchemy.orm import Session
from models import BlogPost
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
#  Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")
# 🔹 앱 시작 시 DB 초기화
init_db()

# 🔹 DB 세션 생성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000"],  # React 개발 서버 주소
    allow_origins=["*"],  # React 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  시스템 내 한글 폰트 목록 가져오기
font_list = [f.name for f in fm.fontManager.ttflist]
print(font_list)  # 사용 가능한 폰트 출력

#  한글 폰트 설정
plt.rc('font', family='Malgun Gothic')  # Windows: 맑은 고딕
# plt.rc('font', family='AppleGothic')  # Mac: 애플고딕
# plt.rc('font', family='NanumGothic')  # Linux: 나눔고딕

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

@app.get("/")
def home(request: Request):
    """ 메인 페이지 (검색 입력 화면) """
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/dashboard2/")
def show_dashboard2(request: Request, query: str, max_results: int = 5, top_n: int = 5, db: Session = Depends(get_db)):
    """ 티스토리 블로그 검색 → 본문 크롤링 → 분석 결과를 대시보드로 시각화 """
    # search_results = search_tistory_blogs_api(query, max_results)
    search_results = search_tistory_google(query, max_results)

    analyzed_results = []
    for result in search_results:
        analysis = fetch_tistory_blog_content(result["link"])
        if "error" in analysis:
            continue  # 본문 크롤링 실패한 경우 제외

        keywords = extract_keywords(analysis["content"], top_n)
        sentiment = analyze_sentiment_kcbert(analysis["content"])

        # 🔹 결과를 DB에 저장
        db_post = BlogPost(
            source="티스토리",
            query=query,
            title=result["title"],
            url=result["link"],
            keywords=",".join(keywords),
            sentiment=sentiment
        )
        db.add(db_post)
        db.commit()

        analyzed_results.append({
            "title": result["title"],
            "url": result["link"],
            "keywords": keywords,
            "sentiment": sentiment
        })

    # 키워드 분석 차트 생성
    keyword_freq = {}
    for result in analyzed_results:
        for kw in result["keywords"]:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

    # Matplotlib 차트 생성
    fig, ax = plt.subplots()
    words = list(keyword_freq.keys())
    scores = list(keyword_freq.values())
    ax.barh(words, scores, color='skyblue')
    plt.xlabel("등장 횟수")
    plt.ylabel("키워드")
    plt.title("티스토리 키워드 분석")

    # 차트를 Base64로 변환하여 HTML에서 사용 가능하게 변환
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close()

    return templates.TemplateResponse("dashboard2.html", {
        "request": request,
        "query": query,
        "results": analyzed_results,
        "chart_data": chart_data
    })


@app.get("/dashboard1/")
def show_dashboard1(request: Request, query: str, max_results: int = 5, top_n: int = 5, db: Session = Depends(get_db)):
    """ 네이버 블로그 검색 → 본문 크롤링 → 분석 결과를 대시보드로 시각화 """
    search_results = search_naver_blogs_api(query, max_results)

    analyzed_results = []
    for result in search_results:
        analysis = fetch_naver_blog_content(result["link"])
        if "error" in analysis:
            continue  # 오류 발생 시 해당 글 제외

        keywords = extract_keywords(analysis["content"], top_n)
        sentiment = analyze_sentiment_kcbert(analysis["content"])

        # 🔹 결과를 DB에 저장
        db_post = BlogPost(
            source="네이버",
            query=query,
            title=result["title"],
            url=result["link"],
            keywords=",".join(keywords),
            sentiment=sentiment
        )
        db.add(db_post)
        db.commit()

        analyzed_results.append({
            "title": result["title"],
            "url": result["link"],
            "keywords": keywords,
            "sentiment": sentiment
        })

    # 키워드 분석 차트 생성
    keyword_freq = {}
    for result in analyzed_results:
        for kw in result["keywords"]:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

    # Matplotlib 차트 생성
    fig, ax = plt.subplots()
    words = list(keyword_freq.keys())
    scores = list(keyword_freq.values())
    ax.barh(words, scores, color='skyblue')
    plt.xlabel("등장 횟수")
    plt.ylabel("키워드")
    plt.title("네이버 키워드 분석")

    # 차트를 Base64로 변환하여 HTML에서 사용 가능하게 변환
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close()

    return templates.TemplateResponse("dashboard1.html", {
        "request": request,
        "query": query,
        "results": analyzed_results,
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


from services.tistory_scraper import fetch_tistory_content

@app.get("/fetch-tistory-content/")
def fetch_tistory(url: str):
    """ Tistory 블로그 본문 크롤링 API """
    data = fetch_tistory_content(url)
    return {"status": "success", "data": data}


from services.text_analyzer import extract_keywords, analyze_sentiment_kcbert

@app.get("/analyze-tistory/")
def analyze_tistory(url: str, top_n: int = 5):
    """ Tistory 블로그 본문을 크롤링하고 키워드 분석 & 감성 분석 수행 """
    data = fetch_tistory_content(url)
    if "error" in data:
        return data

    keywords = extract_keywords(data["content"], top_n)
    sentiment = analyze_sentiment_kcbert(data["content"])

    return {
        "status": "success",
        "url": url,
        "keywords": keywords,
        "sentiment": sentiment
    }


from services.naver_scraper import search_naver_blogs_api,fetch_naver_blog_content
from services.tistory_scraper import search_tistory_blogs_api, fetch_tistory_blog_content, search_tistory_blogs_selenium
from services.text_analyzer import extract_keywords, analyze_sentiment_kcbert


@app.get("/search-analyze-naver/")
def search_analyze_naver(query: str, max_results: int = 5, top_n: int = 5, db: Session = Depends(get_db)):
    #http://127.0.0.1:8000/search-analyze-naver/?query=backend&max_results=5&top_n=5

    """ 네이버 블로그 검색 → 본문 크롤링 → 분석 자동화 """
    search_results = search_naver_blogs_api(query, max_results)

    analyzed_results = []
    for result in search_results:
        analysis = fetch_naver_blog_content(result["link"])
        if "error" in analysis:
            continue  # 본문 크롤링 실패한 경우 제외

        keywords = extract_keywords(analysis["content"], top_n)
        sentiment = analyze_sentiment_kcbert(analysis["content"])

        # 🔹 결과를 DB에 저장
        db_post = BlogPost(
            source="네이버",
            query=query,
            title=result["title"],
            url=result["link"],
            keywords=",".join(keywords),
            sentiment=sentiment
        )
        db.add(db_post)
        db.commit()

        analyzed_results.append({
            "title": result["title"],
            "url": result["link"],
            "keywords": keywords,
            "sentiment": sentiment
        })

    return {"status": "success", "data": analyzed_results}


@app.get("/search-analyze-tistory/")
def search_analyze_tistory(query: str, max_results: int = 5, top_n: int = 5, db: Session = Depends(get_db)):

    # http://127.0.0.1:8000/search-analyze-tistory/?query=backend&max_results=5&top_n=5

    """ 티스토리 블로그 검색 → 본문 크롤링 → 분석 자동화 """
    # search_results = search_tistory_blogs_api(query, max_results)
    search_results = search_tistory_google(query, max_results)

    analyzed_results = []
    for result in search_results:
        analysis = fetch_tistory_blog_content(result["link"])
        if "error" in analysis:
            continue  # 본문 크롤링 실패한 경우 제외

        keywords = extract_keywords(analysis["content"], top_n)
        sentiment = analyze_sentiment_kcbert(analysis["content"])

        # 🔹 결과를 DB에 저장
        db_post = BlogPost(
            source="티스토리",
            query=query,
            title=result["title"],
            url=result["link"],
            keywords=",".join(keywords),
            sentiment=sentiment
        )
        db.add(db_post)
        db.commit()

        analyzed_results.append({
            "title": result["title"],
            "url": result["link"],
            "keywords": keywords,
            "sentiment": sentiment
        })

    return {"status": "success", "data": analyzed_results}

