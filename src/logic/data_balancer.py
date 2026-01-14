import pandas as pd
import numpy as np
import os
import sys

# --- DİNAMİK YOL AYARI ---
# Scriptin olduğu dizini ve proje kök dizini (root) buluyoruz
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))

# Dosya yollarını kök dizine göre tam yol (absolute path) olarak tanımlıyoruz
INPUT_FILE = os.path.join(root_dir, "data", "student_performance.csv")
OUTPUT_FILE = os.path.join(root_dir, "data", "student_performance_balanced.csv")


def generate_balanced_data(num_samples=4000):
    new_rows = []

    # İstatistiksel olasılıkları koruyarak veri üretimi
    for _ in range(num_samples):
        hours = np.random.randint(1, 35)
        attendance = np.random.randint(40, 100)
        prev_score = np.random.randint(30, 100)
        sleep = np.random.randint(4, 10)
        tutoring = np.random.randint(0, 8)
        physical = np.random.randint(0, 6)

        motivation = np.random.choice(['Low', 'Medium', 'High'], p=[0.3, 0.4, 0.3])
        parental = np.random.choice(['Low', 'Medium', 'High'], p=[0.3, 0.4, 0.3])
        resources = np.random.choice(['Low', 'Medium', 'High'], p=[0.3, 0.4, 0.3])
        income = np.random.choice(['Low', 'Medium', 'High'], p=[0.3, 0.4, 0.3])
        teacher = np.random.choice(['Low', 'Medium', 'High'], p=[0.3, 0.4, 0.3])
        distance = np.random.choice(['Near', 'Moderate', 'Far'], p=[0.4, 0.4, 0.2])
        peer = np.random.choice(['Negative', 'Neutral', 'Positive'], p=[0.2, 0.5, 0.3])
        internet = np.random.choice(['Yes', 'No'], p=[0.8, 0.2])
        disability = np.random.choice(['Yes', 'No'], p=[0.1, 0.9])

        # --- MANTIKSAL SKOR HESAPLAMA ---
        # Bu kısım modelin "duyarlılığını" artıracak olan formüldür
        score_weight = 0

        # Kritik Faktörler (%60)
        score_weight += (prev_score / 100) * 0.3
        score_weight += (hours / 35) * 0.15
        score_weight += (attendance / 100) * 0.15

        # Destekleyici Faktörler (%30)
        m_map = {'Low': 0, 'Medium': 0.5, 'High': 1}
        score_weight += m_map[motivation] * 0.1
        score_weight += (sleep / 10) * 0.1
        score_weight += m_map[teacher] * 0.1

        # Çevresel ve Sosyal (%10)
        score_weight += (1 if internet == 'Yes' else 0) * 0.05
        score_weight += (0 if disability == 'Yes' else 0.05)

        # Rastgele gürültü ekleyerek veriyi gerçekçileştir (Normal Dağılım)
        final_score = (score_weight * 100) + np.random.normal(0, 3)
        final_score = max(min(final_score, 100), 10)

        new_rows.append({
            'hours_studied': hours, 'attendance': attendance, 'previous_scores': prev_score,
            'sleep_hours': sleep, 'tutoring_sessions': tutoring, 'physical_activity': physical,
            'motivation_level': motivation, 'parental_involvement': parental,
            'access_to_resources': resources, 'internet_access': internet,
            'family_income': income, 'teacher_quality': teacher,
            'peer_influence': peer, 'learning_disabilities': disability,
            'distance_from_home': distance, 'exam_score': round(final_score, 1)
        })

    return pd.DataFrame(new_rows)


if __name__ == "__main__":
    print(f"🔍 Kaynak dosya kontrol ediliyor: {INPUT_FILE}")

    if os.path.exists(INPUT_FILE):
        original_df = pd.read_csv(INPUT_FILE)
        # Sütun isimlerini normalize et
        original_df.columns = original_df.columns.str.strip().str.lower()

        print("⏳ 4000 satır mantıksal sentetik veri üretiliyor...")
        synthetic_df = generate_balanced_data(4000)

        print("🔗 Mevcut veri setiyle birleştiriliyor...")
        common_cols = list(set(original_df.columns) & set(synthetic_df.columns))
        combined_df = pd.concat([original_df[common_cols], synthetic_df[common_cols]], ignore_index=True)

        # Yeni dosyayı kaydet
        combined_df.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Başarılı! Yeni eğitim dosyan hazır: {OUTPUT_FILE}")
        print(f"📊 Toplam veri büyüklüğü: {len(combined_df)} satır.")
    else:
        print(f"❌ HATA: Kaynak dosya bulunamadı! Lütfen şurada bir CSV olduğundan emin ol: {INPUT_FILE}")