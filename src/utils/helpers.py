def get_ai_feedback(score, student_data):
    """
    Öğrenci verilerini kombine ederek derinlemesine bir profil analizi yapar.
    Veli ve Öğretmen için neden-sonuç ilişkisine dayalı aksiyon planları üretir.
    """

    # Verileri daha kolay kullanmak için normalize edelim
    hours = student_data.get('hours_studied', 0)
    prev_score = student_data.get('previous_scores', 0)
    attendance = student_data.get('attendance', 100)
    sleep = student_data.get('sleep_hours', 7)
    motivation = str(student_data.get('motivation_level', 'Medium')).lower()

    feedback = {
        "risk_label": "", "color": "", "icon": "", "title": "",
        "parent_advice": [], "teacher_advice": [], "final_text_for_db": ""
    }

    # 1. RİSK VE DURUM TESPİTİ (Görsel Göstergeler)
    if score >= 85:
        feedback.update(
            {"risk_label": "Düşük Risk", "color": "success", "icon": "🏆", "title": "Üstün Başarı Potansiyeli"})
    elif score >= 70:
        feedback.update({"risk_label": "Güvenli Bölge", "color": "info", "icon": "📈", "title": "İstikrarlı Gelişim"})
    elif score >= 50:
        feedback.update({"risk_label": "Orta Risk", "color": "warning", "icon": "⚠️", "title": "Kritik Eşik"})
    else:
        feedback.update({"risk_label": "Yüksek Risk", "color": "error", "icon": "🚨", "title": "Acil Akademik Müdahale"})

    # 2. ÖĞRENCİ PROFİL ANALİZİ (Mini Analiz ve Neden-Sonuç İlişkisi)

    # SENARYO A: "Potansiyeli Altında Kalanlar" (Geçmişi iyi ama mevcut çabası düşük)
    if prev_score > score + 10 and hours < 10:
        feedback["parent_advice"].append(
            f"Öğrencimizin geçmişteki {prev_score} puanlık başarısı, yüksek bir potansiyele sahip olduğunu kanıtlıyor. "
            f"Ancak haftalık {hours} saatlik çalışma temposu, bu potansiyelin altında kalmasına neden oluyor. "
            "Evde başarının sadece zeka değil, disiplinle desteklenmesi gerektiğini vurgulayan bir rutin oluşturulmalıdır."
        )
        feedback["teacher_advice"].append(
            "Öğrenci 'Düşük Çaba / Yüksek Potansiyel' profilinde. Akademik bir bıkkınlık yaşıyor olabilir. "
            "Öğrenciye ilgi duyduğu alanlarda proje tabanlı sorumluluklar verilerek içsel motivasyonu tekrar tetiklenmelidir."
        )

    # SENARYO B: "Çabalayan Ama Verim Alamayanlar" (Çalışma saati yüksek ama skor düşük)
    elif hours > 15 and score < 70:
        feedback["parent_advice"].append(
            f"Haftalık {hours} saatlik yoğun çalışma temposuna rağmen notların beklenen seviyeye gelmemesi, 'verimsiz çalışma' sinyali veriyor. "
            "Çocuğunuzun ders başında geçirdiği süreden ziyade, konuyu anlayıp anlamadığına odaklanmalı; "
            "çalışma sırasında dikkat dağıtıcı unsurlar (telefon/gürültü) minimize edilmelidir."
        )
        feedback["teacher_advice"].append(
            "Öğrenci yüksek çaba sarf ediyor ancak öğrenme stratejilerinde problem var. "
            "Aktif geri çağırma (active recall) ve aralıklı tekrar teknikleri konusunda rehberlik edilmeli, "
            "temel kavramlardaki eksikleri için 'scaffolding' (iskele kurma) yöntemiyle destek verilmelidir."
        )

    # SENARYO C: "Dışsal Faktör Kaynaklı Düşüş" (Uyku veya Devamsızlık sorunu)
    if sleep < 6 or attendance < 80:
        reason = "yetersiz uyku düzeni" if sleep < 6 else "devamsızlık kaynaklı konu kopukluğu"
        feedback["parent_advice"].append(
            f"Analizimiz, başarının önündeki asıl engelin akademik değil, yaşam tarzı kaynaklı ({reason}) olduğunu gösteriyor. "
            f"Zihinsel tazelik olmadan öğrenme gerçekleşemez; lütfen evdeki {sleep} saatlik uyku düzenini en az 8 saate çekmeye odaklanın."
        )
        feedback["teacher_advice"].append(
            "Öğrencinin bilişsel performansı fiziksel yorgunluk/devamsızlık nedeniyle kısıtlanıyor. "
            "Sınıf içi performansı düşük olduğunda eleştirmek yerine, okula aidiyet hissini artıracak sosyal katılımlar teşvik edilmelidir."
        )

    # SENARYO D: "Motivasyon ve Çevre Etkisi"
    if motivation == "low" or student_data.get('peer_influence') == 'Negative':
        feedback["parent_advice"].append(
            "Öğrencimizin mevcut isteksizliği, akademik hedeflerle bağ kuramamasından kaynaklanıyor olabilir. "
            "Onunla okul dışı hobileri üzerinden bağ kurarak, bu hobilerin akademik başarıyla nasıl ilişkilendiğini (örn: disiplin) sabırla anlatmalısınız."
        )
        feedback["teacher_advice"].append(
            "Öğrenci 'Düşük Motivasyon' veya 'Olumsuz Akran Etkisi' risk grubunda. "
            "Sınıf içinde onu pozitif rol modellerle gruplandırarak sosyal öğrenme yoluyla tutum değişikliği hedeflenmelidir."
        )

    # 3. GENEL TAMAMLAYICI NOTLAR (Eğer özel durum yoksa)
    if not feedback["parent_advice"]:
        feedback["parent_advice"].append(
            "Mevcut veriler öğrencimizin dengeli bir gelişim sergilediğini gösteriyor. Bu istikrarı korumak için evdeki huzurlu çalışma ortamını sürdürmeniz yeterlidir.")
        feedback["teacher_advice"].append(
            "Öğrenci mevcut müfredatla uyumlu ilerliyor. Zorluk seviyesi kademeli artırılarak kapasitesi zorlanabilir.")

    feedback["final_text_for_db"] = "VELI: " + " ".join(feedback["parent_advice"])[:200]
    return feedback