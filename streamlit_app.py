import streamlit as st
from services.html_scraper import fetch_blog_content
from services.text_analyzer import extract_keywords, analyze_sentiment

st.title("📊 블로그 분석 대시보드")

url = st.text_input("블로그 URL 입력:", "https://lcoding.tistory.com/199")

if st.button("분석 시작"):
    data = fetch_blog_content(url)
    if "error" in data:
        st.error("블로그 크롤링 실패!")
    else:
        st.subheader("📌 블로그 제목")
        st.write(data["title"])

        st.subheader("🔑 키워드 분석")
        keywords = extract_keywords(data["content"], top_n=5)
        st.write(keywords)

        st.subheader("📈 감성 분석")
        sentiment = analyze_sentiment(data["content"])
        st.write(sentiment)
