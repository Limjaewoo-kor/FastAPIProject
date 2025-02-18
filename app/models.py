from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 🔹 SQLite 데이터베이스 설정 (PostgreSQL로 변경 가능)
DATABASE_URL = "sqlite:///./trendflow.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 🔹 검색 결과 모델 정의
class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)  # "네이버" or "티스토리"
    query = Column(String, index=True)
    title = Column(String)
    url = Column(String, unique=True)
    keywords = Column(Text)
    sentiment = Column(String)

# 🔹 데이터베이스 테이블 생성
def init_db():
    Base.metadata.create_all(bind=engine)
