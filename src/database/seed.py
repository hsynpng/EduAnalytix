import pandas as pd
from sqlalchemy.orm import Session
from src.database.db_config import SessionLocal, engine
from src.database.models import TrainingData


def seed_training_data():
    # 1. Oturum Aç
    db: Session = SessionLocal()

    # Eğer tabloda zaten veri varsa tekrar yükleme yapmayalım
    if db.query(TrainingData).count() > 0:
        print("⚠️ Veri tabanı zaten dolu. Yükleme atlandı.")
        db.close()
        return

    print("⏳ CSV dosyası okunuyor...")

    # 2. CSV'yi Oku
    # Dosya yolunu kendi projene göre gerekirse güncelle
    try:
        df = pd.read_csv("data/student_performance.csv")
    except FileNotFoundError:
        print("❌ HATA: 'data/student_performance.csv' dosyası bulunamadı!")
        return

    # 3. Veri Temizliği (Boş hücreleri doldurma)
    # Sayısal olmayan boşlukları "Unknown" yapalım
    object_cols = df.select_dtypes(include=['object']).columns
    df[object_cols] = df[object_cols].fillna("Unknown")

    # Sayısal boşlukları ortalama veya 0 ile doldurabiliriz (Şimdilik 0)
    num_cols = df.select_dtypes(include=['number']).columns
    df[num_cols] = df[num_cols].fillna(0)

    print(f"✅ {len(df)} satır veri hazırlandı, veritabanına yazılıyor...")

    # 4. Veritabanına Ekleme (Bulk Insert)
    # Pandas satırlarını TrainingData nesnesine çeviriyoruz
    data_to_insert = []
    for index, row in df.iterrows():
        record = TrainingData(
            hours_studied=row['Hours_Studied'],
            attendance=row['Attendance'],
            previous_scores=row['Previous_Scores'],
            tutoring_sessions=row['Tutoring_Sessions'],
            sleep_hours=row['Sleep_Hours'],
            physical_activity=row['Physical_Activity'],
            motivation_level=row['Motivation_Level'],
            parental_involvement=row['Parental_Involvement'],
            access_to_resources=row['Access_to_Resources'],
            internet_access=row['Internet_Access'],
            family_income=row['Family_Income'],
            teacher_quality=row['Teacher_Quality'],
            peer_influence=row['Peer_Influence'],
            learning_disabilities=row['Learning_Disabilities'],
            distance_from_home=row['Distance_from_Home'],
            exam_score=row['Exam_Score']
        )
        data_to_insert.append(record)

    # Toplu ekleme yap (Hız için)
    db.bulk_save_objects(data_to_insert)
    db.commit()
    db.close()

    print("🎉 Başarılı! Tüm veriler 'training_data' tablosuna yüklendi.")


if __name__ == "__main__":
    seed_training_data()