import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# GÜVENLİK UYARISI: API Anahtarını buraya yaz 
API_KEY = "9aaaf3814b469af593c5067d1fa71337"

# YENİ: Yan yana 3 maç sığması için layout "wide" (geniş) yapıldı
st.set_page_config(page_title="YZ İddaa Tahmin Pro", layout="wide", page_icon="⚽")
st.title("⚽ Günün Maçları ve Gelişmiş YZ Analizi")

# --- YAPAY ZEKA MODELİ ---
@st.cache_resource 
def yapay_zeka_modeli_olustur():
    try:
        df = pd.read_csv("gecmis_maclar.csv")
        X_egitim_verisi = df[["Ev_Gucu", "Dep_Gucu", "Ev_Form", "Dep_Form"]]
        y_sonuclar = df["Sonuc"]
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_egitim_verisi, y_sonuclar)
        return model
    except FileNotFoundError:
        return None

yapay_zeka = yapay_zeka_modeli_olustur()

def takim_istatistikleri_getir(takim_adi):
    guc = (len(takim_adi) % 5) + 5  
    form = (len(takim_adi) % 6) + 4 
    return guc, form

# --- API'DEN VERİ ÇEKME ---
@st.cache_data(ttl=3600)
def bugunun_maclarini_getir():
    bugun = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {"date": bugun}
    headers = {"x-apisports-key": API_KEY}
    
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

# --- YENİ: TÜM İHTİMALLERİ HESAPLAYAN MOTOR ---
def tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, model):
    tahminler = {}
    
    # 1. Maç Sonucu (Eğittiğimiz Makine Öğrenmesi Modelinden)
    if model:
        olasilik = model.predict_proba([[ev_guc, dep_guc, ev_form, dep_form]])[0]
        tahminler["MS 0 (Beraberlik)"] = olasilik[0] * 100
        tahminler["MS 1 (Ev Sahibi)"] = olasilik[1] * 100
        tahminler["MS 2 (Deplasman)"] = olasilik[2] * 100
    else:
        tahminler["Model Hatası"] = 0

    # 2. Alt/Üst ve KG Var (Matematiksel Mantık Simülasyonu)
    toplam_guc_ve_form = ev_guc + dep_guc + ev_form + dep_form
    
    # İki takım da güçlüyse ve formdaysa maç "Üst" biter mantığı
    ust_ihtimali = 30 + (toplam_guc_ve_form * 1.5)
    ust_ihtimali = max(20, min(85, ust_ihtimali)) 
    tahminler["2.5 Üst"] = ust_ihtimali
    tahminler["2.5 Alt"] = 100 - ust_ihtimali
    
    # Karşılıklı Gol Mantığı
    kg_var_ihtimali = 35 + (ev_guc + dep_guc) * 1.2
    kg_var_ihtimali = max(20, min(80, kg_var_ihtimali))
    tahminler["KG Var"] = kg_var_ihtimali
    tahminler["KG Yok"] = 100 - kg_var_ihtimali
    
    # 3. Korner Mantığı (Hücumcu formda takımlar çok korner kullanır)
    korner_ust = 40 + (ev_form + dep_form) * 1.8
    korner_ust = max(25, min(88, korner_ust))
    tahminler["Korner 8.5 Üst"] = korner_ust
    tahminler["Korner 8.5 Alt"] = 100 - korner_ust
    
    # --- EN YÜKSEK İHTİMALİ (BANKOYU) BULMA ---
    en_iyi_tercih = max(tahminler, key=tahminler.get)
    en_iyi_oran = tahminler[en_iyi_tercih]
    
    return tahminler, en_iyi_tercih, en_iyi_oran

# --- ARAYÜZ (KULLANICI EKRANI) ---
st.markdown("### 🤖 Kapsamlı Algoritma Analizi")
st.write("Her maç için Alt/Üst, Korner, KG ve Maç Sonucu taranıp en yüksek ihtimalli (**🔥 BANKO**) seçenek sunulur.")

