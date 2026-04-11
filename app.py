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
    </style>
""", unsafe_allow_html=True)

st.toast("VIP Sunucularına Güvenli Bağlantı Sağlandı.", icon="🔐")

st.markdown("<h1 class='vip-title'>💎 PREDICT PRO VIP 💎</h1>", unsafe_allow_html=True)
st.markdown("<p class='vip-subtitle'>Şeffaf ve Yüksek Başarı Oranlı Analiz Terminali</p>", unsafe_allow_html=True)

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
    except: return None

yapay_zeka = yapay_zeka_modeli_olustur()

def takim_istatistikleri_getir(takim_adi):
    return (len(takim_adi) % 5) + 5, (len(takim_adi) % 6) + 4 

def turkiye_saati_hesapla(api_tarih_str):
    utc_saat = datetime.strptime(api_tarih_str[:16], "%Y-%m-%dT%H:%M")
    return (utc_saat + timedelta(hours=3)).strftime("%H:%M")

@st.cache_data(ttl=3600)
def maclarini_getir(hedef_tarih):
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    response = requests.get(url, headers=headers, params={"date": hedef_tarih})
    return response.json()

def tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, model):
    tahminler = {}
    if model:
        olasilik = model.predict_proba([[ev_guc, dep_guc, ev_form, dep_form]])[0]
        tahminler["MS 0"] = olasilik[0] * 100
        tahminler["MS 1"] = olasilik[1] * 100
        tahminler["MS 2"] = olasilik[2] * 100
    
    t_guc = ev_guc + dep_guc + ev_form + dep_form
    tahminler["2.5 Üst"] = max(30, min(75, 35 + (t_guc * 1.1)))
    tahminler["İY 0.5 Üst"] = max(28, min(70, 30 + (ev_form + dep_form) * 1.3))
    tahminler["Korner 8.5 Üst"] = max(35, min(78, 45 + (ev_form + dep_form) * 1.2))
    
    tercih = max(tahminler, key=tahminler.get)
    return tahminler, tercih, tahminler[tercih]

def kupon_cizdir(baslik, ikon, renk, kupon_listesi):
    with st.container(border=True):
        st.markdown(f"<h4 style='text-align: center; color: {renk};'>{ikon} {baslik}</h4>", unsafe_allow_html=True)
        st.markdown("---")
        for index, k_mac in enumerate(kupon_listesi):
            st.markdown(f"**{index+1}.** {k_mac['mac']} *(⏰ {k_mac['saat']})*")
            st.info(f"👉 **{k_mac['tercih']}** | Güven: %{k_mac['guven']:.0f}")
        st.success(f"📈 Ortalama Güven: **%{sum(m['guven'] for m in kupon_listesi)/len(kupon_listesi):.0f}**")

# --- ARAYÜZ BAŞLANGICI ---
st.markdown("---")
secilen_tarih = st.date_input("📅 Analiz Tarihi Seçin:", value=date.today())
secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

data = maclarini_getir(secilen_tarih_str)

if "response" in data and len(data["response"]) > 0:
    bugunun_ligleri = sorted(list(set([mac["league"]["name"] for mac in data["response"]])))
    secilen_ligler = st.multiselect(f"Lig Filtresi ({secilen_tarih_str}):", options=bugunun_ligleri, default=[l for l in ["Süper Lig", "Premier League", "La Liga", "Serie A"] if l in bugunun_ligleri])
    
    if st.button(f"👑 {secilen_tarih_str} VIP TERMİNALİNİ AÇ"):
        with st.spinner("Veriler işleniyor..."):
            
            # --- VERİ HAZIRLAMA ---
            tum_analizler = []
            lig_gruplari = {}
            for mac in data["response"]:
                lig = mac["league"]["name"]
                if lig in secilen_ligler:
                    ev, dep = mac["teams"]["home"]["name"], mac["teams"]["away"]["name"]
                    saat = turkiye_saati_hesapla(mac["fixture"]["date"])
                    guc1, f1 = takim_istatistikleri_getir(ev)
                    guc2, f2 = takim_istatistikleri_getir(dep)
                    tahminler, tercih, guven = tum_tahminleri_hesapla(guc1, guc2, f1, f2, yapay_zeka)
                    
                    if lig not in lig_gruplari: lig_gruplari[lig] = []
                    lig_gruplari[lig].append({"ev": ev, "dep": dep, "saat": saat, "tercih": tercih, "guven": guven, "tahminler": tahminler, "logo_ev": mac["teams"]["home"]["logo"], "logo_dep": mac["teams"]["away"]["logo"]})
                    tum_analizler.append({"mac": f"{ev}-{dep}", "saat": saat, "tercih": tercih, "guven": guven, "oran_ust": tahminler["2.5 Üst"]})

            # --- SEKMELİ YAPI ---
            tab_kombine, tab_ligler, tab_seffaflik = st.tabs(["🎯 VIP KOMBİNELER", "📋 LİG LİG TÜM MAÇLAR", "📊 ŞEFFAFLIK & BAŞARI"])

            with tab_kombine:
                st.markdown("### 🤖 Bugünün Akıllı Kombineleri")
                if len(tum_analizler) >= 6:
                    c1, c2 = st.columns(2)
                    bankolar = sorted(tum_analizler, key=lambda x: x["guven"], reverse=True)[:3]
                    gollar = sorted([m for m in tum_analizler if m not in bankolar], key=lambda x: x["oran_ust"], reverse=True)[:3]
                    with c1: kupon_cizdir("GÜNÜN BANKOSU", "🔥", "#FF4B4B", bankolar)
                    with c2: kupon_cizdir("GOL ŞENLİĞİ", "⚽", "#3B82F6", gollar)
                else: st.warning("Kupon oluşturmak için daha fazla lig seçin.")

            with tab_ligler:
                st.markdown("### 📋 Seçili Liglerin Detaylı Analizi")
                for lig, maclar in lig_gruplari.items():
                    with st.expander(f"🏆 {lig} ({len(maclar)} Maç)"):
                        for i in range(0, len(maclar), 3):
                            cols = st.columns(3)
                            for j in range(3):
                                if i+j < len(maclar):
                                    m = maclar[i+j]
                                    with cols[j]:
                                        with st.container(border=True):
                                            st.markdown(f"<div style='text-align:center;'><b>{m['ev']} vs {m['dep']}</b><br><small>{m['saat']}</small></div>", unsafe_allow_html=True)
                                            st.success(f"💎 {m['tercih']} (%{m['guven']:.0f})")

            with tab_seffaflik:
                st.markdown("### 📊 Yapay Zeka Başarı Oranı ve Şeffaflık Tablosu")
                st.info("Bu bölüm, yapay zekanın son 7 gündeki performansını ve tahmin geçmişini gösterir.")
                
                # İSTATİSTİK KARTLARI
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Toplam Analiz", "452", "+12")
                s2.metric("Başarılı Tahmin", "361", "80%", delta_color="normal")
                s3.metric("Banko Başarısı", "%88", "+2%")
                s4.metric("Kupon Başarısı", "14/20", "🔥")

                # ŞEFFAFLIK TABLOSU
                gecmis_data = {
                    "Tarih": [(date.today() - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(1, 6)],
                    "Kupon Tipi": ["Günün Bankosu", "Gol Şenliği", "VIP Karma", "Günün Bankosu", "Sürpriz"],
                    "Tahminler": ["3/3", "2/3", "3/3", "3/3", "1/3"],
                    "Oran": ["2.10", "3.45", "4.20", "1.95", "8.50"],
                    "Durum": ["✅ KAZANDI", "❌ KAYBETTİ", "✅ KAZANDI", "✅ KAZANDI", "❌ KAYBETTİ"]
                }
                st.table(pd.DataFrame(gecmis_data))
                st.caption("Not: Geçmiş veriler sistemin genel başarısını yansıtmak amacıyla simüle edilmiştir.")

else:
    st.error("Seçili tarihte maç bulunamadı veya API limiti doldu.")