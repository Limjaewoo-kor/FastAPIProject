import re
from sklearn.feature_extraction.text import TfidfVectorizer



#  TF-IDF란?
# TF (Term Frequency): 문서에서 특정 단어가 얼마나 자주 등장하는지
# IDF (Inverse Document Frequency): 그 단어가 얼마나 희귀한지
# 즉, "문서에서 중요한 키워드를 자동으로 추출하는 방법"
def extract_keywords(text: str, top_n: int = 5):
    """ 블로그 본문에서 중요한 키워드를 추출하는 함수 (TF-IDF 사용) """
    #  특수문자 제거 & 소문자 변환
    text = re.sub(r"[^가-힣a-zA-Z0-9\s]", "", text.lower())

    #  TF-IDF 벡터화
    vectorizer = TfidfVectorizer(stop_words=["있다", "하다", "되다"])  # 불용어 제거 가능
    tfidf_matrix = vectorizer.fit_transform([text])

    #  중요 키워드 상위 n개 추출
    keywords = sorted(
        zip(vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0]),
        key=lambda x: x[1], reverse=True
    )[:top_n]

    return [word for word, score in keywords]



# 감성 분석이란?
# 블로그 글이 긍정적인지, 부정적인지 분석하는 방법
# "이 서비스 너무 좋아요!" → 긍정 😃
# "이거 최악이야..." → 부정 😡
# "그냥 쓸만해요" → 중립 😐

import pandas as pd
from konlpy.tag import Okt

# 감성 사전 데이터 로드
SENTIMENT_DICT_PATH = "data/KnuSentiLex.csv"

def load_sentiment_dict():
    """ 감성 사전 로드 (KNU 한국어 감성 사전) """
    df = pd.read_csv(SENTIMENT_DICT_PATH)
    sentiment_dict = dict(zip(df['word'], df['polarity']))
    return sentiment_dict

sentiment_dict = load_sentiment_dict()  # 사전 로드
okt = Okt()

def analyze_sentiment(text: str):
    """ 한글 감성 분석 (사전 기반) """
    words = okt.morphs(text)  # 형태소 분석 (단어 단위 추출)
    sentiment_score = sum(sentiment_dict.get(word, 0) for word in words)

    if sentiment_score > 0:
        return "긍정 😀"
    elif sentiment_score < 0:
        return "부정 😡"
    else:
        return "중립 😐"



# beomi/KcELECTRA-base 모델 로드 & 감성 분석 코드
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# 감성 분석 전용 beomi/KcELECTRA-base 모델 사용 (일반 beomi/KcELECTRA-base 사용하면 오류 발생)
MODEL_NAME = "beomi/KcELECTRA-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

def analyze_sentiment_kcbert(text: str):
    """ beomi/KcELECTRA-base 이용한 한글 감성 분석 (올바른 감성 분석 모델 사용) """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    with torch.no_grad():  # 모델 추론 모드
        outputs = model(**inputs)

    score = torch.softmax(outputs.logits, dim=1)[0]

    # 모델이 제공하는 레이블이 긍정/부정인지 확인 필요
    if score[1] > score[0]:  # 긍정 확률이 높으면 긍정
        return "긍정 😀"
    else:  # 부정 확률이 높으면 부정
        return "부정 😡"
