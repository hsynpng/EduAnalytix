from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
# Base sınıfını db_config dosyasından alıyoruz
from .db_config import Base


# 1. Tablo: Gerçek Öğrenci Verileri
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    # Faktörler (Kaggle veri setiyle uyumlu)
    hours_studied = Column(Integer)
    attendance = Column(Integer)
    previous_scores = Column(Integer)
    tutoring_sessions = Column(Integer)
    sleep_hours = Column(Integer)
    physical_activity = Column(Integer)
    motivation_level = Column(String)
    parental_involvement = Column(String)
    access_to_resources = Column(String)
    internet_access = Column(String)
    family_income = Column(String)
    teacher_quality = Column(String)
    peer_influence = Column(String)
    learning_disabilities = Column(String)
    distance_from_home = Column(String)

    # Gerçek sınav notu
    exam_score = Column(Integer, nullable=True)

    # İlişki
    predictions = relationship("AIPrediction", back_populates="student")


# 2. Tablo: Yapay Zeka Eğitim Verisi (Kaggle)
class TrainingData(Base):
    __tablename__ = "training_data"

    id = Column(Integer, primary_key=True, index=True)

    hours_studied = Column(Integer)
    attendance = Column(Integer)
    previous_scores = Column(Integer)
    tutoring_sessions = Column(Integer)
    sleep_hours = Column(Integer)
    physical_activity = Column(Integer)
    motivation_level = Column(String)
    parental_involvement = Column(String)
    access_to_resources = Column(String)
    internet_access = Column(String)
    family_income = Column(String)
    teacher_quality = Column(String)
    peer_influence = Column(String)
    learning_disabilities = Column(String)
    distance_from_home = Column(String)

    exam_score = Column(Integer)


# 3. Tablo: AI Sonuçları
class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))

    prediction_date = Column(DateTime, default=datetime.utcnow)
    predicted_score = Column(Float)
    risk_level = Column(String)
    top_factors = Column(String)
    recommendation = Column(String)

    student = relationship("Student", back_populates="predictions")
