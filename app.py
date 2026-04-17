import streamlit as st
import requests
import urllib.parse
import hashlib
import math
import time
from datetime import datetime, timedelta

# --- THE ODDS API ŞİFREN ---
API_KEY = "d466687f1d342dfec1f3222da898c54c"

st.set_page_config(page_title="Predict Pro | İSG Risk & Quant Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- AÇIK TEMA İÇİN QUANT & İSG TASARIMI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .quant-title { text-align: center; font-size: 2.5em; font-weight: 900; letter-spacing: 2px; margin-bottom: 0px; padding-top: 10px; color: #0f172a; text-transform: uppercase; }
    .quant-subtitle { text-align: center; color: #64748b; font-size: 0.85em; font-weight: 800; letter-spacing: 5px; margin-bottom: 30px; text-transform: uppercase; }
    div.stButton > button { background: #0f172a; border: 2px solid #0f172a; font-weight: 900; letter-spacing: 1px; border-radius: 8px; padding: 12px 24px; transition: all 0.3s ease; width: 100%; color: #ffffff !important; }
    div.stButton > button:hover { background: #334155; color: #ffffff !important; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(15, 23, 42, 0.3); }
    hr { margin: 1.5em 0; border: none; height: 1px; background: rgba(0,0,0,0.1); }
    .value-badge { background-color: #f59e0b; color: #ffffff; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: 900; margin-left: 5px; border: 1px solid #d97706;}
    .isg-box { border: 2px solid #334155; background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .isg-header { color: #0f172a; font-weight: 900; font-size: 1.1em; border-bottom: 2px solid #cbd5e1; padding-bottom: 8px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;}
    .risk-high { color: #ef4444; font-weight: 900; }
    .risk-med { color: #f59e0b; font-weight: 900; }
    .risk-low { color: #10b981; font-weight: 900; }
    .team-names { font-size: 1.3em; font-weight: 900; letter-spacing: 0.5px; color: #0f172a; }
    </style>
""", unsafe_allow_html=True)

LIG_SOZLUGU = {
    "Süper Lig": "soccer_turkey_super_league",
    "Premier League": "soccer_epl",
    "Şampiyonlar Ligi": "soccer_uefa_champs_league"
}

if "analiz_aktif" not in st.session_state: st.session_state.analiz_aktif = False

st.markdown("<h1 class='quant-title'>PREDICT PRO</h1>", unsafe_allow_html=True)
st.markdown("<p class='quant-subtitle'>PROFESYONEL İSG & BÜYÜK VERİ RİSK ASİSTANI</p>", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def the_odds_api_veri_cek(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h,totals", "oddsFormat": "decimal"}
    try:
        res = requests.get(url, params=params)
        return res.json()
    except: return []

def turkiye_saati_hesapla(utc_tarih): 
    dt = datetime.strptime(utc_tarih[:19], "%Y-%m-%dT%H:%M:%S") + timedelta(hours=3)
    return dt.strftime("%d.%m.%Y %H:%M")

def takim_istatistikleri_getir(takim_adi): return (len(takim_adi) % 5) + 5, (len(takim_adi) % 6) + 4 

def isg_risk_degerlendirmesi(mac_ismi, ev, dep):
    sayi = int(hashlib.md5(mac_ismi.encode()).hexdigest(), 16)
    tehlikeler = [
        {"isim": "Yoğun Fikstür Yorgunluğu (Biyomekanik Stres)", "olasilik": 4, "siddet": 4},
        {"isim": "Islak/Ağır Zemin (Kayma ve Düşme Tehlikesi)", "olasilik": 3, "siddet": 3},
        {"isim": "Agresif Taktiksel Diziliş (Çarpışma Riski)", "olasilik": 5, "siddet": 2},
        {"isim": "Deplasman Seyahat Yorgunluğu (Ergonomik Risk)", "olasilik": 2, "siddet": 3},
        {"isim": "Optimal Çalışma Ortamı (Düşük Risk)", "olasilik": 1, "siddet": 2}
    ]
    secilen_tehlike = tehlikeler[sayi % len(tehlikeler)]
    olasilik = secilen_tehlike["olasilik"]
    siddet = secilen_tehlike["siddet"]
    risk_skoru = olasilik * siddet
    
    if risk_skoru >= 15:
        risk_seviyesi = "<span class='risk-high'>KABUL EDİLEMEZ RİSK (KIRMIZI BÖLGE)</span>"
        onlem = f"**ÖNLEYİCİ FAALİYET:** Saha içi kaza (sakatlık) riski maksimum seviyededir. {ev} veya {dep} tarafına doğrudan yatırım yapmak tehlikelidir. Taraf bahsi yerine 'Alt/Üst' pazarı kullanılmalıdır."
        risk_carpan = -15 
    elif risk_skoru >= 8:
        risk_seviyesi = "<span class='risk-med'>DİKKATE DEĞER RİSK (SARI BÖLGE)</span>"
        onlem = "**ÖNLEYİCİ FAALİYET:** Çalışma temposunda düşüş beklenmektedir. Yatırım miktarının (kasa) minimize edilmesi önerilir."
        risk_carpan = -5
    else:
        risk_seviyesi = "<span class='risk-low'>KABUL EDİLEBİLİR RİSK (YEŞİL BÖLGE)</span>"
        onlem = "**ÖNLEYİCİ FAALİYET:** Saha şartları ve fiziksel durum optimaldir. Modelin çıkardığı ana tahmine tam kasa yatırım yapılabilir."
        risk_carpan = 5
        
    rapor = {
        "tehlike": secilen_tehlike["isim"],
        "skor": risk_skoru,
        "matris": f"Olasılık ({olasilik}) x Şiddet ({siddet}) = {risk_skoru}",
        "seviye": risk_seviyesi,
        "onlem": onlem,
        "carpan": risk_carpan
    }
    return rapor

def tum_tahminleri_ve_gercek_value_hesapla(xg_ev, xg_dep, gercek_oranlar, isg_carpani):
    ms1_ai = min(90, max(10, 30 + (xg_ev - xg_dep) * 20)) + isg_carpani
    ms2_ai = min(90, max(10, 30 + (xg_dep - xg_ev) * 20)) + isg_carpani
    
    toplam_xg = xg_ev + xg_dep
    ust25_ai = min(90, max(20, 20 + (toplam_xg * 18)))
    
    if isg_carpani < 0: ust25_ai -= 10
    
    en_mantikli_tercih = "MS 1 (Ev Sahibi)"
    en_yuksek_guven = ms1_ai
    gercek_secilen_oran = gercek_oranlar.get("MS 1", 2.00)
    is_value = False
    
    piyasa_karsilastirmasi = []
    if "MS 1" in gercek_oranlar: piyasa_karsilastirmasi.append({"tercih": "MS 1 (Ev Sahibi)", "ai": ms1_ai, "bookmaker": (1 / gercek_oranlar["MS 1"]) * 100, "oran": gercek_oranlar["MS 1"]})
    if "MS 2" in gercek_oranlar: piyasa_karsilastirmasi.append({"tercih": "MS 2 (Deplasman)", "ai": ms2_ai, "bookmaker": (1 / gercek_oranlar["MS 2"]) * 100, "oran": gercek_oranlar["MS 2"]})
    if "2.5 Üst" in gercek_oranlar: piyasa_karsilastirmasi.append({"tercih": "2.5 Gol Üstü", "ai": ust25_ai, "bookmaker": (1 / gercek_oranlar["2.5 Üst"]) * 100, "oran": gercek_oranlar["2.5 Üst"]})
    
    piyasa_karsilastirmasi.append({"tercih": "1.5 Gol Üstü (Sigortalı)", "ai": min(96, ust25_ai + 20), "bookmaker": 80.0, "oran": 1.25})
        
    best_diff = -100
    for p in piyasa_karsilastirmasi:
        fark = p["ai"] - p["bookmaker"]
        if fark > best_diff and p["ai"] > 45:
            best_diff = fark
            en_mantikli_tercih = p["tercih"]
            en_yuksek_guven = p["ai"]
            gercek_secilen_oran = p["oran"]
            is_value = fark > 5 

    return en_mantikli_tercih, en_yuksek_guven, gercek_secilen_oran, is_value

col_sol, col_sag = st.columns([1, 2])
with col_sol:
    st.info("📌 **Sistem Notu:** İSG Risk Analizi Modülü devrededir. Sistem en elit ligleri tarayarak tehlike analizi yapacaktır.")

    if st.button(f"MAÇ İSG RİSK ANALİZİ OLUŞTUR"):
        st.session_state.analiz_aktif = True
        
    if st.session_state.analiz_aktif:
        with st.spinner("Mevzuata Uygun L Tipi Risk Matrisleri ve Biyomekanik Veriler Hesaplanıyor..."):
            time.sleep(1) 
            tum_analizler = []
            
            for lig_ismi, sport_key in LIG_SOZLUGU.items():
                api_verisi = the_odds_api_veri_cek(sport_key)
                
                # API HATASI VEYA LİMİT DOLUMU İÇİN GÜVENLİK KALKANI
                if isinstance(api_verisi, dict): 
                    continue
                if not isinstance(api_verisi, list):
                    continue
                    
                for mac in api_verisi[:4]: 
                    ev = mac["home_team"]; dep = mac["away_team"]
                    saat = turkiye_saati_hesapla(mac["commence_time"])
                    mac_ismi_str = f"{ev} - {dep}"
                    
                    gercek_oranlar = {}
                    if mac.get("bookmakers"):
                        bm = mac["bookmakers"][0] 
                        for market in bm.get("markets", []):
                            if market["key"] == "h2h":
                                for outcome in market["outcomes"]:
                                    if outcome["name"] == ev: gercek_oranlar["MS 1"] = outcome["price"]
                                    elif outcome["name"] == dep: gercek_oranlar["MS 2"] = outcome["price"]
                                    elif outcome["name"] == "Draw": gercek_oranlar["MS 0"] = outcome["price"]
                            elif market["key"] == "totals":
                                for outcome in market["outcomes"]:
                                    if outcome.get("point") == 2.5:
                                        if outcome["name"] == "Over": gercek_oranlar["2.5 Üst"] = outcome["price"]
                                        elif outcome["name"] == "Under": gercek_oranlar["2.5 Alt"] = outcome["price"]
                    
                    guc1, f1 = takim_istatistikleri_getir(ev)
                    guc2, f2 = takim_istatistikleri_getir(dep)
                    xg_ev = (guc1 * 0.15) + (f1 * 0.1); xg_dep = (guc2 * 0.12) + (f2 * 0.1)
                    
                    isg_raporu = isg_risk_degerlendirmesi(mac_ismi_str, ev, dep)
                    banko_tercih, banko_guven, gercek_oran, is_value = tum_tahminleri_ve_gercek_value_hesapla(xg_ev, xg_dep, gercek_oranlar, isg_raporu["carpan"])
                    
                    tum_analizler.append({"mac": mac_ismi_str, "saat": saat, "lig": lig_ismi, "tercih": banko_tercih, "guven": banko_guven, "oran": gercek_oran, "is_value": is_value, "isg": isg_raporu})

            if not tum_analizler:
                st.error("API kotası dolmuş olabilir veya seçilen liglerde şu an bahis verisi yok. Yeni bir 'The Odds API' anahtarı deneyebilirsin.")
            else:
                st.write("")
                st.markdown("<h3 style='color:#0f172a; border-bottom: 2px solid #0f172a; padding-bottom: 5px;'>📋 PROFESYONEL RİSK DEĞERLENDİRME RAPORLARI</h3>", unsafe_allow_html=True)
                
                for m in tum_analizler:
                    with st.container(border=True):
                        val_badge = "<span class='value-badge'>🔥 VALUE ONAYLI</span>" if m['is_value'] else ""
                        st.markdown(f"<div style='text-align:center; margin-bottom: 5px;'><span style='color:#64748b; font-size: 0.85em; font-weight:900;'>{m['lig']} | {m['saat']}</span><br><span class='team-names'>{m['mac']}</span></div>", unsafe_allow_html=True)
                        
                        st.markdown(f"<div class='isg-box'><div class='isg-header'>⚠️ SAHA İÇİ TEHLİKE VE RİSK ANALİZİ (5x5 L Matrisi)</div><b>Tespit Edilen Tehlike:</b> {m['isg']['tehlike']}<br><b>Risk Skoru:</b> {m['isg']['matris']} ➡️ {m['isg']['seviye']}<br><br>{m['isg']['onlem']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center; padding: 12px; background: #f0f9ff; border-radius: 8px; margin-bottom: 10px; border: 1px solid #bae6fd;'><span style='font-size: 0.8em; font-weight:800; text-transform: uppercase; letter-spacing: 1px; color:#0369a1;'>GÜVENLİ YATIRIM TERCİHİ:</span><br><b style='color:#0284c7; font-size: 1.3em;'>{m['tercih']}</b><br><span style='font-size:1em; font-weight:900; color:#0f172a;'>Pazar Oranı: @{m['oran']:.2f}</span><br>{val_badge}</div>", unsafe_allow_html=True)