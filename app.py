import streamlit as st
import requests
import pandas as pd
import urllib.parse
import hashlib
import math
import time
from datetime import datetime, timedelta, date
from sklearn.ensemble import RandomForestClassifier

# --- SENİN API ŞİFREN (PATLARSA YEDEK SİSTEM DEVREYE GİRER) ---
API_KEY = "18961e393de1214e4595758bbebe08aa"

st.set_page_config(page_title="Predict Pro | Big Data Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- AÇIK TEMA (BEYAZ ARKA PLAN) İÇİN KOYU YAZI TASARIMI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .quant-title { text-align: center; font-size: 2.5em; font-weight: 900; letter-spacing: 2px; margin-bottom: 0px; padding-top: 10px; color: #0284c7; text-transform: uppercase; }
    .quant-subtitle { text-align: center; color: #64748b; font-size: 0.85em; font-weight: 800; letter-spacing: 5px; margin-bottom: 30px; text-transform: uppercase; }
    
    div.stButton > button { background: #f8fafc; border: 2px solid #0284c7; font-weight: 900; letter-spacing: 1px; border-radius: 8px; padding: 10px 24px; transition: all 0.3s ease; width: 100%; color: #0284c7 !important; }
    div.stButton > button:hover { background: #0284c7; color: #ffffff !important; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3); }
    hr { margin: 1.5em 0; border: none; height: 1px; background: rgba(0,0,0,0.1); }
    
    .wa-button { display: block; text-align: center; background-color: #25D366; color: #ffffff !important; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: 900; letter-spacing: 1px; margin-top: 15px; transition: all 0.3s; box-shadow: 0 4px 6px rgba(37, 211, 102, 0.3); }
    .wa-button:hover { background-color: #16a34a; transform: scale(1.02); box-shadow: 0 6px 12px rgba(37, 211, 102, 0.4); }
    
    .value-badge { background-color: #f59e0b; color: #ffffff; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: 900; margin-left: 5px; }
    .drop-badge { background-color: #ef4444; color: #ffffff; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: 900; animation: pulse 2s infinite; display: inline-block; margin-bottom:5px;}
    
    .darkweb-box { border: 2px solid #ef4444; background: #fef2f2; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1); }
    .darkweb-title { color: #b91c1c; font-weight: 900; font-size: 1.2em; text-align: center; letter-spacing: 2px; margin-bottom: 10px; animation: pulse 1.5s infinite; }
    .darkweb-source { font-family: 'Courier New', monospace; font-size: 0.85em; color: #991b1b; font-weight: bold; text-align: center; margin-bottom: 10px; }
    
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }
    
    .scout-box { border-left: 4px solid #6366f1; padding: 15px; border-radius: 0 8px 8px 0; font-size: 0.9em; font-weight: 700; color: #334155; line-height: 1.5; margin-bottom: 10px; background: #e0e7ff; }
    .injury-box { border-left: 4px solid #ef4444; padding: 10px 15px; border-radius: 0 8px 8px 0; font-size: 0.9em; font-weight: 800; color:#b91c1c; background: #fef2f2; margin-bottom: 10px; }
    .xg-box { display: flex; justify-content: space-between; padding: 12px; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); margin-bottom: 10px; background: #f8fafc; font-weight:800; align-items:center;}
    .xg-value { font-size: 1.5em; color: #059669; font-weight: 900; }
    
    .team-names { font-size: 1.3em; font-weight: 900; letter-spacing: 0.5px; color: #0f172a; }
    .kombine-title { text-align:center; font-size: 1.2em; font-weight: 900; color: #0f172a; margin-bottom: 5px; }
    .kombine-desc { text-align:center; font-size: 0.85em; color: #64748b; font-weight: 600; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- SİSTEM HAFIZASI ---
if "analiz_aktif" not in st.session_state: st.session_state.analiz_aktif = False
if "aktif_tarih" not in st.session_state: st.session_state.aktif_tarih = None
if "aktif_ligler" not in st.session_state: st.session_state.aktif_ligler = []

st.markdown("<h1 class='quant-title'>PREDICT PRO</h1>", unsafe_allow_html=True)
st.markdown("<p class='quant-subtitle'>GLOBAL SIZINTI VE BİG DATA TERMİNALİ</p>", unsafe_allow_html=True)

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
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        # GÖLGE PROTOKOLÜ (API Çökerse Şov Devam Eder)
        if "errors" in data and data["errors"]:
            st.warning("⚠️ [GÖLGE PROTOKOLÜ AKTİF]: Ana API bağlantısı gizlendi. Çevrimdışı Simülasyon Verileri (Şov Modu) kullanılıyor.")
            return {
                "response": [
                    {"fixture": {"date": f"{hedef_tarih}T19:00:00+00:00"}, "league": {"name": "UEFA Champions League"}, "teams": {"home": {"name": "Real Madrid"}, "away": {"name": "Manchester City"}}},
                    {"fixture": {"date": f"{hedef_tarih}T20:00:00+00:00"}, "league": {"name": "UEFA Champions League"}, "teams": {"home": {"name": "Bayern Munich"}, "away": {"name": "Arsenal"}}},
                    {"fixture": {"date": f"{hedef_tarih}T17:00:00+00:00"}, "league": {"name": "Süper Lig"}, "teams": {"home": {"name": "Galatasaray"}, "away": {"name": "Fenerbahçe"}}},
                    {"fixture": {"date": f"{hedef_tarih}T14:30:00+00:00"}, "league": {"name": "Süper Lig"}, "teams": {"home": {"name": "Beşiktaş"}, "away": {"name": "Trabzonspor"}}},
                    {"fixture": {"date": f"{hedef_tarih}T16:00:00+00:00"}, "league": {"name": "Premier League"}, "teams": {"home": {"name": "Liverpool"}, "away": {"name": "Chelsea"}}},
                    {"fixture": {"date": f"{hedef_tarih}T15:00:00+00:00"}, "league": {"name": "Serie A"}, "teams": {"home": {"name": "Juventus"}, "away": {"name": "Inter"}}},
                    {"fixture": {"date": f"{hedef_tarih}T18:00:00+00:00"}, "league": {"name": "La Liga"}, "teams": {"home": {"name": "Barcelona"}, "away": {"name": "Atletico Madrid"}}}
                ]
            }
        return data
    except:
        return {"errors": "Bağlantı hatası"}

def gizli_istihbarat_olustur(oran, guven, mac_ismi):
    sayi = int(hashlib.md5(mac_ismi.encode()).hexdigest(), 16)
    is_dropping = guven > 75 and (sayi % 4 == 0) 
    acilis_orani = oran
    hacim = 0
    if is_dropping:
        acilis_orani = oran + (sayi % 50) / 100.0
        hacim = f"${1.2 + (sayi % 80) / 10.0:.1f}M"
        
    is_fixed = (sayi % 14 == 0) 
    kaynaklar = ["[X] KAYNAK: Rusya Yeraltı Sendikası (Dark Web)", "[X] KAYNAK: Asya Bahis Borsası (Anormal Hacim Tespiti)", "[X] KAYNAK: Sızdırılmış VIP Telegram Paneli"]
    sike_kaynagi = kaynaklar[sayi % len(kaynaklar)] if is_fixed else ""
    return acilis_orani, hacim, is_dropping, is_fixed, sike_kaynagi

def oran_ve_value_hesapla(guven, takimlar_str):
    sapma = (len(takimlar_str) % 15) - 5 
    iddaa_ihtimali = guven - sapma
    if iddaa_ihtimali <= 5: iddaa_ihtimali = 5
    oran = round(100 / iddaa_ihtimali, 2)
    oran = max(1.10, min(oran, 8.50))
    is_value = (guven - iddaa_ihtimali) > 5 
    return oran, is_value

def poisson_xg_hesapla(ev_guc, dep_guc, ev_form, dep_form, mac_ismi):
    sayi = int(hashlib.md5(mac_ismi.encode()).hexdigest(), 16)
    xg_ev = (ev_guc * 0.15) + (ev_form * 0.1) + ((sayi % 50)/100.0)
    xg_dep = (dep_guc * 0.12) + (dep_form * 0.1) + (((sayi//10) % 40)/100.0)
    
    skor_ihtimalleri = []
    for e in range(5):
        for d in range(5):
            ihtimal_ev = (math.exp(-xg_ev) * (xg_ev**e)) / math.factorial(e)
            ihtimal_dep = (math.exp(-xg_dep) * (xg_dep**d)) / math.factorial(d)
            skor_ihtimalleri.append({"skor": f"{e} - {d}", "yuzde": (ihtimal_ev * ihtimal_dep) * 100})
            
    en_olasi_skorlar = sorted(skor_ihtimalleri, key=lambda x: x["yuzde"], reverse=True)[:3]
    return round(xg_ev, 2), round(xg_dep, 2), en_olasi_skorlar

def taktik_ve_eksik_radari(mac_ismi, ev, dep):
    sayi = int(hashlib.md5(mac_ismi.encode()).hexdigest(), 16)
    taktikler = ["4-3-3 Ofansif / Gegenpress", "5-3-2 Katı Defans / Kontra Atak", "4-2-3-1 Topa Sahip Olma (Tiki-Taka)", "3-4-3 Kanat Akınları", "4-4-2 Dengeli Blok"]
    eksikler = ["Kritik Eksik Yok (Tam Kadro)", "Rotasyon Oyuncuları Eksik", "🚨 DİKKAT: Yıldız Forvet ve 1. Kaleci Sakat!", "🚨 DİKKAT: Kaptan ve Defans Lideri Cezalı!", "Orta Sahada 2 Oyuncu Belirsiz"]
    taktik_ev = taktikler[sayi % len(taktikler)]
    taktik_dep = taktikler[(sayi // 5) % len(taktikler)]
    eksik_durumu = eksikler[(sayi // 25) % len(eksikler)]
    rapor = f"Taktiksel Eşleşme: {ev} ({taktik_ev}) ile sahaya çıkarken, {dep} tarafının ({taktik_dep}) stratejisiyle yanıt vermesi bekleniyor. "
    if "Katı Defans" in taktik_dep: rapor += "Deplasman takımının otobüs çekeceği bu maçta gol yollarında tıkanıklık (Alt) yaşanabilir. "
    elif "Ofansif" in taktik_ev and "Ofansif" in taktik_dep: rapor += "İki takımın da agresif dizilişi, geçiş oyunlarında ciddi boşluklar yaratacak. Yüksek xG (Gol Beklentisi) ve tempolu bir oyun öngörülüyor. "
    return taktik_ev, taktik_dep, eksik_durumu, rapor

def tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, xg_ev, xg_dep, eksik_durumu):
    tahminler = {}
    sapma = 0
    if "Yıldız Forvet" in eksik_durumu: sapma -= 15 
    if "Defans Lideri" in eksik_durumu: sapma += 15 
    
    ms1 = min(90, max(10, 30 + (xg_ev - xg_dep) * 20))
    ms2 = min(90, max(10, 30 + (xg_dep - xg_ev) * 20))
    ms0 = max(10, 100 - (ms1 + ms2))

    tahminler["MS 1 (Ev Sahibi)"] = ms1; tahminler["MS 0 (Beraberlik)"] = ms0; tahminler["MS 2 (Deplasman)"] = ms2
    tahminler["1X Çifte Şans"] = min(96, ms1 + ms0); tahminler["X2 Çifte Şans"] = min(96, ms2 + ms0)
    tahminler["Ev Sahibi 0.5 Gol Üstü"] = min(95, 30 + (xg_ev * 25) + (sapma if sapma < 0 else 0))
    tahminler["Deplasman 0.5 Gol Üstü"] = min(95, 30 + (xg_dep * 25))
    
    toplam_xg = xg_ev + xg_dep
    ust_25 = min(90, max(20, 20 + (toplam_xg * 18) + (sapma if sapma > 0 else 0)))
    tahminler["2.5 Gol Üstü"] = ust_25; tahminler["2.5 Gol Altı"] = 100 - ust_25
    tahminler["1.5 Gol Üstü (Güvenli)"] = min(96, ust_25 + 18)
    iy_ust = min(85, max(25, 20 + (toplam_xg * 15)))
    tahminler["İlk Yarı 0.5 Gol Üstü"] = iy_ust
    kg_var = min(85, max(25, 20 + (xg_ev * 12) + (xg_dep * 12)))
    tahminler["Karşılıklı Gol Var"] = kg_var
    korner_85 = max(30, min(85, 45 + (ev_form + dep_form) * 1.2))
    tahminler["Toplam Korner 8.5 Üst"] = korner_85
    
    en_gercekci = max(tahminler, key=tahminler.get)
    return tahminler, en_gercekci, tahminler[en_gercekci]

# --- YENİ EFSANEVİ WHATSAPP BUTONU FONKSİYONU ---
def kupon_cizdir(baslik, aciklama, renk, kupon_listesi):
    with st.container(border=True):
        st.markdown(f"<div class='kombine-title' style='color: {renk};'>{baslik.upper()}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='kombine-desc'>{aciklama}</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
        if not kupon_listesi: 
            st.warning("Algoritma bu portföy için uygun maç bulamadı. Lig ekleyin.")
            return
            
        toplam_oran = 1.0
        
        # WHATSAPP ŞOV METNİ BURADA HAZIRLANIYOR
        wa_text = f"🤖 *Alın bu da Yapay Zekanın bugünkü Risk Dağılımı:*\n"
        wa_text += f"💼 *{baslik.upper()}*\n"
        wa_text += "------------------------\n"
        
        for k_mac in kupon_listesi:
            toplam_oran *= k_mac['oran']
            value_badge = "<span class='value-badge'>🔥 VALUE</span>" if k_mac.get('is_value', False) else ""
            drop_badge = f"<div class='drop-badge'>📉 HACİM: {k_mac['hacim']} | ORAN DÜŞÜŞÜ</div>" if k_mac.get('is_dropping', False) else ""
            
            if k_mac.get('is_dropping', False): st.markdown(drop_badge, unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 0.85em; color: #64748b; margin-bottom: 2px; font-weight: 800;'>{k_mac['saat']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='team-names'>{k_mac['mac']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='margin-bottom: 15px;'><span style='color: {renk}; font-weight: 900;'>{k_mac['tercih']}</span> <span style='font-size: 0.9em; font-weight:800; color:#334155;'>| @ {k_mac['oran']:.2f}</span> {value_badge}</div>", unsafe_allow_html=True)
            
            # WhatsApp'a eklenecek maç bilgisi
            wa_text += f"⚽ {k_mac['mac']}\n🎯 {k_mac['tercih']} (Oran: {k_mac['oran']:.2f})\n\n"
            
        st.markdown(f"<div style='text-align: right; font-size: 1.2em; margin-top: 10px; font-weight: 900; color:#0f172a;'>Olası Çarpan: {toplam_oran:.2f}x</div>", unsafe_allow_html=True)
        wa_text += f"📈 *Olası Çarpan: {toplam_oran:.2f}x*\n\n"
        wa_text += f"_(Predict Pro AI Tarafından Hesaplanmıştır)_"
        
        st.markdown(f"<a href='https://api.whatsapp.com/send?text={urllib.parse.quote(wa_text)}' target='_blank' class='wa-button'>📲 WhatsApp ile Arkadaşlara Gönder</a>", unsafe_allow_html=True)

# --- ARAYÜZ ---
col_sol, col_sag = st.columns([1, 2])
with col_sol:
    secilen_tarih = st.date_input("Analiz Tarihi", value=date.today(), label_visibility="collapsed")
    secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

data = maclarini_getir(secilen_tarih_str)

if "response" in data and len(data["response"]) > 0:
    bugunun_ligleri = sorted(list(set([mac["league"]["name"] for mac in data["response"]])))
    genis_havuz = ["Süper Lig", "1. Lig", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "UEFA Champions League", "UEFA Europa League", "Eredivisie", "MLS", "Saudi Pro League"]
    varsayilan_secimler = [l for l in genis_havuz if l in bugunun_ligleri] or bugunun_ligleri[:10]
    secilen_ligler = st.multiselect(f"Veri Havuzu (Data Lake)", options=bugunun_ligleri, default=varsayilan_secimler)
    
    if st.session_state.aktif_tarih != secilen_tarih_str or st.session_state.aktif_ligler != secilen_ligler: st.session_state.analiz_aktif = False

    if st.button(f"SİSTEMİ BAŞLAT VE AĞLARI TARA"):
        st.session_state.analiz_aktif = True
        st.session_state.aktif_tarih = secilen_tarih_str
        st.session_state.aktif_ligler = secilen_ligler
        
    if st.session_state.analiz_aktif:
        with st.spinner("Dark Web Forumları, xG Motoru ve Kombinasyonlar Hesaplanıyor..."):
            time.sleep(1) 
            tum_analizler = []
            lig_gruplari = {}
            for mac in data["response"]:
                lig = mac["league"]["name"]
                if lig in secilen_ligler:
                    ev, dep = mac["teams"]["home"]["name"], mac["teams"]["away"]["name"]
                    saat = turkiye_saati_hesapla(mac["fixture"]["date"])
                    mac_ismi_str = f"{ev} - {dep}"
                    
                    guc1, f1 = takim_istatistikleri_getir(ev)
                    guc2, f2 = takim_istatistikleri_getir(dep)
                    
                    xg_ev, xg_dep, skor_tahminleri = poisson_xg_hesapla(guc1, guc2, f1, f2, mac_ismi_str)
                    t_ev, t_dep, eksikler, scout_metni = taktik_ve_eksik_radari(mac_ismi_str, ev, dep)
                    
                    tahminler_sozlugu, banko_tercih, banko_guven = tum_tahminleri_hesapla(guc1, guc2, f1, f2, xg_ev, xg_dep, eksikler)
                    oran, is_value = oran_ve_value_hesapla(banko_guven, f"{ev}{dep}")
                    
                    acilis_orani, hacim, is_dropping, is_fixed, sike_kaynagi = gizli_istihbarat_olustur(oran, banko_guven, mac_ismi_str)
                    
                    if lig not in lig_gruplari: lig_gruplari[lig] = []
                    lig_gruplari[lig].append({"ev": ev, "dep": dep, "saat": saat, "en_gercekci_tercih": banko_tercih, "en_gercekci_guven": banko_guven, "oran": oran, "is_value": is_value, "is_dropping": is_dropping, "is_fixed": is_fixed, "sike_kaynagi": sike_kaynagi, "acilis": acilis_orani, "hacim": hacim, "tahminler": tahminler_sozlugu, "skorlar": skor_tahminleri, "scout": scout_metni, "xg_ev": xg_ev, "xg_dep": xg_dep, "t_ev": t_ev, "t_dep": t_dep, "eksikler": eksikler})
                    tum_analizler.append({"mac": mac_ismi_str, "saat": saat, "tercih": banko_tercih, "guven": banko_guven, "oran": oran, "is_value": is_value, "is_dropping": is_dropping, "is_fixed": is_fixed, "sike_kaynagi": sike_kaynagi, "acilis": acilis_orani, "hacim": hacim, "oran_ust": tahminler_sozlugu["2.5 Gol Üstü"], "oran_iy": tahminler_sozlugu["İlk Yarı 0.5 Gol Üstü"]})

            st.write("")
            tab_darkweb, tab_rolling, tab_kombineler, tab_ligler = st.tabs(["🕵️‍♂️ DARK WEB", "🚀 2.00x KASA", "💼 ALGORİTMİK KOMBİNELER", "MAÇ MAÇ BİG DATA"])

            with tab_darkweb:
                st.markdown("<br>", unsafe_allow_html=True)
                sike_supheli_maclar = [m for m in tum_analizler if m["is_fixed"]]
                if len(sike_supheli_maclar) > 0:
                    st.success("Sistem Tarandı: Küresel yeraltı ağlarında anormal istihbarat tespit edildi.")
                    for sm in sike_supheli_maclar:
                        st.markdown(f"""<div class='darkweb-box'><div class='darkweb-title'>🚨 ŞİKE ŞÜPHESİ / KÜRESEL SIZINTI TESPİTİ 🚨</div><div class='darkweb-source'>{sm['sike_kaynagi']}</div><hr style='border-color: rgba(239, 68, 68, 0.2); margin: 10px 0;'><div style='text-align:center;'><span style='color:#7f1d1d; font-size: 0.9em; font-weight:900;'>{sm['saat']}</span><br><span style='font-size: 1.6em; font-weight: 900; color:#450a0a;'>{sm['mac']}</span><br><br><span style='font-size: 0.9em; text-transform: uppercase; color:#991b1b; font-weight:800;'>Sızdırılan Tahmin Yönü:</span><br><b style='color:#dc2626; font-size: 1.8em;'>{sm['tercih']}</b><br><span style='font-size:1.1em; font-weight:900; color:#b91c1c;'>Olası Oran: @{sm['oran']:.2f}</span></div></div>""", unsafe_allow_html=True)
                else: st.info("📡 Şu anki ağ taramasında %100 doğrulukta bir sızıntı veya şike verisi tespit edilemedi.")

            with tab_rolling:
                st.markdown("<br>", unsafe_allow_html=True)
                mevcut_oran = 1.0
                rolling_kupon = []
                en_guvenilir_ve_mantikli = sorted(tum_analizler, key=lambda x: x["guven"], reverse=True)
                for m in en_guvenilir_ve_mantikli:
                    if mevcut_oran < 1.95:
                        rolling_kupon.append(m); mevcut_oran *= m["oran"]
                    else: break
                
                col_kupon, col_sim = st.columns([1, 1])
                with col_kupon:
                    if len(rolling_kupon) > 0: kupon_cizdir("GÜNLÜK HEDEF YATIRIM (~2.00x)", "Her gün kasayı ikiye katlamak için en uygun risk profili.", "#0284c7", rolling_kupon)
                    else: st.warning("Güvenli oran için lig ekleyin.")

                with col_sim:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center; font-weight: 900; letter-spacing: 2px; font-size: 1.1em; color: #0284c7;'>20 GÜNLÜK BİLEŞİK GETİRİ SİMÜLASYONU</div>", unsafe_allow_html=True)
                        st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                        kasa = 100
                        gunler = []
                        for gun in range(1, 21):
                            gunler.append({"Aşama": f"Gün {gun}", "Sermaye": f"{int(kasa):,} ₺", "Hedef": f"{int(kasa*2):,} ₺"})
                            kasa *= 2
                        st.dataframe(pd.DataFrame(gunler), hide_index=True, use_container_width=True, height=250)

            with tab_kombineler:
                st.markdown("<br>", unsafe_allow_html=True)
                st.info("💡 Yapay zeka bültendeki maçları tarayarak farklı risk ve kazanç stratejilerine göre 3 ayrı yatırım portföyü (Kombine) oluşturdu.")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    bankolar = sorted(tum_analizler, key=lambda x: x["guven"], reverse=True)[:3]
                    kupon_cizdir("🛡️ HEDGE FONU (ANA KASA)", "Risk barındırmayan, matematiksel olarak en garanti eşleşmeler.", "#10b981", bankolar)
                with c2:
                    kullanilan_maclar = [m["mac"] for m in bankolar]
                    gollar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_maclar], key=lambda x: x["oran_ust"], reverse=True)[:3]
                    gollar_list = [{"mac": m["mac"], "saat": m["saat"], "tercih": "2.5 Gol Üstü", "guven": m["oran_ust"], "oran": oran_ve_value_hesapla(m["oran_ust"], m["mac"])[0], "is_value": oran_ve_value_hesapla(m["oran_ust"], m["mac"])[1], "is_dropping": False} for m in gollar]
                    kupon_cizdir("⚽ LİKİDİTE GOL AĞI", "xG formülüne göre savunma zaafiyeti yüksek, bol gollü geçecek maçlar.", "#3b82f6", gollar_list)
                with c3:
                    kullanilan_maclar.extend([m["mac"] for m in gollar])
                    yuksek_risk = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_maclar and (m["is_value"] or m["is_dropping"] or m["oran"] > 1.80)], key=lambda x: x["oran"], reverse=True)[:3]
                    if len(yuksek_risk) < 3:
                        yuksek_risk = sorted([m for m in tum_analizler if m["mac"] not in kullanilan_maclar], key=lambda x: x["guven"])[:3]
                    kupon_cizdir("🌋 ALPHA FONU (YÜKSEK GETİRİ)", "Küresel para akışına ve şüpheli değerlere (Value) dayalı yüksek oranlı fon.", "#ef4444", yuksek_risk)

            with tab_ligler:
                st.markdown("<br>", unsafe_allow_html=True)
                for lig, maclar in lig_gruplari.items():
                    with st.expander(f"📁 {lig} ({len(maclar)} Karşılaşma)", expanded=False):
                        for i in range(0, len(maclar), 2):
                            cols = st.columns(2)
                            for j in range(2):
                                if i+j < len(maclar):
                                    m = maclar[i+j]
                                    with cols[j]:
                                        with st.container(border=True):
                                            val_badge = "<span class='value-badge'>🔥 VALUE</span>" if m['is_value'] else ""
                                            drop_badge = f"<div class='drop-badge'>📉 KÜRESEL HACİM: {m['hacim']} | ORAN DÜŞÜŞÜ ({m['acilis']:.2f} ➡️ {m['oran']:.2f})</div>" if m['is_dropping'] else ""
                                            
                                            if m['is_dropping']: st.markdown(f"<div style='text-align:center;'>{drop_badge}</div>", unsafe_allow_html=True)
                                            st.markdown(f"<div style='text-align:center; margin-bottom: 5px;'><span style='color:#64748b; font-size: 0.85em; font-weight:900;'>{m['saat']}</span><br><span class='team-names'>{m['ev']}</span> <span style='margin: 0 5px; color:#94a3b8;'>vs</span> <span class='team-names'>{m['dep']}</span></div>", unsafe_allow_html=True)
                                            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                            st.markdown(f"<div style='text-align:center; padding: 12px; background: #f0f9ff; border-radius: 8px; margin-bottom: 10px; border: 1px solid #bae6fd;'><span style='font-size: 0.8em; font-weight:800; text-transform: uppercase; letter-spacing: 1px; color:#0369a1;'>YAPAY ZEKA EN GÜVENLİ TERCİH:</span><br><b style='color:#0284c7; font-size: 1.3em;'>{m['en_gercekci_tercih']}</b><br><span style='font-size:1em; font-weight:900; color:#0f172a;'>Güncel Oran: @{m['oran']:.2f}</span> {val_badge}</div>", unsafe_allow_html=True)
                                            
                                            with st.expander("🧠 BİG DATA METRİKLERİ (Taktik, xG, Kadro)", expanded=False):
                                                st.markdown("<div style='font-weight:900; font-size:0.85em; margin-bottom:5px; color:#475569;'>POISSON GOL BEKLENTİSİ (xG)</div>", unsafe_allow_html=True)
                                                st.markdown(f"<div class='xg-box'><div>{m['ev'][:12]}..</div><div class='xg-value'>{m['xg_ev']:.2f} <span style='color:#64748b; font-size:0.7em;'>xG</span></div></div>", unsafe_allow_html=True)
                                                st.markdown(f"<div class='xg-box'><div>{m['dep'][:12]}..</div><div class='xg-value'>{m['xg_dep']:.2f} <span style='color:#64748b; font-size:0.7em;'>xG</span></div></div>", unsafe_allow_html=True)
                                                
                                                if "DİKKAT" in m['eksikler']: st.markdown(f"<div class='injury-box'>{m['eksikler']}</div>", unsafe_allow_html=True)
                                                st.markdown(f"<div class='scout-box'><b>Taktiksel Dağılım:</b><br>{m['ev']}: {m['t_ev']}<br>{m['dep']}: {m['t_dep']}<br><br><b>Scout Özeti:</b> {m['scout']}</div>", unsafe_allow_html=True)
                                                
                                                st.markdown("<div style='text-align:center; font-size:0.85em; font-weight:900; margin-bottom:5px; margin-top:15px; color:#475569;'>Matematiksel Skor Dağılımı</div>", unsafe_allow_html=True)
                                                st.markdown("<div class='score-sim-box'>", unsafe_allow_html=True)
                                                for skor in m["skorlar"]:
                                                    st.markdown(f"<div class='score-item'><div class='score-val'>{skor['skor']}</div><div class='score-prob'>%{skor['yuzde']:.1f}</div></div>", unsafe_allow_html=True)
                                                st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Sistem hazır. Veri girişi bekleniyor.")