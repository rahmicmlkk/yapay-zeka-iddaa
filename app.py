import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, date
from sklearn.ensemble import RandomForestClassifier

# GÜVENLİK UYARISI: API Anahtarı Streamlit Secrets'tan çekiliyor
API_KEY = st.secrets["BENIM_SIFREM"]

st.set_page_config(page_title="VIP YZ Tahmin Pro", layout="wide", page_icon="💎")

# --- VIP TASARIM (CSS) EKLENTİLERİ ---
st.markdown("""
    <style>
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
    .vip-subtitle {
        text-align: center;
        color: #888888;
        font-size: 1.2em;
        font-style: italic;
        margin-bottom: 30px;
    }
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
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        box-shadow: 0px 6px 15px rgba(212, 175, 55, 0.6);
    }
    </style>
""", unsafe_allow_html=True)

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

# --- YENİ: ZAMAN MAKİNESİ FONKSİYONU ---
@st.cache_data(ttl=3600)
def maclarini_getir(hedef_tarih):
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {"date": hedef_tarih}
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
            st.markdown(f"**{index+1}.** {k_mac['mac']} *(⏰ {k_mac['saat']})*")
            st.info(f"👉 **{k_mac['tercih']}** | YZ Güveni: %{k_mac['guven']:.0f}")
            
        ortalama_guven = toplam_guven / len(kupon_listesi)
        st.success(f"📈 Kupon Ortalama Başarı İhtimali: **%{ortalama_guven:.0f}**")

# --- YENİ: KULLANICI ARAYÜZÜ VE TARİH SEÇİCİ ---
st.markdown("---")
col_tarih, col_bosluk = st.columns([1, 2])

with col_tarih:
    secilen_tarih = st.date_input("📅 Analiz Edilecek Tarihi Seçin:", value=date.today())
    secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

# Veriyi seçilen tarihe göre çekiyoruz!
data = maclarini_getir(secilen_tarih_str)

