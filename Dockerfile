# 🔹 1. Python 3.9 기반 Docker 이미지 사용
FROM python:3.9

# Java 설치
RUN apt update && apt install -y openjdk-17-jdk

# JAVA_HOME 설정
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# 🔹 2. 작업 디렉토리 생성 및 설정
WORKDIR /app

# 🔹 3. 로컬 프로젝트의 모든 파일을 Docker 컨테이너 내부로 복사
COPY . /app

# 🔹 4. 패키지 설치
RUN pip install --no-cache-dir --upgrade pip \
    && pip install -r requirements.txt

# 🔹 5. FastAPI 실행 포트 설정 (Docker 내부 8000 포트 오픈)
EXPOSE 8000

# 🔹 6. FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
