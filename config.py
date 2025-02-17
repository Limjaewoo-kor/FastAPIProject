import os
from dotenv import load_dotenv

# 🔹 .env 파일 로드
load_dotenv(dotenv_path="config/.env")

# 🔹 환경 변수 가져오기
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
