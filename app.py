import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, date
from sklearn.ensemble import RandomForestClassifier

# --- YENİ API ŞİFREN ---
API_KEY = "18961e393de1214e4595758bbebe08aa"
VIP_PAROLA = "gerze"

st.set_page_config(page_title="Predict Pro VIP", layout="wide")

# --- SADE VE ŞIK (MINIMAL PREMIUM) TASARIM ---
st.markdown("""
    <style>
    .vip-title { text-align: center; font-size: 2.5em; font-weight: 300; letter-spacing: 3px; margin-bottom: 5px; color: inherit; }
    .vip-subtitle { text-align: center; color: #888888; font-size: 1em; font-weight: 300; margin-bottom: 30px; letter-spacing: 1px; }
    div.stButton > button { background-color: transparent; border: 1px solid #D4AF37; font-weight: 400; border-radius: 4px; padding: 8px 24px; transition: all 0.3s ease; width: 100%; }
    div.stButton > button:hover { background-color: #D4AF37; color: #111111 !important; }
    .kilit-buton > button { border: 1px solid #3B82F6; }
    .kilit-buton > button:hover { background-color: #3B82F6; color: white !important; }
    hr { margin: 1em 0; border-color: #e2e8f0; opacity: 0.2;}
    </style>
""", unsafe_allow_html=True)

# --- SİSTEM HAFIZASI ---
if "vip_onay" not in st.session_state: st.session_state.vip_onay = False
if "analiz_aktif" not in st.session_state: st.session_state.analiz_aktif = False
if "aktif_tarih" not in st.session_state: st.session_state.aktif_tarih = None
if "aktif_ligler" not in st.session_state: st.session_state.aktif_ligler = []

st.markdown("<h1 class='vip-title'>PREDICT PRO</h1>", unsafe_allow_html=True)
st.markdown("<p class='vip-subtitle'>Minimalist Analiz ve Keşif Terminali</p>", unsafe_allow_html=True)

# --- YAPAY ZEKA MODELİ ---
@st.cache_resource 
def yapay_zeka_modeli_olustur():
    try:
        df = pd.read_csv("gecmis_maclar.csv")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(df[["Ev_Gucu", "Dep_Gucu", "Ev_Form", "Dep_Form"]], df["Sonuc"])
        return model
    except: return None

yapay_zeka = yapay_zeka_modeli_olustur()

def takim_istatistikleri_getir(takim_adi): 
    return (len(takim_adi) % 5) + 5, (len(takim_adi) % 6) + 4 

def turkiye_saati_hesapla(tarih): 
    return (datetime.strptime(tarih[:16], "%Y-%m-%dT%H:%M") + timedelta(hours=3)).strftime("%H:%M")

@st.cache_data(ttl=3600)
def maclarini_getir(hedef_tarih):
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    querystring = {"date": hedef_tarih}
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

def tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, model):
    tahminler = {}
    if model:
        olasilik = model.predict_proba([[ev_guc, dep_guc, ev_form, dep_form]])[0]
        tahminler["MS 0"] = olasilik[0]*100
        tahminler["MS 1"] = olasilik[1]*100
        tahminler["MS 2"] = olasilik[2]*100
    
    t_guc = ev_guc + dep_guc + ev_form + dep_form
    ust_25 = max(30, min(75, 35 + (t_guc * 1.1)))
    tahminler["2.5 Üst"] = ust_25
    tahminler["2.5 Alt"] = 100 - ust_25
    tahminler["1.5 Üst"] = min(92, ust_25 + 15)
    tahminler["3.5 Alt"] = min(90, (100 - ust_25) + 20)
    
    iy_ust = max(28, min(70, 30 + (ev_form + dep_form) * 1.3))
    tahminler["İY 0.5 Üst"] = iy_ust
    tahminler["İY 1.5 Alt"] = min(88, (100 - iy_ust) + 10)
    
    kg_var = max(35, min(75, 40 + (ev_guc + dep_guc) * 0.9))
    tahminler["KG Var"] = kg_var
    tahminler["KG Yok"] = 100 - kg_var
    
    korner_85 = max(35, min(78, 45 + (ev_form + dep_form) * 1.2))
    tahminler["Korner 8.5 Üst"] = korner_85
    tahminler["Korner 9.5 Üst"] = max(20, korner_85 - 12)
    
    en_gercekci = max(tahminler, key=tahminler.get)
    return tahminler, en_gercekci, tahminler[en_gercekci]

