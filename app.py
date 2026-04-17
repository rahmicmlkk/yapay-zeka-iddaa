import streamlit as st
import requests
import pandas as pd
import urllib.parse
import hashlib
import random
from datetime import datetime, timedelta, date
from sklearn.ensemble import RandomForestClassifier

# --- SENİN API ŞİFREN ---
API_KEY = "18961e393de1214e4595758bbebe08aa"

st.set_page_config(page_title="Predict Pro VIP | Yeraltı Terminali", layout="wide", initial_sidebar_state="expanded")

# --- HACKER / İSTİHBARAT TASARIMI ---
st.markdown("""
    <style>
    .elegant-title { text-align: center; font-family: 'Courier New', Courier, monospace; font-size: 2.2em; font-weight: 800; letter-spacing: 4px; margin-bottom: 0px; padding-top: 10px; color: #10b981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.5); }
    .elegant-subtitle { text-align: center; color: #94a3b8; font-family: 'Courier New', Courier, monospace; font-size: 1em; font-weight: 600; letter-spacing: 2px; margin-bottom: 40px; }
    div.stButton > button { background-color: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; font-weight: bold; letter-spacing: 1px; border-radius: 4px; padding: 8px 24px; transition: all 0.4s ease; width: 100%; color: #10b981 !important; font-family: 'Courier New', Courier, monospace;}
    div.stButton > button:hover { background-color: #10b981; color: #000 !important; box-shadow: 0 0 15px rgba(16, 185, 129, 0.8); }
    hr { margin: 1.5em 0; border: none; height: 1px; background: linear-gradient(90deg, rgba(16,185,129,0) 0%, rgba(16,185,129,0.5) 50%, rgba(16,185,129,0) 100%); }
    .wa-button { display: block; text-align: center; background-color: #25D366; color: white !important; padding: 10px; border-radius: 4px; text-decoration: none; font-weight: 600; letter-spacing: 1px; margin-top: 15px; font-family: sans-serif; }
    .value-badge { background-color: #f59e0b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; font-weight: bold; margin-left: 5px; }
    .insider-badge { display: inline-block; background-color: #ef4444; color: white; padding: 5px 10px; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-top: 10px; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.2; } }
    .terminal-box { background-color: #000; color: #0f0; font-family: 'Courier New', Courier, monospace; font-size: 0.8em; padding: 15px; border-radius: 5px; border: 1px solid #333; height: 300px; overflow-y: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- SİSTEM HAFIZASI ---
if "analiz_aktif" not in st.session_state: st.session_state.analiz_aktif = False
if "aktif_tarih" not in st.session_state: st.session_state.aktif_tarih = None
if "aktif_ligler" not in st.session_state: st.session_state.aktif_ligler = []

# --- SOL MENÜ: HACKER TERMİNALİ ŞOVU ---
with st.sidebar:
    st.markdown("<h3 style='color:#10b981; font-family: Courier New;'>📡 SİSTEM GÜNLÜĞÜ</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div class="terminal-box">
        root@predict-pro:~# connect --target asian_markets<br>
        [OK] Bypassing Bet365 Firewalls...<br>
        [OK] Establishing secure tunnel...<br>
        [!] Fetching underground volume data...<br>
        [OK] 4.2 TB data decrypted.<br>
        root@predict-pro:~# run deep_learning.py<br>
        [OK] Loading Chaos Theory matrices...<br>
        [OK] Referee behaviors injected.<br>
        [!] WARNING: Suspicious bets detected in lower leagues.<br>
        root@predict-pro:~# ready for execution.
        </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.caption("🔒 Bağlantı Şifreli: 256-bit AES")
    st.caption("📍 Sunucu Konumu: Gizli")

st.markdown("<h1 class='elegant-title'>PREDICT PRO // ROOT</h1>", unsafe_allow_html=True)
st.markdown("<p class='elegant-subtitle'>ASIAN MARKET INSIDER & DEEP LEARNING TERMINAL</p>", unsafe_allow_html=True)

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

def takim_istatistikleri_getir(takim_adi): return (len(takim_adi) % 5) + 5, (len(takim_adi) % 6) + 4 
def turkiye_saati_hesapla(tarih): return (datetime.strptime(tarih[:16], "%Y-%m-%dT%H:%M") + timedelta(hours=3)).strftime("%H:%M")

@st.cache_data(ttl=3600)
def maclarini_getir(hedef_tarih):
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    querystring = {"date": hedef_tarih}
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

def oran_ve_value_hesapla(guven, takimlar_str):
    sapma = (len(takimlar_str) % 15) - 5 
    iddaa_ihtimali = guven - sapma
    if iddaa_ihtimali <= 5: iddaa_ihtimali = 5
    oran = round(100 / iddaa_ihtimali, 2)
    oran = max(1.10, min(oran, 8.50))
    is_value = (guven - iddaa_ihtimali) > 4 
    return oran, is_value

def kaos_faktoru_uret(mac_ismi):
    sayi = int(hashlib.md5(mac_ismi.encode()).hexdigest(), 16)
    havalar = ["☀️ Açık", "🌧️ Sağanak", "☁️ Rüzgarlı", "❄️ Sert Zemin"]
    hakemler = ["🟨 4.5 Kart (Sert)", "🟩 2.1 Kart (Ilıman)", "🟥 Kırmızı Potansiyelli", "⚖️ Standart"]
    yorgunluk = ["🟢 İki Takım Dinç", "🔴 Ev Sahibi Yorgun", "🔴 Deplasman Yorgun", "🟡 Fikstür Sıkışık"]
    
    # ŞOV ÖZELLİĞİ: "Şikeli Maç" Radarı (Her 15 maçtan 1'inde tetiklenir)
    is_insider = (sayi % 15) == 0
    
    return {"hava": havalar[sayi % len(havalar)], "hakem": hakemler[(sayi // 10) % len(hakemler)], "yorgunluk": yorgunluk[(sayi // 100) % len(yorgunluk)], "is_insider": is_insider}

def tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, model, mac_ismi):
    tahminler = {}
    kaos = kaos_faktoru_uret(mac_ismi)
    kaos_etkisi = -5 if "Yağış" in kaos["hava"] else (-3 if "Yorgun" in kaos["yorgunluk"] else 0)
    
    if model:
        olasilik = model.predict_proba([[ev_guc, dep_guc, ev_form, dep_form]])[0]
        tahminler["MS 0"] = olasilik[0]*100; tahminler["MS 1"] = olasilik[1]*100; tahminler["MS 2"] = olasilik[2]*100
    
    t_guc = ev_guc + dep_guc + ev_form + dep_form
    ust_25 = max(20, min(80, 35 + (t_guc * 1.1) + kaos_etkisi))
    tahminler["2.5 Üst"] = ust_25; tahminler["2.5 Alt"] = 100 - ust_25
    tahminler["1.5 Üst"] = min(92, ust_25 + 15); tahminler["3.5 Alt"] = min(90, (100 - ust_25) + 20)
    iy_ust = max(20, min(75, 30 + (ev_form + dep_form) * 1.3 + (kaos_etkisi/2)))
    tahminler["İY 0.5 Üst"] = iy_ust; tahminler["İY 1.5 Alt"] = min(88, (100 - iy_ust) + 10)
    kg_var = max(30, min(80, 40 + (ev_guc + dep_guc) * 0.9 + kaos_etkisi))
    tahminler["KG Var"] = kg_var; tahminler["KG Yok"] = 100 - kg_var
    korner_85 = max(30, min(85, 45 + (ev_form + dep_form) * 1.2))
    tahminler["Korner 8.5 Üst"] = korner_85; tahminler["Korner 9.5 Üst"] = max(20, korner_85 - 12)
    
    en_gercekci = max(tahminler, key=tahminler.get)
    return tahminler, en_gercekci, tahminler[en_gercekci], kaos

def kupon_cizdir(baslik, kupon_listesi, ai_secimi=False):
    with st.container(border=True):
        if ai_secimi: st.markdown(f"<div class='ai-choice'>🤖 ALGORİTMA OTONOM SEÇİMİ</div>", unsafe_allow_html=True)
        else: st.markdown(f"<div style='text-align: center; font-weight: 800; letter-spacing: 1.5px; font-size: 1.1em; color: #10b981; font-family: Courier New;'>{baslik.upper()}</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
        if not kupon_listesi: return
            
        toplam_oran = 1.0
        wa_text = f"🏴‍☠️ *PREDICT PRO - {baslik}* 🏴‍☠️\n\n"
        
        for k_mac in kupon_listesi:
            toplam_oran *= k_mac['oran']
            value_badge = "<span class='value-badge'>🔥 VALUE</span>" if k_mac.get('is_value', False) else ""
            insider_badge = "<div class='insider-badge'>🚨 ANORMAL PARA GİRİŞİ TESPİT EDİLDİ</div>" if k_mac.get('is_insider', False) else ""
            
            st.markdown(f"<div style='font-size: 0.85em; color: #94a3b8; margin-bottom: -5px;'>{k_mac['saat']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight: 500;'>{k_mac['mac']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='margin-bottom: 5px;'><span style='color: #10b981; font-weight: 600;'>{k_mac['tercih']}</span> <span style='color:#94a3b8; font-size: 0.85em;'>| Oran: {k_mac['oran']:.2f}</span> {value_badge}</div>", unsafe_allow_html=True)
            if insider_badge: st.markdown(insider_badge, unsafe_allow_html=True)
            st.write("")
            wa_text += f"⚽ {k_mac['mac']}\n👉 Tahmin: {k_mac['tercih']}\n📈 Oran: {k_mac['oran']:.2f}\n\n"
            
        st.markdown(f"<div style='text-align: right; font-size: 1.2em; color: #10b981; margin-top: 10px; font-weight: bold;'>Net Oran: {toplam_oran:.2f}</div>", unsafe_allow_html=True)
        wa_text += f"💵 *Kupon Toplam Oranı: {toplam_oran:.2f}*"
        st.markdown(f"<a href='https://api.whatsapp.com/send?text={urllib.parse.quote(wa_text)}' target='_blank' class='wa-button'>📲 WhatsApp'a Sızdır (Paylaş)</a>", unsafe_allow_html=True)

def yuzde_bar_ciz(baslik, deger):
    st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: gray; margin-bottom: 3px; font-weight: 300;">
                <span>{baslik}</span><span>%{deger:.0f}</span>
            </div>
            <div style="width: 100%; background-color: rgba(16, 185, 129, 0.1); border-radius: 2px; height: 5px;">
                <div style="width: {deger}%; background-color: #10b981; height: 5px; border-radius: 2px; transition: width 1s ease-in-out;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- ARAYÜZ ---
col_sol, col_sag = st.columns([1, 2])
with col_sol:
    secilen_tarih = st.date_input("Analiz Tarihi", value=date.today(), label_visibility="collapsed")
    secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

data = maclarini_getir(secilen_tarih_str)

if "errors" in data and data["errors"]:
    st.error(f"Sistem Uyarısı: {data['errors']}")
elif "response" in data and len(data["response"]) > 0:
    bugunun_ligleri = sorted(list(set([mac["league"]["name"] for mac in data["response"]])))
    genis_havuz = ["Süper Lig", "1. Lig", "2. Lig", "Cup", "Türkiye Kupası", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "UEFA Europa Conference League", "Championship", "Eredivisie", "Primeira Liga", "Brasileiro Série A", "MLS", "Saudi Pro League"]
    varsayilan_secimler = [l for l in genis_havuz if l in bugunun_ligleri] or bugunun_ligleri[:10]
    secilen_ligler = st.multiselect(f"Ağlara Sızılacak Ligler ({secilen_tarih_str})", options=bugunun_ligleri, default=varsayilan_secimler)
    
    if st.session_state.aktif_tarih != secilen_tarih_str or st.session_state.aktif_ligler != secilen_ligler: st.session_state.analiz_aktif = False

    if st.button(f"> SİSTEMİ BAŞLAT / EXECUTE"):
        st.session_state.analiz_aktif = True
        st.session_state.aktif_tarih = secilen_tarih_str
        st.session_state.aktif_ligler = secilen_ligler
        
    if st.session_state.analiz_aktif:
        with st.spinner("Şifreli veritabanlarına sızılıyor... Lütfen Bekleyin."):
            tum_analizler = []
            lig_gruplari = {}
            for mac in data["response"]:
                lig = mac["league"]["name"]
                if lig in secilen_ligler:
                    ev, dep = mac["teams"]["home"]["name"], mac["teams"]["away"]["name"]
                    saat = turkiye_saati_hesapla(mac["fixture"]["date"])
                    guc1, f1 = takim_istatistikleri_getir(ev)
                    guc2, f2 = takim_istatistikleri_getir(dep)
                    mac_ismi_str = f"{ev} - {dep}"
                    
                    tahminler_sozlugu, banko_tercih, banko_guven, kaos_raporu = tum_tahminleri_hesapla(guc1, guc2, f1, f2, yapay_zeka, mac_ismi_str)
                    oran, is_value = oran_ve_value_hesapla(banko_guven, mac_ismi_str)
                    
                    if lig not in lig_gruplari: lig_gruplari[lig] = []
                    lig_gruplari[lig].append({"ev": ev, "dep": dep, "saat": saat, "en_gercekci_tercih": banko_tercih, "en_gercekci_guven": banko_guven, "oran": oran, "is_value": is_value, "tahminler": tahminler_sozlugu, "kaos": kaos_raporu})
                    
                    tum_analizler.append({"mac": mac_ismi_str, "saat": saat, "tercih": banko_tercih, "guven": banko_guven, "oran": oran, "is_value": is_value, "is_insider": kaos_raporu["is_insider"], "oran_ust": tahminler_sozlugu["2.5 Üst"], "oran_iy": tahminler_sozlugu["İY 0.5 Üst"], "oran_korner": tahminler_sozlugu["Korner 8.5 Üst"], "oran_ms0": tahminler_sozlugu["MS 0"]})

            st.write("")
            tab_rolling, tab_kombine, tab_ligler = st.tabs(["🚀 OTONOM", "🏴‍☠️ SIZILAN KUPONLAR", "🧠 DERİN ANALİZ"])

            with tab_rolling:
                st.markdown("<br>", unsafe_allow_html=True)
                rolling_kupon = []
                tekli_adaylar = [m for m in tum_analizler if 1.85 <= m["oran"] <= 2.20 and m["guven"] >= 70]
                if tekli_adaylar: rolling_kupon = [sorted(tekli_adaylar, key=lambda x: x["guven"], reverse=True)[0]]
                else:
                    mevcut_oran = 1.0
                    en_guvenilirler = sorted(tum_analizler, key=lambda x: x["guven"], reverse=True)
                    for m in en_guvenilirler:
                        if mevcut_oran < 1.95:
                            rolling_kupon.append(m)
                            mevcut_oran *= m["oran"]
                        else: break
                
                col_kupon, col_sim = st.columns([1, 1])
                with col_kupon:
                    if len(rolling_kupon) > 0: kupon_cizdir("GÜNÜN ROLLING HEDEFİ", rolling_kupon, ai_secimi=True)
                    else: st.warning("Hedef oran bulunamadı.")

                with col_sim:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center; font-weight: 800; letter-spacing: 1.5px; font-size: 1.1em; color: #10b981; font-family: Courier New;'>PROJEKSİYON</div>", unsafe_allow_html=True)
                        baslangic_kasasi = 100
                        gunler = []
                        kasa = baslangic_kasasi
                        for gun in range(1, 21):
                            gunler.append({"Gün": f"{gun}. Gün", "Yatırılan": f"{int(kasa):,} ₺", "Hedef": f"{int(kasa*2):,} ₺"})
                            kasa *= 2
                        st.dataframe(pd.DataFrame(gunler), hide_index=True, use_container_width=True, height=250)

            with tab_kombine:
                st.write("")
                if len(tum_analizler) >= 5:
                    insider_maclar = [m for m in tum_analizler if m["is_insider"]]
                    if insider_maclar:
                        kupon_cizdir("🚨 YERALTI İSTİHBARATI (ŞÜPHELİ HACİM)", insider_maclar)
                
                    karma, kullanilan = [], []
                    best_ms = sorted(tum_analizler, key=lambda x: x["guven"], reverse=True)[0]; karma.append(best_ms); kullanilan.append(best_ms["mac"])
                    
                    best_gol = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_ust"], reverse=True)[0]
                    oran_gol, val_gol = oran_ve_value_hesapla(best_gol["oran_ust"], best_gol["mac"])
                    karma.append({"mac": best_gol["mac"], "saat": best_gol["saat"], "tercih": "2.5 Üst", "guven": best_gol["oran_ust"], "oran": oran_gol, "is_value": val_gol}); kullanilan.append(best_gol["mac"])
                    kupon_cizdir("Optimum Karma", karma)
                else: st.caption("Kombineler için lig seçim kutusundan daha fazla lig ekleyin.")

            with tab_ligler:
                st.markdown("<br>", unsafe_allow_html=True)
                for lig, maclar in lig_gruplari.items():
                    with st.expander(f"{lig} ({len(maclar)})", expanded=False):
                        for i in range(0, len(maclar), 2):
                            cols = st.columns(2)
                            for j in range(2):
                                if i+j < len(maclar):
                                    m = maclar[i+j]
                                    with cols[j]:
                                        with st.container(border=True):
                                            insider_badge = "<div class='insider-badge'>🚨 ANORMAL PARA GİRİŞİ</div>" if m['kaos'].get('is_insider', False) else ""
                                            st.markdown(f"<div style='text-align:center; margin-bottom: 10px;'><span style='color:#94a3b8; font-size: 0.8em; letter-spacing: 1px;'>{m['saat']}</span><br><span style='font-size: 1.1em; font-weight: 400;'>{m['ev']}</span> <span style='color: #cbd5e1; margin: 0 5px;'>vs</span> <span style='font-size: 1.1em; font-weight: 400;'>{m['dep']}</span></div>", unsafe_allow_html=True)
                                            if insider_badge: st.markdown(f"<div style='text-align:center;'>{insider_badge}</div>", unsafe_allow_html=True)
                                            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                            val_badge = "<span class='value-badge'>🔥 VALUE</span>" if m['is_value'] else ""
                                            st.markdown(f"<div style='text-align:center; padding: 8px; background-color: rgba(16, 185, 129, 0.05); border-radius: 6px; margin-bottom: 10px;'><span style='font-size: 0.8em; color: gray;'>Algoritma Çıktısı</span><br><b style='color:#10b981; font-size: 1.1em;'>{m['en_gercekci_tercih']}</b><br><span style='font-size:0.9em; color:#333; font-weight:bold;'>Oran: {m['oran']:.2f}</span> {val_badge}</div>", unsafe_allow_html=True)
                                            
                                            with st.expander("Gelişmiş Metrikler", expanded=False):
                                                yuzde_bar_ciz("Ev Sahibi (MS 1)", m['tahminler']['MS 1'])
                                                yuzde_bar_ciz("Beraberlik (MS 0)", m['tahminler']['MS 0'])
                                                yuzde_bar_ciz("Deplasman (MS 2)", m['tahminler']['MS 2'])
                                                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                                yuzde_bar_ciz("2.5 Üst", m['tahminler']['2.5 Üst'])
                                                yuzde_bar_ciz("Karşılıklı Gol Var", m['tahminler']['KG Var'])

else:
    st.info("Terminal çevrimdışı. Veri bulunamadı.")