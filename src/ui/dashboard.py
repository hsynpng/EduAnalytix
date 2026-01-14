import sys
import os
import json
import pandas as pd
import streamlit as st
import joblib
import plotly.express as px
from sqlalchemy.orm import Session
import base64  # HTML indirmek için gerekli

# --- PATH AYARI ---
# Proje kök dizinini bulup ekliyoruz ki src modülleri görülebilsin
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(root_dir)

from src.database.db_config import SessionLocal
from src.database.models import Student, AIPrediction
# Akıllı öneri motorunu dahil ediyoruz (Veli/Öğretmen ayrımı olan versiyon)
from src.utils.helpers import get_ai_feedback

st.set_page_config(page_title="EduAnalytix Pro", layout="wide", page_icon="🎓")


# --- MODELLERİ YÜKLE ---
@st.cache_resource
def load_ai_assets():
    try:
        model_path = os.path.join(root_dir, "models", "student_score_model.pkl")
        encoders_path = os.path.join(root_dir, "models", "encoders.pkl")
        metrics_path = os.path.join(root_dir, "models", "metrics.json")

        model = joblib.load(model_path)
        encoders = joblib.load(encoders_path)

        metrics = None
        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
        return model, encoders, metrics
    except FileNotFoundError:
        return None, None, None


model, encoders, metrics = load_ai_assets()