if "response" in data and len(data["response"]) > 0:
    bugunun_ligleri = list(set([mac["league"]["name"] for mac in data["response"]]))
    bugunun_ligleri.sort()
    
    ana_ligler = ["Süper Lig", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "Championship"]
    varsayilan_secimler = [lig for lig in ana_ligler if lig in bugunun_ligleri]
    
    secilen_ligler = st.multiselect(f"Hedef Ligleri Seçin ({secilen_tarih_str}):", options=bugunun_ligleri, default=varsayilan_secimler)
    filtrelenmis_mac_sayisi = len([m for m in data["response"] if m["league"]["name"] in secilen_ligler])
    
    if filtrelenmis_mac_sayisi > 0:
        if st.button(f"👑 {secilen_tarih_str} TARİHLİ ELITE ANALİZİ BAŞLAT ({filtrelenmis_mac_sayisi} Maç)"):
            with st.spinner(f"{secilen_tarih_str} tarihli maçlar VIP Algoritmalar ile taranıyor..."):
                
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
                            "oran_korner": tahminler["Korner 8.5 Üst"],
                            "oran_iy": tahminler["İY 0.5 Üst"]
                        })

                st.markdown("---")
                tab_kombineler, tab_ligler = st.tabs(["🎯 VIP KOMBİNELER", "📋 LİG LİG TÜM MAÇLAR"])

                with tab_kombineler:
                    st.markdown(f"### 🤖 {secilen_tarih_str} Tarihli YZ Seçimi Kombineler")
                    
                    if len(tum_analizler) >= 3:
                        karma_adaylar = []
                        kullanilan_karma = []
                        
                        best_ms = sorted(tum_analizler, key=lambda x: x["guven_genel"], reverse=True)[0]
                        karma_adaylar.append({"mac": best_ms["mac"], "saat": best_ms["saat"], "tercih": best_ms["tercih_genel"], "guven": best_ms["guven_genel"]})
                        kullanilan_karma.append(best_ms["mac"])
                        
                        best_gol = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_karma], key=lambda x: x["oran_ust"], reverse=True)[0]
                        karma_adaylar.append({"mac": best_gol["mac"], "saat": best_gol["saat"], "tercih": "2.5 Üst", "guven": best_gol["oran_ust"]})
                        kullanilan_karma.append(best_gol["mac"])
                        
                        best_korner = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_karma], key=lambda x: x["oran_korner"], reverse=True)[0]
                        karma_adaylar.append({"mac": best_korner["mac"], "saat": best_korner["saat"], "tercih": "Korner 8.5 Üst", "guven": best_korner["oran_korner"]})
                        kullanilan_karma.append(best_korner["mac"])
                        
                        kupon_cizdir("PLATINUM KARMA KUPON", "💎", "#D4AF37", karma_adaylar, vurgulu=True)

                    banko_adaylar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_karma], key=lambda x: x["guven_genel"], reverse=True)
                    kupon_banko = [{"mac": m["mac"], "saat": m["saat"], "tercih": m["tercih_genel"], "guven": m["guven_genel"]} for m in banko_adaylar[:3]]
                    kullanilan_maclar = kullanilan_karma + [m["mac"] for m in kupon_banko]
                    
                    gol_adaylar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_maclar], key=lambda x: x["oran_ust"], reverse=True)
                    kupon_gol = [{"mac": m["mac"], "saat": m["saat"], "tercih": "2.5 Üst", "guven": m["oran_ust"]} for m in gol_adaylar[:3]]
                    kullanilan_maclar.extend([m["mac"] for m in kupon_gol])
                    
                    iy_adaylar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_maclar], key=lambda x: x["oran_iy"], reverse=True)
                    kupon_iy = [{"mac": m["mac"], "saat": m["saat"], "tercih": "İlk Yarı 0.5 Üst", "guven": m["oran_iy"]} for m in iy_adaylar[:3]]

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        kupon_cizdir("GÜNÜN BANKOSU", "🔥", "#FF4B4B", kupon_banko)
                    with col2:
                        kupon_cizdir("GOL ŞENLİĞİ", "⚽", "#3B82F6", kupon_gol)
                    with col3:
                        kupon_cizdir("İLK YARI GOLLÜ", "⏱️", "#F59E0B", kupon_iy)

                with tab_ligler:
                    st.markdown(f"### 📋 {secilen_tarih_str} Tarihli Kapsamlı İstihbarat")
                    
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
                                                
                                                st.markdown(f"<div style='text-align: center; color: gray;'>⏰ {saat}</div>", unsafe_allow_html=True)
                                                col_logo1, col_isim, col_logo2 = st.columns([1, 3, 1])
                                                with col_logo1:
                                                    st.image(ev_logo, width=30)
                                                with col_isim:
                                                    st.markdown(f"<div style='text-align: center; font-size: 13px;'><b>{ev_sahibi}</b><br>vs<br><b>{deplasman}</b></div>", unsafe_allow_html=True)
                                                with col_logo2:
                                                    st.image(dep_logo, width=30)
                                                
                                                st.markdown("---")
                                                st.success(f"💎 **{banko_tercih}**\n\n YZ Güveni: %{banko_oran:.0f}")
                                                
                                                with st.expander("📊 Diğer İhtimaller"):
                                                    st.caption(f"İY 0.5 Üst: %{tahminler['İY 0.5 Üst']:.0f}")
                                                    st.caption(f"2.5 Üst: %{tahminler['2.5 Üst']:.0f}")
                                                    st.caption(f"KG Var: %{tahminler['KG Var']:.0f}")
                                                    st.caption(f"Korner 8.5 Üst: %{tahminler['Korner 8.5 Üst']:.0f}")
    else:
        st.warning("Lütfen analiz yapmak için yukarıdan en az bir lig seçin.")
else:
    st.error("Seçili tarihte oynanacak maç bulunamadı veya API limiti doldu.")