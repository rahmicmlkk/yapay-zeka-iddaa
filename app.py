import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier

# GÜVENLİK UYARISI: API Anahtarı Streamlit Secrets'tan çekiliyor
API_KEY = st.secrets["BENIM_SIFREM"]

st.set_page_config(page_title="YZ İddaa Tahmin Pro", layout="wide", page_icon="⚽")
st.title("⚽ Günün Maçları ve 4 Farklı YZ Kombinesi")

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

# --- TÜRKİYE SAATİNE ÇEVİRME ---
def turkiye_saati_hesapla(api_tarih_str):
    utc_saat = datetime.strptime(api_tarih_str[:16], "%Y-%m-%dT%H:%M")
    tr_saat = utc_saat + timedelta(hours=3) 
    return tr_saat.strftime("%H:%M")

# --- YAPAY ZEKA DEĞER ORANI HESAPLAMA ---
def oran_hesapla(guven_yuzdesi):
    if guven_yuzdesi <= 0: return 1.00
    oran = (100 / guven_yuzdesi) * 0.92
    return max(1.05, round(oran, 2)) 

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
    
    ust_ihtimali = 30 + (toplam_guc_ve_form * 1.5)
    ust_ihtimali = max(20, min(85, ust_ihtimali)) 
    tahminler["2.5 Üst"] = ust_ihtimali
    tahminler["2.5 Alt"] = 100 - ust_ihtimali
    
    kg_var_ihtimali = 35 + (ev_guc + dep_guc) * 1.2
    kg_var_ihtimali = max(20, min(80, kg_var_ihtimali))
    tahminler["KG Var"] = kg_var_ihtimali
    
    korner_ust = 40 + (ev_form + dep_form) * 1.8
    korner_ust = max(25, min(88, korner_ust))
    tahminler["Korner 8.5 Üst"] = korner_ust
    
    en_iyi_tercih = max(tahminler, key=tahminler.get)
    en_iyi_oran = tahminler[en_iyi_tercih]
    
    return tahminler, en_iyi_tercih, en_iyi_oran

# --- KUPON ÇİZDİRME VE TOPLAM ORAN ---
def kupon_cizdir(baslik, ikon, renk, kupon_listesi):
    with st.container(border=True):
        st.markdown(f"<h4 style='text-align: center; color: {renk};'>{ikon} {baslik} {ikon}</h4>", unsafe_allow_html=True)
        st.markdown("---")
        if len(kupon_listesi) == 0:
            st.warning("Bu kategori için yeterli maç bulunamadı.")
            return

        toplam_oran = 1.0
        
        for index, k_mac in enumerate(kupon_listesi):
            mac_orani = oran_hesapla(k_mac["guven"])
            toplam_oran *= mac_orani
            
            st.markdown(f"**{index+1}.** {k_mac['mac']} *(⏰ {k_mac['saat']})*")
            st.info(f"👉 **{k_mac['tercih']}** | Güven: %{k_mac['guven']:.0f} | **Oran: {mac_orani:.2f}**")
            
        st.success(f"💰 Toplam Kupon Oranı: **{toplam_oran:.2f}**")

# --- ARAYÜZ ---
data = bugunun_maclarini_getir()

