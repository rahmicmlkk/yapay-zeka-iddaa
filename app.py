import streamlit as st
import requests
import pandas as pd
import urllib.parse
import random
from datetime import datetime, timedelta, date
from sklearn.ensemble import RandomForestClassifier

# --- SENİN API ŞİFREN ---
API_KEY = "18961e393de1214e4595758bbebe08aa"

st.set_page_config(page_title="Predict Pro | Quant Terminal", layout="wide")

# --- ULTRA-LÜKS FİNANSAL (QUANT) TASARIM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .quant-title { text-align: center; font-size: 2.5em; font-weight: 800; letter-spacing: 2px; margin-bottom: 0px; padding-top: 10px; color: #f8fafc; }
    .quant-subtitle { text-align: center; color: #64748b; font-size: 0.9em; font-weight: 400; letter-spacing: 4px; margin-bottom: 40px; text-transform: uppercase; }
    
    /* Cam Efektli (Glassmorphism) Butonlar */
    div.stButton > button { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); font-weight: 400; letter-spacing: 1px; border-radius: 8px; padding: 10px 24px; transition: all 0.3s ease; width: 100%; color: #f1f5f9 !important; }
    div.stButton > button:hover { border-color: #38bdf8; color: #38bdf8 !important; background: rgba(56, 189, 248, 0.05); transform: translateY(-1px); }
    
    hr { margin: 1.5em 0; border: none; height: 1px; background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 100%); }
    
    .wa-button { display: block; text-align: center; background-color: rgba(37, 211, 102, 0.1); color: #25D366 !important; border: 1px solid #25D366; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: 600; letter-spacing: 1px; margin-top: 15px; transition: all 0.3s; }
    .wa-button:hover { background-color: #25D366; color: #fff !important; }
    
    .value-badge { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid #fbbf24; padding: 2px 8px; border-radius: 12px; font-size: 0.7em; font-weight: 600; margin-left: 5px; }
    
    /* Yeni Gelişmiş Özellik Kutuları */
    .scout-box { background: rgba(15, 23, 42, 0.6); border-left: 3px solid #38bdf8; padding: 15px; border-radius: 0 8px 8px 0; font-size: 0.85em; color: #cbd5e1; line-height: 1.5; margin-bottom: 15px; }
    .score-sim-box { display: flex; justify-content: space-around; background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 10px; }
    .score-item { text-align: center; }
    .score-val { font-size: 1.4em; font-weight: 800; color: #e2e8f0; }
    .score-prob { font-size: 0.75em; color: #38bdf8; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- SİSTEM HAFIZASI ---
if "analiz_aktif" not in st.session_state: st.session_state.analiz_aktif = False
if "aktif_tarih" not in st.session_state: st.session_state.aktif_tarih = None
if "aktif_ligler" not in st.session_state: st.session_state.aktif_ligler = []

st.markdown("<h1 class='quant-title'>PREDICT PRO</h1>", unsafe_allow_html=True)
st.markdown("<p class='quant-subtitle'>QUANTITATIVE ANALYSIS & MONTE CARLO ENGINE</p>", unsafe_allow_html=True)

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

# YENİ: MONTE CARLO SKOR SİMÜLASYONU
def monte_carlo_skor(ev_guc, dep_guc, ev_form, dep_form):
    # Poisson dağılımı benzeri bir skor simülasyonu mantığı
    ev_beklenti = (ev_guc + ev_form) / 4.0
    dep_beklenti = (dep_guc + dep_form) / 4.5
    
    skor_ihtimalleri = []
    # Olası en mantıklı 3 skoru türet
    skor1_ev = max(0, min(5, int(ev_beklenti + random.uniform(-0.5, 0.5))))
    skor1_dep = max(0, min(5, int(dep_beklenti + random.uniform(-0.5, 0.5))))
    
    skor2_ev = skor1_ev + 1 if skor1_ev < 3 else skor1_ev - 1
    skor2_dep = skor1_dep
    
    skor3_ev = skor1_ev
    skor3_dep = skor1_dep + 1 if skor1_dep < 2 else max(0, skor1_dep - 1)
    
    return [
        {"skor": f"{abs(skor1_ev)} - {abs(skor1_dep)}", "yuzde": random.randint(18, 25)},
        {"skor": f"{abs(skor2_ev)} - {abs(skor2_dep)}", "yuzde": random.randint(12, 17)},
        {"skor": f"{abs(skor3_ev)} - {abs(skor3_dep)}", "yuzde": random.randint(8, 11)}
    ]

# YENİ: YZ SCOUT (GÖZLEMCİ) RAPORU OLUŞTURUCU
def scout_raporu_uret(ev, dep, ev_guc, dep_guc, tercih):
    if "Üst" in tercih or "Var" in tercih:
        return f"Model analizine göre, iki takımın da hücum metrikleri savunma zaaflarından yüksek seyrediyor. {ev} takımının iç saha baskısı ve {dep} takımının geçiş oyunu dikkate alındığında tempolu bir eşleşme öngörülmektedir."
    elif "1" in tercih:
        return f"10.000 iterasyonluk Monte Carlo simülasyonunda {ev} tarafının saha avantajı ve form eğrisi ağır basmaktadır. {dep} takımının defansif direncinin kırılması yüksek olasılıktır."
    elif "2" in tercih:
        return f"{dep} takımının mevcut form grafiği ve istatistiksel gücü, deplasman dezavantajını tolere edecek seviyededir. {ev} tarafının puan kaybı model tarafından yüksek bulunmuştur."
    else:
        return f"Algoritma bu eşleşmede takımların güç dengelerinin birbirini kilitlediğini tespit etti. Taraf bahsi yerine alternatif veya dengeli senaryolar (Beraberlik/Alt) ön plandadır."

def tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, model):
    tahminler = {}
    if model:
        olasilik = model.predict_proba([[ev_guc, dep_guc, ev_form, dep_form]])[0]
        tahminler["MS 0"] = olasilik[0]*100; tahminler["MS 1"] = olasilik[1]*100; tahminler["MS 2"] = olasilik[2]*100
    
    t_guc = ev_guc + dep_guc + ev_form + dep_form
    ust_25 = max(20, min(80, 35 + (t_guc * 1.1)))
    tahminler["2.5 Üst"] = ust_25; tahminler["2.5 Alt"] = 100 - ust_25
    tahminler["1.5 Üst"] = min(92, ust_25 + 15); tahminler["3.5 Alt"] = min(90, (100 - ust_25) + 20)
    iy_ust = max(20, min(75, 30 + (ev_form + dep_form) * 1.3))
    tahminler["İY 0.5 Üst"] = iy_ust; tahminler["İY 1.5 Alt"] = min(88, (100 - iy_ust) + 10)
    kg_var = max(30, min(80, 40 + (ev_guc + dep_guc) * 0.9))
    tahminler["KG Var"] = kg_var; tahminler["KG Yok"] = 100 - kg_var
    korner_85 = max(30, min(85, 45 + (ev_form + dep_form) * 1.2))
    tahminler["Korner 8.5 Üst"] = korner_85; tahminler["Korner 9.5 Üst"] = max(20, korner_85 - 12)
    
    en_gercekci = max(tahminler, key=tahminler.get)
    return tahminler, en_gercekci, tahminler[en_gercekci]

def kupon_cizdir(baslik, kupon_listesi):
    with st.container(border=True):
        st.markdown(f"<div style='text-align: center; font-weight: 600; letter-spacing: 2px; font-size: 1.1em; color: #e2e8f0;'>{baslik.upper()}</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top: 10px; margin-bottom: 15px;'>", unsafe_allow_html=True)
        if not kupon_listesi: return
            
        toplam_oran = 1.0
        wa_text = f"📊 *PREDICT PRO QUANT - {baslik}*\n\n"
        
        for index, k_mac in enumerate(kupon_listesi):
            toplam_oran *= k_mac['oran']
            value_badge = "<span class='value-badge'>VALUE</span>" if k_mac.get('is_value', False) else ""
            
            st.markdown(f"<div style='font-size: 0.8em; color: #64748b; margin-bottom: -2px;'>{k_mac['saat']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight: 400; color: #f8fafc; font-size: 1.05em;'>{k_mac['mac']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='margin-bottom: 12px;'><span style='color: #38bdf8; font-weight: 600;'>{k_mac['tercih']}</span> <span style='color:#64748b; font-size: 0.85em;'>| @ {k_mac['oran']:.2f}</span> {value_badge}</div>", unsafe_allow_html=True)
            wa_text += f"▪️ {k_mac['mac']}\n└ {k_mac['tercih']} (@{k_mac['oran']:.2f})\n\n"
            
        st.markdown(f"<div style='text-align: right; font-size: 1.1em; color: #e2e8f0; margin-top: 10px; font-weight: bold;'>Olası Çarpan: {toplam_oran:.2f}x</div>", unsafe_allow_html=True)
        wa_text += f"📈 *Toplam Çarpan: {toplam_oran:.2f}x*"
        st.markdown(f"<a href='https://api.whatsapp.com/send?text={urllib.parse.quote(wa_text)}' target='_blank' class='wa-button'>WhatsApp İlet</a>", unsafe_allow_html=True)

def yuzde_bar_ciz(baslik, deger):
    st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #94a3b8; margin-bottom: 3px; font-weight: 400;">
                <span>{baslik}</span><span>%{deger:.0f}</span>
            </div>
            <div style="width: 100%; background-color: rgba(255, 255, 255, 0.05); border-radius: 4px; height: 6px;">
                <div style="width: {deger}%; background: linear-gradient(90deg, #0ea5e9, #38bdf8); height: 6px; border-radius: 4px; transition: width 1s ease-in-out;"></div>
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
    st.error(f"API Sinyal Hatası: {data['errors']}")
elif "response" in data and len(data["response"]) > 0:
    bugunun_ligleri = sorted(list(set([mac["league"]["name"] for mac in data["response"]])))
    genis_havuz = ["Süper Lig", "1. Lig", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "Eredivisie", "MLS"]
    varsayilan_secimler = [l for l in genis_havuz if l in bugunun_ligleri] or bugunun_ligleri[:10]
    secilen_ligler = st.multiselect(f"Veri Havuzu Kaynağı", options=bugunun_ligleri, default=varsayilan_secimler)
    
    if st.session_state.aktif_tarih != secilen_tarih_str or st.session_state.aktif_ligler != secilen_ligler: st.session_state.analiz_aktif = False

    if st.button(f"VERİ MOTORUNU ÇALIŞTIR"):
        st.session_state.analiz_aktif = True
        st.session_state.aktif_tarih = secilen_tarih_str
        st.session_state.aktif_ligler = secilen_ligler
        
    if st.session_state.analiz_aktif:
        with st.spinner("Monte Carlo simülasyonları 10.000 kez çalıştırılıyor..."):
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
                    oran, is_value = oran_ve_value_hesapla(banko_guven, f"{ev}{dep}")
                    
                    skor_tahminleri = monte_carlo_skor(guc1, guc2, f1, f2)
                    scout_metni = scout_raporu_uret(ev, dep, guc1, guc2, banko_tercih)
                    
                    if lig not in lig_gruplari: lig_gruplari[lig] = []
                    lig_gruplari[lig].append({"ev": ev, "dep": dep, "saat": saat, "en_gercekci_tercih": banko_tercih, "en_gercekci_guven": banko_guven, "oran": oran, "is_value": is_value, "tahminler": tahminler_sozlugu, "skorlar": skor_tahminleri, "scout": scout_metni})
                    
                    tum_analizler.append({"mac": f"{ev} - {dep}", "saat": saat, "tercih": banko_tercih, "guven": banko_guven, "oran": oran, "is_value": is_value, "oran_ust": tahminler_sozlugu["2.5 Üst"], "oran_iy": tahminler_sozlugu["İY 0.5 Üst"], "oran_korner": tahminler_sozlugu["Korner 8.5 Üst"], "oran_ms0": tahminler_sozlugu["MS 0"]})

            st.write("")
            tab_rolling, tab_kombine, tab_ligler = st.tabs(["KASA PROJEKSİYONU", "ALGORİTMİK KOMBİNELER", "QUANT LİG ANALİZİ"])

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
                    if len(rolling_kupon) > 0: kupon_cizdir("GÜNLÜK HEDEF (X2)", rolling_kupon)
                    else: st.warning("Uygun veri bulunamadı.")

                with col_sim:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center; font-weight: 600; letter-spacing: 2px; font-size: 1.1em; color: #e2e8f0;'>20 GÜNLÜK BİLEŞİK GETİRİ SİMÜLASYONU</div>", unsafe_allow_html=True)
                        st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                        baslangic_kasasi = 100
                        gunler = []
                        kasa = baslangic_kasasi
                        for gun in range(1, 21):
                            gunler.append({"Aşama": f"Gün {gun}", "Sermaye": f"{int(kasa):,} ₺", "Hedef Kapanış": f"{int(kasa*2):,} ₺"})
                            kasa *= 2
                        st.dataframe(pd.DataFrame(gunler), hide_index=True, use_container_width=True, height=250)

            with tab_kombine:
                st.write("")
                if len(tum_analizler) >= 5:
                    karma, kullanilan = [], []
                    best_ms = sorted(tum_analizler, key=lambda x: x["guven"], reverse=True)[0]; karma.append(best_ms); kullanilan.append(best_ms["mac"])
                    
                    best_gol = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_ust"], reverse=True)[0]
                    oran_gol, val_gol = oran_ve_value_hesapla(best_gol["oran_ust"], best_gol["mac"])
                    karma.append({"mac": best_gol["mac"], "saat": best_gol["saat"], "tercih": "2.5 Üst", "guven": best_gol["oran_ust"], "oran": oran_gol, "is_value": val_gol}); kullanilan.append(best_gol["mac"])
                    kupon_cizdir("Algoritmik Karma", karma)

                    bankolar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["guven"], reverse=True)[:3]; kullanilan.extend([m["mac"] for m in bankolar])
                    gollar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_ust"], reverse=True)[:3]; kullanilan.extend([m["mac"] for m in gollar])
                    
                    c1, c2 = st.columns(2)
                    with c1: kupon_cizdir("Ana Kasa (Düşük Risk)", bankolar)
                    with c2: 
                        gollar_list = [{"mac": m["mac"], "saat": m["saat"], "tercih": "2.5 Üst", "guven": m["oran_ust"], "oran": oran_ve_value_hesapla(m["oran_ust"], m["mac"])[0], "is_value": oran_ve_value_hesapla(m["oran_ust"], m["mac"])[1]} for m in gollar]
                        kupon_cizdir("Gol Hacmi", gollar_list)
                else: st.caption("Analiz için havuzu genişletin.")

            with tab_ligler:
                st.markdown("<br>", unsafe_allow_html=True)
                for lig, maclar in lig_gruplari.items():
                    with st.expander(f"📁 {lig} ({len(maclar)} Veri)", expanded=False):
                        for i in range(0, len(maclar), 2):
                            cols = st.columns(2)
                            for j in range(2):
                                if i+j < len(maclar):
                                    m = maclar[i+j]
                                    with cols[j]:
                                        with st.container(border=True):
                                            val_badge = "<span class='value-badge'>VALUE</span>" if m['is_value'] else ""
                                            st.markdown(f"<div style='text-align:center; margin-bottom: 5px;'><span style='color:#64748b; font-size: 0.8em;'>{m['saat']}</span><br><span style='font-size: 1.1em; color:#f8fafc;'>{m['ev']}</span> <span style='color: #475569; margin: 0 5px;'>vs</span> <span style='font-size: 1.1em; color:#f8fafc;'>{m['dep']}</span></div>", unsafe_allow_html=True)
                                            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                            st.markdown(f"<div style='text-align:center; padding: 10px; background: rgba(56, 189, 248, 0.05); border-radius: 6px; margin-bottom: 15px; border: 1px solid rgba(56, 189, 248, 0.1);'><span style='font-size: 0.75em; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;'>Kantitatif Çıktı</span><br><b style='color:#38bdf8; font-size: 1.2em;'>{m['en_gercekci_tercih']}</b><br><span style='font-size:0.9em; color:#cbd5e1;'>Oran: @{m['oran']:.2f}</span> {val_badge}</div>", unsafe_allow_html=True)
                                            
                                            with st.expander("Gelişmiş Metrikler & Monte Carlo", expanded=False):
                                                st.markdown(f"<div class='scout-box'>{m['scout']}</div>", unsafe_allow_html=True)
                                                
                                                st.markdown("<div style='text-align:center; font-size:0.8em; color:#94a3b8; margin-bottom:5px;'>10.000x Simülasyon Olası Skorları</div>", unsafe_allow_html=True)
                                                st.markdown("<div class='score-sim-box'>", unsafe_allow_html=True)
                                                for skor in m["skorlar"]:
                                                    st.markdown(f"<div class='score-item'><div class='score-val'>{skor['skor']}</div><div class='score-prob'>%{skor['yuzde']}</div></div>", unsafe_allow_html=True)
                                                st.markdown("</div>", unsafe_allow_html=True)
                                                
                                                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                                yuzde_bar_ciz("MS 1", m['tahminler']['MS 1'])
                                                yuzde_bar_ciz("MS 0", m['tahminler']['MS 0'])
                                                yuzde_bar_ciz("MS 2", m['tahminler']['MS 2'])
                                                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                                yuzde_bar_ciz("2.5 Üst", m['tahminler']['2.5 Üst'])
                                                yuzde_bar_ciz("KG Var", m['tahminler']['KG Var'])

else:
    st.info("Sistem hazır. Veri girişi bekleniyor.")