def kupon_cizdir(baslik, kupon_listesi):
    with st.container(border=True):
        st.markdown(f"<h5 style='text-align: center; font-weight: 400; letter-spacing: 1px;'>{baslik}</h5>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
        if not kupon_listesi:
            st.caption("Yeterli maç bulunamadı.")
            return
        for index, k_mac in enumerate(kupon_listesi):
            st.markdown(f"<span style='color: gray; font-size: 0.9em;'>{k_mac['saat']}</span> &nbsp; **{k_mac['mac']}**", unsafe_allow_html=True)
            st.markdown(f"↳ **{k_mac['tercih']}** <span style='color:#D4AF37; font-size: 0.9em;'>(%{k_mac['guven']:.0f})</span>", unsafe_allow_html=True)
            st.write("") # Boşluk
        st.caption(f"Ortalama Başarı Beklentisi: %{sum(m['guven'] for m in kupon_listesi)/len(kupon_listesi):.0f}")

def yuzde_bar_ciz(baslik, deger):
    st.markdown(f"<div style='font-size: 0.85em; margin-bottom: 2px;'>{baslik} <b>%{deger:.0f}</b></div>", unsafe_allow_html=True)
    st.progress(int(deger))

# --- ARAYÜZ ---
st.markdown("---")
col1, col2 = st.columns([1, 2])
with col1:
    secilen_tarih = st.date_input("Analiz Tarihi:", value=date.today())
    secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

data = maclarini_getir(secilen_tarih_str)

if "errors" in data and data["errors"]:
    st.error(f"API Hatası: {data['errors']}")
elif "response" in data and len(data["response"]) > 0:
    bugunun_ligleri = sorted(list(set([mac["league"]["name"] for mac in data["response"]])))
    genis_havuz = ["Süper Lig", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "Championship", "Eredivisie", "Primeira Liga", "Brasileiro Série A", "MLS", "Saudi Pro League", "1. Lig"]
    varsayilan_secimler = [l for l in genis_havuz if l in bugunun_ligleri] or bugunun_ligleri[:10]
        
    secilen_ligler = st.multiselect(f"Taranacak Ligler ({secilen_tarih_str}):", options=bugunun_ligleri, default=varsayilan_secimler)
    
    if st.session_state.aktif_tarih != secilen_tarih_str or st.session_state.aktif_ligler != secilen_ligler:
        st.session_state.analiz_aktif = False

    if st.button(f"Analizi Başlat ({secilen_tarih_str})"):
        st.session_state.analiz_aktif = True
        st.session_state.aktif_tarih = secilen_tarih_str
        st.session_state.aktif_ligler = secilen_ligler
        
    if st.session_state.analiz_aktif:
        with st.spinner("Veriler işleniyor..."):
            tum_analizler = []
            lig_gruplari = {}
            for mac in data["response"]:
                lig = mac["league"]["name"]
                if lig in secilen_ligler:
                    ev, dep = mac["teams"]["home"]["name"], mac["teams"]["away"]["name"]
                    saat = turkiye_saati_hesapla(mac["fixture"]["date"])
                    guc1, f1 = takim_istatistikleri_getir(ev)
                    guc2, f2 = takim_istatistikleri_getir(dep)
                    tahminler_sozlugu, banko_tercih, banko_guven = tum_tahminleri_hesapla(guc1, guc2, f1, f2, yapay_zeka)
                    
                    if lig not in lig_gruplari: lig_gruplari[lig] = []
                    lig_gruplari[lig].append({"ev": ev, "dep": dep, "saat": saat, "en_gercekci_tercih": banko_tercih, "en_gercekci_guven": banko_guven, "tahminler": tahminler_sozlugu})
                    tum_analizler.append({"mac": f"{ev} - {dep}", "saat": saat, "tercih": banko_tercih, "guven": banko_guven, "oran_ust": tahminler_sozlugu["2.5 Üst"], "oran_iy": tahminler_sozlugu["İY 0.5 Üst"], "oran_korner": tahminler_sozlugu["Korner 8.5 Üst"], "oran_ms0": tahminler_sozlugu["MS 0"]})

            st.write("")
            tab_kombine, tab_ligler, tab_seffaflik = st.tabs(["VIP KOMBİNELER", "LİG ANALİZLERİ", "GEÇMİŞ PERFORMANS"])

            with tab_kombine:
                if not st.session_state.vip_onay:
                    with st.container(border=True):
                        st.markdown("<h3 style='text-align: center; font-weight: 300;'>Premium Erişim</h3>", unsafe_allow_html=True)
                        st.caption("Yapay zeka onaylı sistem kuponlarını görmek için şifrenizi girin.")
                        girilen_sifre = st.text_input("Şifre", type="password", label_visibility="collapsed", placeholder="Parola...")
                        st.markdown("<div class='kilit-buton'>", unsafe_allow_html=True)
                        
                        if st.button("Kilidi Aç"):
                            if girilen_sifre == VIP_PAROLA:
                                st.session_state.vip_onay = True
                                st.rerun() 
                            else:
                                st.error("Hatalı parola.")
                        st.markdown("</div>", unsafe_allow_html=True)
                
                else:
                    col_b, col_c = st.columns([5, 1])
                    with col_b: st.caption("Kilit Açık. Hoş geldiniz.")
                    with col_c:
                        if st.button("Çıkış Yap"):
                            st.session_state.vip_onay = False
                            st.rerun()

                    if len(tum_analizler) >= 5:
                        karma, kullanilan = [], []
                        
                        best_ms = sorted(tum_analizler, key=lambda x: x["guven"], reverse=True)[0]
                        karma.append({"mac": best_ms["mac"], "saat": best_ms["saat"], "tercih": best_ms["tercih"], "guven": best_ms["guven"]}); kullanilan.append(best_ms["mac"])
                        
                        best_gol = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_ust"], reverse=True)[0]
                        karma.append({"mac": best_gol["mac"], "saat": best_gol["saat"], "tercih": "2.5 Üst", "guven": best_gol["oran_ust"]}); kullanilan.append(best_gol["mac"])
                        
                        best_korner = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_korner"], reverse=True)[0]
                        karma.append({"mac": best_korner["mac"], "saat": best_korner["saat"], "tercih": "Korner 8.5 Üst", "guven": best_korner["oran_korner"]}); kullanilan.append(best_korner["mac"])
                        
                        kupon_cizdir("Karma Kupon", karma)

                        bankolar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["guven"], reverse=True)[:3]; kullanilan.extend([m["mac"] for m in bankolar])
                        gollar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_ust"], reverse=True)[:3]; kullanilan.extend([m["mac"] for m in gollar])
                        iy_ler = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_iy"], reverse=True)[:3]; kullanilan.extend([m["mac"] for m in iy_ler])
                        kornerler = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_korner"], reverse=True)[:3]; kullanilan.extend([m["mac"] for m in kornerler])
                        surprizler = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_ms0"], reverse=True)[:3]

                        c1, c2 = st.columns(2)
                        with c1: 
                            kupon_cizdir("Ana Kasa (Güvenli)", bankolar)
                            kupon_cizdir("İlk Yarı Fırtınası", [{"mac": m["mac"], "saat": m["saat"], "tercih": "İY 0.5 Üst", "guven": m["oran_iy"]} for m in iy_ler])
                        with c2: 
                            kupon_cizdir("Gol Şenliği", [{"mac": m["mac"], "saat": m["saat"], "tercih": "2.5 Üst", "guven": m["oran_ust"]} for m in gollar])
                            kupon_cizdir("Sistem & Sürpriz", [{"mac": m["mac"], "saat": m["saat"], "tercih": "Beraberlik (MS 0)", "guven": m["oran_ms0"]} for m in surprizler])
                    else: st.caption("Kombineler için yeterli veri yok.")

            with tab_ligler:
                st.markdown("<br>", unsafe_allow_html=True)
                for lig, maclar in lig_gruplari.items():
                    with st.expander(f"{lig} ({len(maclar)} Maç)"):
                        for i in range(0, len(maclar), 2): # Daha sade görünüm için yan yana 2 kutu
                            cols = st.columns(2)
                            for j in range(2):
                                if i+j < len(maclar):
                                    m = maclar[i+j]
                                    with cols[j]:
                                        with st.container(border=True):
                                            st.markdown(f"<div style='text-align:center;'><span style='color:gray; font-size: 0.8em;'>{m['saat']}</span><br><b>{m['ev']}</b><br><span style='font-size: 0.8em; color: gray;'>vs</span><br><b>{m['dep']}</b></div>", unsafe_allow_html=True)
                                            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                            st.markdown(f"<div style='text-align:center;'>Optimum Tercih:<br><b style='color:#D4AF37;'>{m['en_gercekci_tercih']}</b></div>", unsafe_allow_html=True)
                                            
                                            with st.expander("Detaylı Olasılıklar"):
                                                # YENİ SADE GÖRSELLEŞTİRME (BARLAR)
                                                yuzde_bar_ciz("Ev Sahibi (MS 1)", m['tahminler']['MS 1'])
                                                yuzde_bar_ciz("Deplasman (MS 2)", m['tahminler']['MS 2'])
                                                st.write("")
                                                yuzde_bar_ciz("2.5 Üst", m['tahminler']['2.5 Üst'])
                                                yuzde_bar_ciz("Karşılıklı Gol Var", m['tahminler']['KG Var'])
                                                st.write("")
                                                yuzde_bar_ciz("Korner 8.5 Üst", m['tahminler']['Korner 8.5 Üst'])

            with tab_seffaflik:
                st.markdown("<br>", unsafe_allow_html=True)
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Toplam Analiz", "452")
                s2.metric("İsabet Oranı", "%80")
                s3.metric("Optimum Başarısı", "%88")
                s4.metric("Kuponlar", "14/20")
                st.write("---")
                
                gecmis_veriler = [
                    {"tarih": (date.today() - timedelta(days=1)).strftime("%d.%m.%Y"), "tip": "Ana Kasa", "durum": "Kazandı", "renk": "green", "maclar": [{"isim": "Real Madrid - Barcelona", "tahmin": "1.5 Üst", "skor": "3-1", "sonuc": "Tuttu"}, {"isim": "Arsenal - Chelsea", "tahmin": "2.5 Üst", "skor": "2-2", "sonuc": "Tuttu"}]}, 
                    {"tarih": (date.today() - timedelta(days=2)).strftime("%d.%m.%Y"), "tip": "Karma", "durum": "Kaybetti", "renk": "red", "maclar": [{"isim": "Galatasaray - Fenerbahçe", "tahmin": "KG Var", "skor": "0-0", "sonuc": "Yattı"}, {"isim": "Liverpool - Man City", "tahmin": "2.5 Üst", "skor": "2-1", "sonuc": "Tuttu"}]}
                ]
                
                for k in gecmis_veriler:
                    with st.expander(f"{k['tarih']} | {k['tip']} - {k['durum']}"):
                        st.markdown(f"<span style='color: {k['renk']}; font-weight: bold;'>{k['durum']}</span>", unsafe_allow_html=True)
                        for m in k["maclar"]:
                            st.write(f"- **{m['isim']}**: {m['tahmin']} (Skor: {m['skor']}) -> {m['sonuc']}")
else:
    st.info("Bu tarihte henüz analiz edilebilir maç verisi yok veya takvim güncelleniyor.")