# --- RAPOR OLUŞTURUCU (HTML) ---
def create_report_html(student_name, score, risk, advice_list):
    """
    Sadece VELİYE GÖSTERİLECEK bilgileri içeren temiz bir HTML rapor oluşturur.
    Öğretmen notları buraya dahil edilmez.
    """
    advice_html = "".join([f"<li style='margin-bottom:10px;'>{item}</li>" for item in advice_list])

    # Basit ve Şık bir HTML Tasarımı
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; padding: 20px; background-color: #f4f4f4; }}
            .container {{ max-width: 800px; margin: 0 auto; background-color: #fff; padding: 40px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }}
            .header h1 {{ margin: 0; color: #2E7D32; }}
            .score-box {{ background-color: #f9f9f9; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 30px; border: 1px solid #e0e0e0; }}
            .score {{ font-size: 48px; font-weight: bold; color: #4CAF50; margin: 10px 0; }}
            .risk {{ font-size: 22px; font-weight: bold; color: #555; }}
            .advice-section {{ background-color: #e8f5e9; padding: 25px; border-radius: 10px; border-left: 5px solid #4CAF50; }}
            h2 {{ color: #2E7D32; margin-top: 0; }}
            ul {{ padding-left: 20px; }}
            .footer {{ margin-top: 40px; text-align: center; font-size: 12px; color: #888; border-top: 1px solid #eee; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 EduAnalytix Gelişim Raporu</h1>
                <p>Sayın Veli,</p>
            </div>

            <p style="font-size: 16px;">Öğrencimiz <strong>{student_name}</strong> için yapılan yapay zeka destekli akademik performans analizi sonuçları aşağıdadır.</p>

            <div class="score-box">
                <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Tahmini Dönem Sonu Başarısı</div>
                <div class="score">{score:.1f} / 100</div>
                <div class="risk">Genel Durum: {risk}</div>
            </div>

            <div class="advice-section">
                <h2>💡 Gelişim ve Destek Önerileri</h2>
                <ul>
                    {advice_html}
                </ul>
            </div>

            <div class="footer">
                Bu rapor EduAnalytix Yapay Zeka Destekli Karar Destek Sistemi tarafından oluşturulmuştur. <br>
                Okul Rehberlik Servisi
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


# --- SAYFA 1: ANALİZ ---
def show_analysis_page():
    st.title("🎓 Yeni Öğrenci Analizi")
    st.markdown("---")

    if not model:
        st.error("🚨 Model dosyaları bulunamadı! Lütfen önce 'ml_engine.py' dosyasını çalıştırın.")
        return

    # --- SOL MENÜ ---
    st.sidebar.header("📝 Öğrenci Bilgileri")
    if metrics:
        with st.sidebar.expander("ℹ️ Model Güvenilirliği", expanded=True):
            st.write(f"**Doğruluk (R2):** %{metrics['r2'] * 100:.1f}")
            st.write(f"**Hata Payı:** ±{metrics['mae']:.1f} Puan")
            st.caption(f"Son Eğitim: {metrics.get('last_trained', '-')}")
            if metrics['r2'] > 0:
                st.progress(metrics['r2'])

    first_name = st.sidebar.text_input("Öğrenci Adı")
    last_name = st.sidebar.text_input("Öğrenci Soyadı")
    st.sidebar.markdown("---")

    # Girdiler
    hours_studied = st.sidebar.number_input("Haftalık Çalışma Saati", 0, 168, 10)
    attendance = st.sidebar.slider("Devamsızlık Oranı (%)", 0, 100, 10)
    previous_scores = st.sidebar.number_input("Önceki Sınav Ortalaması", 0, 100, 75)
    sleep_hours = st.sidebar.slider("Günlük Uyku Saati", 0, 24, 7)
    tutoring_sessions = st.sidebar.number_input("Aylık Özel Ders Sayısı", 0, 30, 0)
    physical_activity = st.sidebar.number_input("Haftalık Spor Saati", 0, 20, 2)

    # Kategorik Girdiler
    motivation_level = st.sidebar.selectbox("Motivasyon Seviyesi", ["Low", "Medium", "High"])
    parental_involvement = st.sidebar.selectbox("Aile İlgisi", ["Low", "Medium", "High"])
    access_to_resources = st.sidebar.selectbox("Kaynaklara Erişim", ["Low", "Medium", "High"])
    internet_access = st.sidebar.selectbox("İnternet Erişimi", ["Yes", "No"])
    family_income = st.sidebar.selectbox("Aile Gelir Düzeyi", ["Low", "Medium", "High"])
    teacher_quality = st.sidebar.selectbox("Öğretmen Kalitesi (Algılanan)", ["Low", "Medium", "High"])
    peer_influence = st.sidebar.selectbox("Arkadaş Çevresi Etkisi", ["Negative", "Neutral", "Positive"])
    learning_disabilities = st.sidebar.selectbox("Öğrenme Güçlüğü", ["Yes", "No"])
    distance_from_home = st.sidebar.selectbox("Okula Uzaklık", ["Near", "Moderate", "Far"])

    data = {
        'hours_studied': hours_studied, 'attendance': attendance, 'previous_scores': previous_scores,
        'tutoring_sessions': tutoring_sessions, 'sleep_hours': sleep_hours, 'physical_activity': physical_activity,
        'motivation_level': motivation_level, 'parental_involvement': parental_involvement,
        'access_to_resources': access_to_resources, 'internet_access': internet_access,
        'family_income': family_income, 'teacher_quality': teacher_quality,
        'peer_influence': peer_influence, 'learning_disabilities': learning_disabilities,
        'distance_from_home': distance_from_home
    }
    input_df = pd.DataFrame(data, index=[0])

    # --- ORTA EKRAN ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Analiz Sonuçları")

        if 'prediction_result' not in st.session_state:
            st.session_state['prediction_result'] = None

        # --- TAHMİN ÖNCESİ SÜTUN SIRALAMASINI DÜZELTME ---
        if st.button("🚀 Başarıyı Tahmin Et", type="primary"):
            if not first_name or not last_name:
                st.warning("Lütfen önce öğrenci adını ve soyadını girin.")
            else:
                # 1. Veriyi Hazırla
                processed_df = input_df.copy()

                # 2. Encoding (Kategorik verileri sayıya çevir)
                for col, encoder in encoders.items():
                    if col in processed_df.columns:
                        try:
                            processed_df[col] = encoder.transform(processed_df[col].astype(str))
                        except:
                            processed_df[col] = 0

                # --- KRİTİK DÜZELTME BURASI ---
                # Modelin eğitim sırasında gördüğü sütunların listesini alıyoruz
                if hasattr(model, 'feature_names_in_'):
                    # processed_df içindeki sütunları, modelin beklediği sıraya göre diziyoruz
                    processed_df = processed_df[model.feature_names_in_]
                # ------------------------------

                # 3. Tahmin Yap
                pred = model.predict(processed_df)[0]

                # 4. Geri Bildirim Al
                feedback = get_ai_feedback(pred, input_df.iloc[0])

                st.session_state['prediction_result'] = {
                    'score': pred,
                    'feedback': feedback,
                    'processed_df': processed_df
                }

        if st.session_state['prediction_result']:
            res = st.session_state['prediction_result']
            fb = res['feedback']

            # Metrikler
            c1, c2 = st.columns(2)
            c1.metric("Tahmini Not", f"{res['score']:.1f} / 100")
            c2.metric("Risk Durumu", fb['risk_label'], delta_color="inverse")

            st.markdown("---")

            # --- YENİ: Veli ve Öğretmen Ayrımı (Tabs) ---
            st.subheader("📋 Detaylı Karne ve Raporlama")

            tab1, tab2 = st.tabs(["👨‍👩‍👧‍👦 Veli Raporu (Önizleme)", "👩‍🏫 Öğretmen Tavsiyeleri"])

            with tab1:
                st.info("💡 Bu sekmedeki bilgiler veli ile paylaşılacak raporda yer alır.")

                # Veliye özel mesajları göster
                for item in fb['parent_advice']:
                    st.write(f"- {item}")

                # HTML Raporunu Oluştur
                report_html = create_report_html(
                    f"{first_name} {last_name}",
                    res['score'],
                    fb['risk_label'],
                    fb['parent_advice']  # Sadece veli mesajlarını gönderiyoruz!
                )

                st.download_button(
                    label="📥 Veli Raporunu İndir (HTML)",
                    data=report_html,
                    file_name=f"Karne_{first_name}_{last_name}.html",
                    mime="text/html"
                )

            with tab2:
                st.warning("🔒 Bu sekme SADECE öğretmen içindir. Raporda yer almaz.")
                for item in fb['teacher_advice']:
                    st.write(f"- {item}")
            # ---------------------------------------------

            st.markdown("---")

            # Grafik
            importances = pd.DataFrame({
                'Faktör': res['processed_df'].columns,
                'Önem': model.feature_importances_
            }).sort_values(by='Önem', ascending=False).head(5)

            with st.expander("📊 Etkili Faktörleri Gör"):
                fig = px.bar(importances, x='Önem', y='Faktör', orientation='h', title="Başarıyı Etkileyen Faktörler")
                st.plotly_chart(fig, use_container_width=True)

            # Kaydetme Butonu
            if st.button("💾 Analizi Veritabanına Kaydet"):
                db = SessionLocal()
                try:
                    new_student = Student(first_name=first_name, last_name=last_name, **input_df.iloc[0].to_dict())
                    db.add(new_student)
                    db.commit()
                    db.refresh(new_student)

                    new_pred = AIPrediction(
                        student_id=new_student.id,
                        predicted_score=float(res['score']),
                        risk_level=fb['risk_label'],
                        top_factors="Manual Analysis",
                        recommendation=fb['final_text_for_db']  # Veritabanına birleşik metni kaydediyoruz
                    )
                    db.add(new_pred)
                    db.commit()
                    st.success(f"✅ {first_name} {last_name} sisteme kaydedildi!")
                except Exception as e:
                    st.error(f"Hata: {e}")
                finally:
                    db.close()

    with col2:
        st.info("💡 **Nasıl Kullanılır?**")
        st.write("""
        1. Öğrenci bilgilerini girin.
        2. 'Başarıyı Tahmin Et' butonuna basın.
        3. 'Veli Raporu' sekmesinden karneyi indirip veliye gönderin.
        4. 'Öğretmen Tavsiyeleri' sekmesinden sınıf içi stratejilerinizi belirleyin.
        """)


# --- SAYFA 2: TOPLU ANALİZ (Düzeltilmiş Versiyon) ---
def show_batch_analysis_page():
    st.title("📂 Toplu Sınıf Analizi")
    st.markdown("---")

    st.info("💡 **Bilgi:** Yükleyeceğiniz CSV dosyasındaki sütun isimleri otomatik olarak eşleştirilecektir.")

    uploaded_file = st.file_uploader("Sınıf Listesi Yükle (CSV)", type=["csv"])

    if uploaded_file is not None:
        try:
            input_df = pd.read_csv(uploaded_file)

            # --- DÜZELTME: Sütun isimlerini normalize et ---
            input_df.columns = input_df.columns.str.strip().str.lower()

            st.success(f"✅ Dosya yüklendi! Toplam {len(input_df)} öğrenci bulundu.")

            with st.expander("📄 Yüklenen Veriyi Gör", expanded=False):
                st.dataframe(input_df.head())

            if st.button("🚀 Toplu Analizi Başlat", type="primary"):

                processed_df = input_df.copy()

                # Encoder İşlemi
                for col, encoder in encoders.items():
                    if col in processed_df.columns:
                        processed_df[col] = processed_df[col].astype(str).apply(
                            lambda x: encoder.transform([x])[0] if x in encoder.classes_ else 0
                        )

                # Eksik sütun kontrolü
                expected_cols = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else processed_df.columns

                for col in expected_cols:
                    if col not in processed_df.columns:
                        processed_df[col] = 0

                # Tahmin
                try:
                    processed_df = processed_df[expected_cols]
                    predictions = model.predict(processed_df)
                except Exception as e:
                    st.error(f"Tahmin sırasında hata: {e}")
                    return

                # Sonuçları Birleştir
                results_df = input_df.copy()
                results_df['Tahmini_Not'] = predictions.round(1)

                def get_risk_label(score):
                    if score >= 85:
                        return "Düşük Risk"
                    elif score >= 50:
                        return "Orta Risk"
                    else:
                        return "Yüksek Risk"

                results_df['Risk_Durumu'] = results_df['Tahmini_Not'].apply(get_risk_label)

                # Görselleştirme
                st.markdown("### 📊 Sınıf Analiz Raporu")
                c1, c2 = st.columns(2)

                risk_counts = results_df['Risk_Durumu'].value_counts().reset_index()
                risk_counts.columns = ['Risk', 'Sayı']

                color_map = {'Düşük Risk': '#28a745', 'Orta Risk': '#ffc107', 'Yüksek Risk': '#dc3545'}

                fig_pie = px.pie(risk_counts, values='Sayı', names='Risk', title="Sınıf Risk Dağılımı",
                                 color='Risk', color_discrete_map=color_map)
                c1.plotly_chart(fig_pie, use_container_width=True)

                fig_hist = px.histogram(results_df, x="Tahmini_Not", nbins=20, title="Not Dağılımı",
                                        color_discrete_sequence=['#17a2b8'])
                fig_hist.add_vline(x=50, line_dash="dash", line_color="red", annotation_text="Geçme Sınırı")
                c2.plotly_chart(fig_hist, use_container_width=True)

                st.dataframe(results_df[['Tahmini_Not', 'Risk_Durumu']], use_container_width=True)

                # Veritabanına Kayıt
                st.markdown("---")
                if st.button("💾 Tüm Sonuçları Kaydet"):
                    db = SessionLocal()
                    progress_bar = st.progress(0)
                    success_count = 0

                    try:
                        for idx, row in results_df.iterrows():
                            f_name = row.get('first_name', "Öğrenci")
                            l_name = row.get('last_name', f"{idx + 1}")

                            # Student Tablosu İçin Veri Hazırlığı
                            student_data = row.to_dict()

                            # Fazlalıkları temizle
                            for key in ['Tahmini_Not', 'Risk_Durumu', 'first_name', 'last_name']:
                                if key in student_data:
                                    del student_data[key]

                            # Sadece model sütunlarını al
                            valid_columns = [c.name for c in Student.__table__.columns]
                            student_data = {k: v for k, v in student_data.items() if k in valid_columns}

                            new_student = Student(first_name=str(f_name), last_name=str(l_name), **student_data)
                            db.add(new_student)
                            db.commit()
                            db.refresh(new_student)

                            # Prediction Tablosu
                            feedback = get_ai_feedback(row['Tahmini_Not'], row)
                            new_pred = AIPrediction(
                                student_id=new_student.id,
                                predicted_score=row['Tahmini_Not'],
                                risk_level=row['Risk_Durumu'],
                                top_factors="Toplu Analiz",
                                recommendation=feedback['final_text_for_db']
                            )
                            db.add(new_pred)
                            success_count += 1
                            progress_bar.progress(success_count / len(results_df))

                        db.commit()
                        st.success(f"✅ {success_count} öğrenci başarıyla kaydedildi!")
                    except Exception as e:
                        st.error(f"Kayıt hatası: {e}")
                    finally:
                        db.close()

        except Exception as e:
            st.error(f"CSV işlenirken hata: {e}")


# --- SAYFA 3: GEÇMİŞ KAYITLAR ---
def show_history_page():
    st.title("🗂️ Geçmiş Analiz Kayıtları")
    st.markdown("Veritabanında kayıtlı tüm analizler.")

    db = SessionLocal()
    results = db.query(
        Student.first_name, Student.last_name, AIPrediction.predicted_score,
        AIPrediction.risk_level, AIPrediction.prediction_date, AIPrediction.recommendation
    ).join(AIPrediction).order_by(AIPrediction.prediction_date.desc()).all()
    db.close()

    if results:
        df = pd.DataFrame(results, columns=["Ad", "Soyad", "Tahmini Not", "Risk", "Tarih", "Öneri"])
        df['Tarih'] = pd.to_datetime(df['Tarih']).dt.strftime('%d-%m-%Y %H:%M')
        df['Tahmini Not'] = df['Tahmini Not'].round(1)

        st.dataframe(df, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Analiz", len(df))
        c2.metric("Ortalama Başarı", f"{df['Tahmini Not'].mean():.1f}")
        risky = len(df[df['Risk'].str.contains("Yüksek") | df['Risk'].str.contains("Kritik")])
        c3.metric("Riskli Öğrenci", risky, delta_color="inverse")
    else:
        st.warning("Henüz hiç kayıt bulunmuyor.")


# --- ANA UYGULAMA MANTIĞI ---
page = st.sidebar.selectbox("📌 Sayfa Seçimi", ["📊 Analiz Yap", "📂 Toplu Analiz", "🗂️ Geçmiş Kayıtlar"])

if page == "📊 Analiz Yap":
    show_analysis_page()
elif page == "📂 Toplu Analiz":
    show_batch_analysis_page()
else:
    show_history_page()