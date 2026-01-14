import pandas as pd
import joblib
import json
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score

# Proje dizin yapısına göre path ayarı
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(root_dir)

# Dosya Yolları
MODEL_DIR = os.path.join(root_dir, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "student_score_model.pkl")
ENCODERS_PATH = os.path.join(MODEL_DIR, "encoders.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")

# --- ÖNEMLİ: YENİ VERİ SETİ YOLU ---
# data_balancer.py ile oluşturduğun dengeli veriyi kullanıyoruz
BALANCED_DATA_PATH = os.path.join(root_dir, "data", "student_performance_balanced.csv")

def train_and_save_model():
    print("⏳ Eğitim verisi yükleniyor...")

    # 1. Veriyi Yükle (Dengelenmiş CSV'den)
    if os.path.exists(BALANCED_DATA_PATH):
        print(f"📂 Dengelenmiş veri seti kullanılıyor: {BALANCED_DATA_PATH}")
        df = pd.read_csv(BALANCED_DATA_PATH)
    else:
        # Eğer dengelenmiş CSV yoksa hata ver ve dur (Çünkü sorunumuzu bu çözüyor)
        print(f"❌ HATA: {BALANCED_DATA_PATH} bulunamadı!")
        print("Lütfen önce 'data_balancer.py' scriptini çalıştırarak dengeli veriyi oluşturun.")
        return

    # Sütun isimlerini küçük harfe çevirerek standardizasyon sağla
    df.columns = df.columns.str.strip().str.lower()

    # Gereksiz id varsa temizle
    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    print(f"✅ {len(df)} satır veri ile eğitim başlıyor...")

    # 2. Veri Ön İşleme (Preprocessing)
    label_encoders = {}
    categorical_columns = df.select_dtypes(include=['object']).columns

    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = df[col].astype(str)
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

    # Hedef ve Özellik Ayrımı (Sütun isimlerinin küçük harf olduğundan emin ol)
    X = df.drop(columns=['exam_score'])
    y = df['exam_score']

    # Bölme (%80 Eğitim, %20 Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Modeli Eğit (Daha hassas olması için n_estimators artırılabilir)
    print("🧠 Yapay Zeka modeli eğitiliyor (Random Forest - Balanced)...")
    model = RandomForestRegressor(n_estimators=150, random_state=42, min_samples_split=5)
    model.fit(X_train, y_train)

    # 4. Test Et
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print(f"\n📊 --- Yeni Model Başarı Raporu ---")
    print(f"Ortalama Hata Payı (MAE): {mae:.2f} puan")
    print(f"Model Doğruluğu (R2 Score): {r2:.2f}")

    # 5. Kaydet
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(label_encoders, ENCODERS_PATH)

    metrics_data = {
        "mae": mae,
        "r2": r2,
        "last_trained": pd.Timestamp.now().strftime("%d-%m-%Y %H:%M")
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_data, f)

    print(f"\n💾 Yeni model ve metrikler kaydedildi: {MODEL_DIR}")
    print("✅ Artık dashboard üzerinden en kötü senaryoları test edebilirsiniz!")

if __name__ == "__main__":
    train_and_save_model()