if st.button("Bugünün Maçlarını Analiz Et"):
    with st.spinner("Tüm marketler (Korner, Alt/Üst, KG) taranıyor..."):
        data = bugunun_maclarini_getir()
        
        if "response" in data and len(data["response"]) > 0:
            st.success(f"Günün tüm maçları (Toplam {len(data['response'])} maç) analiz edildi!")
            st.markdown("---")
            
            # MAÇLARI LİGLERE GÖRE GRUPLAMA
            lig_gruplari = {}
            for mac in data["response"]:
                lig_adi = mac["league"]["name"]
                if lig_adi not in lig_gruplari:
                    lig_gruplari[lig_adi] = []
                lig_gruplari[lig_adi].append(mac)
                
            # LİG LİG VE YAN YANA (3'LÜ) EKRANA YAZDIRMA
            for lig, maclar in lig_gruplari.items():
                with st.expander(f"🏆 {lig} ({len(maclar)} Maç)", expanded=True):
                    
                    # Maçları 3'erli gruplara (satırlara) bölen döngü
                    for i in range(0, len(maclar), 3):
                        cols = st.columns(3) # Yan yana 3 sütun aç
                        
                        # O satırdaki 3 maçı sırayla kolonlara yerleştir
                        for j in range(3):
                            if i + j < len(maclar):
                                mac = maclar[i + j]
                                with cols[j]:
                                    
                                    # Her maçı şık bir kutu (container) içine alıyoruz
                                    with st.container(border=True):
                                        ev_sahibi = mac["teams"]["home"]["name"]
                                        ev_logo = mac["teams"]["home"]["logo"]
                                        deplasman = mac["teams"]["away"]["name"]
                                        dep_logo = mac["teams"]["away"]["logo"]
                                        saat = mac["fixture"]["date"][11:16] 
                                        
                                        ev_guc, ev_form = takim_istatistikleri_getir(ev_sahibi)
                                        dep_guc, dep_form = takim_istatistikleri_getir(deplasman)
                                        
                                        # YENİ FONKSİYONU ÇAĞIRIYORUZ
                                        tahminler, banko_tercih, banko_oran = tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, yapay_zeka)
                                        
                                        # Kutu İçi Tasarımı
                                        st.markdown(f"<div style='text-align: center; color: gray;'>⏰ {saat}</div>", unsafe_allow_html=True)
                                        
                                        col_logo1, col_isim, col_logo2 = st.columns([1, 3, 1])
                                        with col_logo1:
                                            st.image(ev_logo, width=30)
                                        with col_isim:
                                            st.markdown(f"<div style='text-align: center; font-size: 13px;'><b>{ev_sahibi}</b><br>vs<br><b>{deplasman}</b></div>", unsafe_allow_html=True)
                                        with col_logo2:
                                            st.image(dep_logo, width=30)
                                        
                                        st.markdown("---")
                                        
                                        # Banko Tahmin Vurgusu
                                        st.success(f"🔥 **EN GÜÇLÜ TAHMİN**\n### {banko_tercih} (%{banko_oran:.0f})")
                                        st.progress(int(banko_oran))
                                        
                                        # Diğer ihtimalleri "Detaylar" kutusuna gizle
                                        with st.expander("📊 Diğer İhtimalleri Gör"):
                                            st.write(f"**Maç Sonucu:** MS1 (%{tahminler['MS 1 (Ev Sahibi)']:.0f}) | MS0 (%{tahminler['MS 0 (Beraberlik)']:.0f}) | MS2 (%{tahminler['MS 2 (Deplasman)']:.0f})")
                                            st.write(f"**Alt / Üst:** Üst (%{tahminler['2.5 Üst']:.0f}) | Alt (%{tahminler['2.5 Alt']:.0f})")
                                            st.write(f"**Karşılıklı Gol:** Var (%{tahminler['KG Var']:.0f}) | Yok (%{tahminler['KG Yok']:.0f})")
                                            st.write(f"**Korner:** 8.5 Üst (%{tahminler['Korner 8.5 Üst']:.0f}) | 8.5 Alt (%{tahminler['Korner 8.5 Alt']:.0f})")
        else:
            st.error("Bugün oynanacak maç bulunamadı veya API limiti doldu.")