FROM python:3.10

# Java 설치
RUN apt-get update && apt-get install -y openjdk-17-jdk

# 환경 변수 설정
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# 프로젝트 복사 및 의존성 설치
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
