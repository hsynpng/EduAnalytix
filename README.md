# 🎓 EduAnalytix

> **Yapay Zeka Destekli Öğrenci Performans Analiz ve Karar Destek Sistemi**

EduAnalytix, öğrencilerin akademik başarılarını tahmin eden, risk altındaki öğrencileri tespit eden ve hem velilere hem de öğretmenlere kişiselleştirilmiş öneriler sunan kapsamlı bir veri analitiği platformudur.

---

## 🚀 Proje Hakkında

Bu proje, modern eğitim teknolojilerini yapay zeka ile birleştirerek eğitimcilerin ve ailelerin daha bilinçli kararlar almasını sağlar. Makine öğrenmesi algoritmaları (Random Forest), öğrencinin çalışma alışkanlıkları, devamsızlık durumu ve sosyal faktörlerini analiz ederek dönem sonu başarı puanını tahmin eder.

### 🌟 Temel Özellikler

*   **📈 Bireysel Öğrenci Analizi:** Öğrenci bilgilerini girerek anlık başarı tahmini ve risk analizi.
*   **🤖 Yapay Zeka Destekli Öneriler:** Sonuçlara göre otomatik oluşturulan pedagojik tavsiyeler.
*   **👨‍👩‍👧‍👦 Veli & Öğretmen Raporları:** Veli için karne tadında HTML rapor indirilebilir, öğretmen için ise sınıf içi stratejiler sunulur.
*   **📂 Toplu Sınıf Analizi:** CSV dosyası yükleyerek tüm sınıfın risk haritasını çıkarma.
*   **📊 İnteraktif Dashboard:** Plotly grafikleri ile verileri görselleştirme.
*   **🗂️ Geçmiş Kayıtlar:** Yapılan tüm analizlerin veritabanında saklanması ve takibi.

---

## 🛠 Kullanılan Teknolojiler

Bu proje aşağıdaki teknoloji yığınını kullanmaktadır:

*   **Dil:** Python 3.9+
*   **Arayüz:** [Streamlit](https://streamlit.io/)
*   **Yapay Zeka:** Scikit-learn (Random Forest Regressor)
*   **Veri İşleme:** Pandas, NumPy
*   **Veritabanı:** PostgreSQL, SQLAlchemy
*   **Görselleştirme:** Plotly Express

---

## ⚙️ Kurulum ve Başlangıç

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Gereksinimler

*   Python kurulu olmalı.
*   PostgreSQL veritabanı kurulu ve çalışıyor olmalı.

### 2. Projeyi İndirin

```bash
git clone https://github.com/kullaniciadi/EduAnalytix.git
cd EduAnalytix
```

### 3. Sanal Ortam Oluşturun (Önerilen)

```bash
python -m venv .venv
# Windows için:
.venv\Scripts\activate
# Mac/Linux için:
source .venv/bin/activate
```

### 4. Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

### 5. Veritabanı Ayarları

`.env` dosyası oluşturarak (veya doğrudan `src/database/db_config.py` içinde) veritabanı bağlantı bilgilerinizi girin.
*(Not: Proje varsayılan olarak yerel PostgreSQL sunucusuna bağlanmaya çalışacaktır).*

### 6. Veritabanını Başlatın

Tabloları oluşturmak için ana scripti bir kez çalıştırın:

```bash
python main.py
```

### 7. Yapay Zeka Modelini Eğitin

Örnek veri seti ile modeli eğitmek için:

```bash
python src/logic/ml_engine.py
```
*Bu işlem `models/` klasörüne `.pkl` dosyalarını kaydedecektir.*

---

## ▶️ Uygulamayı Çalıştırma

Kurulum tamamlandıktan sonra arayüzü başlatmak için:

```bash
streamlit run src/ui/dashboard.py
```

Tarayıcınızda otomatik olarak `http://localhost:8501` adresi açılacaktır.

---

## 📂 Proje Yapısı

```
EduAnalytix/
├── data/                  # Eğitim verisetleri (CSV)
├── models/                # Eğitilmiş .pkl modelleri ve metrikler
├── src/
│   ├── database/          # Veritabanı modelleri ve bağlantı (SQLAlchemy)
│   ├── logic/             # Makine öğrenmesi ve veri işleme mantığı
│   ├── ui/                # Streamlit arayüz kodları
│   └── utils/             # Yardımcı fonksiyonlar (HTML rapor vb.)
├── main.py                # Başlangıç ve DB init scripti
├── requirements.txt       # Kütüphane listesi
└── README.md              # Proje dokümantasyonu
```

---

## 🤝 Katkıda Bulunma

1. Bu projeyi forklayın.
2. Yeni bir özellik dalı (branch) oluşturun (`git checkout -b yeni-ozellik`).
3. Değişikliklerinizi yapın ve commit'leyin (`git commit -m 'Yeni özellik eklendi'`).
4. Dalınızı pushlayın (`git push origin yeni-ozellik`).
5. Bir Pull Request açın.
