import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier

# GÜVENLİK UYARISI: API Anahtarı Streamlit Secrets'tan çekiliyor
API_KEY = st.secrets["BENIM_SIFREM"]

st.set_page_config(page_title="VIP YZ Tahmin Pro", layout="wide", page_icon="💎")

# --- YENİ: VIP TASARIM (CSS) EKLENTİLERİ ---
st.markdown("""
    <style>
    /* Altın Sarısı Premium Başlık */
    .vip-title {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #FFDF00, #D4AF37, #996515);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5em;
        font-weight: 900;
        margin-bottom: -10px;
        letter-spacing: 2px;
    }
    /* Alt başlık */
    .vip-subtitle {
        text-align: center;
        color: #888888;
        font-size: 1.2em;
        font-style: italic;
        margin-bottom: 30px;
    }
    /* VIP Altın Buton Tasarımı */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #D4AF37, #FFDF00);
        color: #111111 !important;
        border: none;
        font-weight: 800;
        font-size: 1.1em;
        border-radius: 8px;
        padding: 10px 24px;
        box-shadow: 0px 4px 10px rgba(212, 175, 55, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        box-shadow: 0px 6px 15px rgba(212, 175, 55, 0.6);
    }
    </style>
""", unsafe_allow_html=True)

# VIP Karşılama Mesajı (Sadece sayfa ilk yüklendiğinde çıkar)
st.toast("VIP Sunucularına Güvenli Bağlantı Sağlandı.", icon="🔐")

st.markdown("<h1 class='vip-title'>💎 PREDICT PRO VIP 💎</h1>", unsafe_allow_html=True)
st.markdown("<p class='vip-subtitle'>Yapay Zeka Destekli Elite Analiz Terminali</p>", unsafe_allow_html=True)

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

def turkiye_saati_hesapla(api_tarih_str):
    utc_saat = datetime.strptime(api_tarih_str[:16], "%Y-%m-%dT%H:%M")
    tr_saat = utc_saat + timedelta(hours=3) 
    return tr_saat.strftime("%H:%M")

# --- API'DEN VERİ ÇEKME ---
@st.cache_data(ttl=3600)
def bugunun_maclarini_getir():
    bugun = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {"date": bugun}
    headers = {"x-apisports-key": API_KEY}
    
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

# --- TÜM İHTİMALLERİ HESAPLAYAN MOTOR ---
def tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, model):
    tahminler = {}
    
    if model:
        olasilik = model.predict_proba([[ev_guc, dep_guc, ev_form, dep_form]])[0]
        tahminler["MS 0 (Beraberlik)"] = olasilik[0] * 100
        tahminler["MS 1 (Ev Sahibi)"] = olasilik[1] * 100
        tahminler["MS 2 (Deplasman)"] = olasilik[2] * 100
    else:
        tahminler["Model Hatası"] = 0

    toplam_guc_ve_form = ev_guc + dep_guc + ev_form + dep_form
    
    ust_ihtimali = 35 + (toplam_guc_ve_form * 1.1)
    ust_ihtimali = max(30, min(75, ust_ihtimali)) 
    tahminler["2.5 Üst"] = ust_ihtimali
    tahminler["2.5 Alt"] = 100 - ust_ihtimali
    
    kg_var_ihtimali = 40 + (ev_guc + dep_guc) * 0.9
    kg_var_ihtimali = max(35, min(75, kg_var_ihtimali))
    tahminler["KG Var"] = kg_var_ihtimali
    
    iy_ust_ihtimali = 30 + (ev_form + dep_form) * 1.3
    iy_ust_ihtimali = max(28, min(70, iy_ust_ihtimali))
    tahminler["İY 0.5 Üst"] = iy_ust_ihtimali
    
    korner_ust = 45 + (ev_form + dep_form) * 1.2
    korner_ust = max(35, min(78, korner_ust))
    tahminler["Korner 8.5 Üst"] = korner_ust
    
    en_iyi_tercih = max(tahminler, key=tahminler.get)
    en_iyi_oran = tahminler[en_iyi_tercih]
    
    return tahminler, en_iyi_tercih, en_iyi_oran

# --- KUPON ÇİZDİRME ---
def kupon_cizdir(baslik, ikon, renk, kupon_listesi, vurgulu=False):
    with st.container(border=True):
        st.markdown(f"<h4 style='text-align: center; color: {renk};'>{ikon} {baslik} {ikon}</h4>", unsafe_allow_html=True)
        st.markdown("---")
        if len(kupon_listesi) == 0:
            st.warning("Bu kategori için yeterli maç bulunamadı.")
            return

        toplam_guven = 0
        
        for index, k_mac in enumerate(kupon_listesi):
            toplam_guven += k_mac["guven"]
            
            st.