import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from urllib.parse import quote_plus

# .env dosyasını yükle
load_dotenv()

# Veritabanı bilgilerini al
user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "postgres")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
db_name = os.getenv("POSTGRES_DB", "edu_db")

# Şifreyi URL uyumlu hale getir
encoded_password = quote_plus(password)
DATABASE_URL = f"postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{db_name}"

# Motoru oluştur
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base sınıfını burada oluşturuyoruz (Modeller bunu kullanacak)
Base = declarative_base()


def init_db():
    """Tabloları veritabanında oluşturur."""
    # DÖNGÜYÜ KIRAN YER: Modelleri fonksiyonun İÇİNDE import et
    from src.database.models import Student, TrainingData, AIPrediction

    Base.metadata.create_all(bind=engine)
    print("✅ Veritabanı tabloları başarıyla oluşturuldu!")