if "response" in data and len(data["response"]) > 0:
    bugunun_ligleri = list(set([mac["league"]["name"] for mac in data["response"]]))
    bugunun_ligleri.sort()
    
    ana_ligler = ["Süper Lig", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "Championship"]
    varsayilan_secimler = [lig for lig in ana_ligler if lig in bugunun_ligleri]
    
    secilen_ligler = st.multiselect("Hedef Ligleri Seçin:", options=bugunun_ligleri, default=varsayilan_secimler)
    filtrelenmis_mac_sayisi = len([m for m in data["response"] if m["league"]["name"] in secilen_ligler])
    
    if filtrelenmis_mac_sayisi > 0:
        if st.button(f"Analizi Başlat ve Kuponları Oluştur ({filtrelenmis_mac_sayisi} Maç)"):
            with st.spinner("Yapay zeka binlerce ihtimali tarayıp oranları hesaplıyor..."):
                
                tab1, tab2 = st.tabs(["🎯 ÖZEL KOMBİNE KUPONLAR", "📋 Tüm Maçların Detaylı Analizi"])
                
                lig_gruplari = {}
                tum_analizler = [] 
                
                for mac in data["response"]:
                    lig_adi = mac["league"]["name"]
                    if lig_adi in secilen_ligler: 
                        if lig_adi not in lig_gruplari:
                            lig_gruplari[lig_adi] = []
                        lig_gruplari[lig_adi].append(mac)
                        
                        ev_sahibi = mac["teams"]["home"]["name"]
                        deplasman = mac["teams"]["away"]["name"]
                        saat = turkiye_saati_hesapla(mac["fixture"]["date"])
                        
                        ev_guc, ev_form = takim_istatistikleri_getir(ev_sahibi)
                        dep_guc, dep_form = takim_istatistikleri_getir(deplasman)
                        
                        tahminler, banko_tercih, banko_oran = tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, yapay_zeka)
                        
                        tum_analizler.append({
                            "mac": f"{ev_sahibi} - {deplasman}",
                            "saat": saat,
                            "tercih_genel": banko_tercih,
                            "guven_genel": banko_oran,
                            "oran_ust": tahminler["2.5 Üst"],
                            "oran_ms0": tahminler["MS 0 (Beraberlik)"],
                            "oran_korner": tahminler["Korner 8.5 Üst"]
                        })

                # --- 1. SEKME: 4 FARKLI KUPON ---
                with tab1:
                    st.markdown("### 🤖 YZ Tarafından Hesaplanmış Tahminler ve Oranlar")
                    
                    banko_adaylar = sorted(tum_analizler, key=lambda x: x["guven_genel"], reverse=True)
                    kupon_banko = [{"mac": m["mac"], "saat": m["saat"], "tercih": m["tercih_genel"], "guven": m["guven_genel"]} for m in banko_adaylar[:3]]
                    kullanilan_maclar = [m["mac"] for m in kupon_banko]
                    
                    gol_adaylar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_maclar], key=lambda x: x["oran_ust"], reverse=True)
                    kupon_gol = [{"mac": m["mac"], "saat": m["saat"], "tercih": "2.5 Üst", "guven": m["oran_ust"]} for m in gol_adaylar[:3]]
                    kullanilan_maclar.extend([m["mac"] for m in kupon_gol])
                    
                    surpriz_adaylar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_maclar], key=lambda x: x["oran_ms0"], reverse=True)
                    kupon_surpriz = [{"mac": m["mac"], "saat": m["saat"], "tercih": "MS 0 (Beraberlik)", "guven": m["oran_ms0"]} for m in surpriz_adaylar[:3]]
                    kullanilan_maclar.extend([m["mac"] for m in kupon_surpriz])
                    
                    korner_adaylar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_maclar], key=lambda x: x["oran_korner"], reverse=True)
                    kupon_korner = [{"mac": m["mac"], "saat": m["saat"], "tercih": "Korner 8.5 Üst", "guven": m["oran_korner"]} for m in korner_adaylar[:3]]

                    col1, col2 = st.columns(2)
                    with col1:
                        kupon_cizdir("GÜNÜN BANKOSU", "🔥", "#FF4B4B", kupon_banko)
                        kupon_cizdir("SÜRPRİZ / SİSTEM", "🎁", "#FACC15", kupon_surpriz)
                    with col2:
                        kupon_cizdir("GOL ŞENLİĞİ", "⚽", "#3B82F6", kupon_gol)
                        kupon_cizdir("KORNER KOMBİNESİ", "🚩", "#10B981", kupon_korner)

                # --- 2. SEKME: TÜM MAÇLARIN DETAYLI ANALİZİ ---
                with tab2:
                    st.markdown("### 📋 Seçili Liglerin Detaylı Listesi")
                    for lig, maclar in lig_gruplari.items():
                        with st.expander(f"🏆 {lig} ({len(maclar)} Maç)"):
                            for i in range(0, len(maclar), 3):
                                cols = st.columns(3) 
                                for j in range(3):
                                    if i + j < len(maclar):
                                        mac = maclar[i + j]
                                        with cols[j]:
                                            with st.container(border=True):
                                                ev_sahibi = mac["teams"]["home"]["name"]
                                                ev_logo = mac["teams"]["home"]["logo"]
                                                deplasman = mac["teams"]["away"]["name"]
                                                dep_logo = mac["teams"]["away"]["logo"]
                                                
                                                saat = turkiye_saati_hesapla(mac["fixture"]["date"])
                                                
                                                ev_guc, ev_form = takim_istatistikleri_getir(ev_sahibi)
                                                dep_guc, dep_form = takim_istatistikleri_getir(deplasman)
                                                tahminler, banko_tercih, banko_oran = tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, yapay_zeka)
                                                
                                                hesaplanan_oran = oran_hesapla(banko_oran)
                                                
                                                st.markdown(f"<div style='text-align: center; color: gray;'>⏰ {saat}</div>", unsafe_allow_html=True)
                                                col_logo1, col_isim, col_logo2 = st.columns([1, 3, 1])
                                                with col_logo1:
                                                    st.image(ev_logo, width=30)
                                                with col_isim:
                                                    st.markdown(f"<div style='text-align: center; font-size: 13px;'><b>{ev_sahibi}</b><br>vs<br><b>{deplasman}</b></div>", unsafe_allow_html=True)
                                                with col_logo2:
                                                    st.image(dep_logo, width=30)
                                                
                                                st.markdown("---")
                                                st.success(f"🔥 **{banko_tercih}**\n\n Güven: %{banko_oran:.0f} | **Oran: {hesaplanan_oran:.2f}**")
    else:
        st.warning("Lütfen analiz yapmak için yukarıdan en az bir lig seçin.")
else:
    st.error("Bugün oynanacak maç bulunamadı veya API limiti doldu.")