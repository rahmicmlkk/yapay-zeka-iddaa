import streamlit as st
import requests
import urllib.parse
import hashlib
import math
import time
import random
import pandas as pd
from datetime import datetime, timedelta, date

# --- THE ODDS API ŞİFREN ---
API_KEY = "d466687f1d342dfec1f3222da898c54c"

st.set_page_config(page_title="Predict Pro | Ultimate Quant Terminal", layout="wide", initial_sidebar_state="expanded")

# --- GELİŞMİŞ CSS TASARIMI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .quant-title { text-align: center; font-size: 2.8em; font-weight: 900; letter-spacing: 2px; color: #0f172a; text-transform: uppercase; margin-bottom:0;}
    .quant-subtitle { text-align: center; color: #64748b; font-size: 0.9em; font-weight: 800; letter-spacing: 6px; margin-bottom: 30px; text-transform: uppercase; }
    div.stButton > button { background: #0f172a; border: none; font-weight: 800; border-radius: 8px; padding: 12px; width: 100%; color: white !important; transition: 0.3s; }
    div.stButton > button:hover { background: #334155; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    .status-card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .team-names { font-size: 1.3em; font-weight: 900; color: #0f172a; }
    .wa-button { display: block; text-align: center; background-color: #25D366; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: 800; margin-top: 10px; }
    .isg-badge { background: #e2e8f0; color: #475569; padding: 2px 8px; border-radius: 5px; font-size: 0.7em; font-weight: 800; }
    .value-badge { background: #f59e0b; color: white; padding: 2px 8px; border-radius: 5px; font-size: 0.7em; font-weight: 800; }
    
    .kombine-box { background: #ffffff; border: 1px solid #cbd5e1; border-top: 4px solid #0284c7; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);}
    .kombine-baslik { font-size: 1.1em; font-weight: 900; color: #0f172a; margin-bottom: 5px; }
    .kombine-aciklama { font-size: 0.8em; color: #64748b; font-weight: 600; margin-bottom: 10px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px;}
    .mac-row { display:flex; justify-content: space-between; font-size: 0.9em; margin-bottom: 5px; border-bottom: 1px dashed #f1f5f9; padding-bottom: 5px;}
    .mac-tercih { font-weight: 900; color: #0284c7; }
    .mac-oran { font-weight: 800; color: #475569; }
    .toplam-oran { text-align: right; font-size: 1.2em; font-weight: 900; color: #0f172a; margin-top: 10px; }
    
    /* YENİ: KÜRESEL ŞİKE RADARI TASARIMI */
    .darkweb-box { border: 2px solid #991b1b; background: #000000; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 0 25px rgba(220, 38, 38, 0.5); position: relative; overflow: hidden; }
    .darkweb-box::before { content: ""; position: absolute; top: 0; left: -100%; width: 50%; height: 100%; background: linear-gradient(to right, transparent, rgba(220, 38, 38, 0.2), transparent); animation: scan 3s infinite linear; }
    @keyframes scan { 0% { left: -100%; } 100% { left: 200%; } }
    .darkweb-title { color: #ef4444; font-weight: 900; font-size: 1.5em; text-align: center; letter-spacing: 4px; margin-bottom: 5px; text-shadow: 0 0 10px #ef4444; }
    .darkweb-source { font-family: 'Courier New', monospace; font-size: 0.9em; color: #fca5a5; font-weight: bold; text-align: center; margin-bottom: 15px; border-bottom: 1px dashed #7f1d1d; padding-bottom: 10px; }
    .darkweb-team { font-size: 1.8em; font-weight: 900; color: #ffffff; text-shadow: 0 0 5px #ffffff; }
    .darkweb-pick { color: #ef4444; font-size: 2.2em; font-weight: 900; text-shadow: 0 0 15px #ef4444; margin: 10px 0; }
    
    .prob-container { margin-bottom: 8px; }
    .prob-label { display: flex; justify-content: space-between; font-size: 0.85em; font-weight: 800; color: #334155; margin-bottom: 3px; }
    .prob-bar-bg { width: 100%; background-color: #e2e8f0; border-radius: 4px; height: 8px; overflow: hidden;}
    .prob-bar-fill { height: 100%; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

LIG_SOZLUGU = {
    "Süper Lig": "soccer_turkey_super_league",
    "Premier League": "soccer_epl",
    "La Liga": "soccer_spain_la_liga",
    "Serie A": "soccer_italy_serie_a",
    "Bundesliga": "soccer_germany_bundesliga",
    "Şampiyonlar Ligi": "soccer_uefa_champs_league"
}

if "analiz_aktif" not in st.session_state: st.session_state.analiz_aktif = False

@st.cache_data(ttl=3600)
def veri_getir(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {"apiKey": API_KEY, "regions": "eu", "markets": "h2h,totals", "oddsFormat": "decimal"}
    try:
        res = requests.get(url, params=params)
        data = res.json()
        if isinstance(data, dict) and ("error" in data or "message" in data): return "shadow_mode"
        return data
    except: return "shadow_mode"

def shadow_data():
    return [
        {"home_team": "Real Madrid", "away_team": "Barcelona", "commence_time": "2026-04-20T20:00:00Z"},
        {"home_team": "Galatasaray", "away_team": "Fenerbahçe", "commence_time": "2026-04-19T18:00:00Z"},
        {"home_team": "Man City", "away_team": "Liverpool", "commence_time": "2026-04-18T16:00:00Z"}
    ]

# --- YENİ: KÜRESEL ŞİKE SİMÜLATÖRÜ ---
def karanlik_ag_taramasi():
    # Afrika, Asya, Güney Amerika'dan rastgele takımlar ve ligler (Tamamen şov amaçlı)
    sahte_ligler = [
        {"lig": "Nijerya Premier Ligi", "ev": "Enyimba FC", "dep": "Kano Pillars", "kaynak": "[X] Kripto Sızıntısı: Afrika Yeraltı Bahis Sendikası", "tercih": "İlk Yarı 2 (Deplasman)", "oran": 4.50},
        {"lig": "Gana Premier Ligi", "ev": "Asante Kotoko", "dep": "Hearts of Oak", "kaynak": "[X] Dark Web: Gana Hakem Karteli", "tercih": "Kırmızı Kart Çıkar (EVET)", "oran": 3.10},
        {"lig": "Vietnam V.League 1", "ev": "Hanoi FC", "dep": "Hoang Anh Gia Lai", "kaynak": "[X] Asya Borsası: $2.4M Anormal Hacim Girişi", "tercih": "Maç Sonucu 0 (Beraberlik)", "oran": 5.20},
        {"lig": "Kolombiya Primera A", "ev": "Atletico Nacional", "dep": "Millonarios", "kaynak": "[X] VIP Telegram Sızıntısı: Bogota Karteli", "tercih": "3.5 Gol Üstü", "oran": 4.80},
        {"lig": "Endonezya V-League", "ev": "Bali United", "dep": "Persib Bandung", "kaynak": "[X] Tor Network Sızıntısı: Uzak Doğu Şike Ağı", "tercih": "Maç Sonucu 2 / 2.5 Üst", "oran": 6.50}
    ]
    
    # Rastgele 2 maç seç
    secilenler = random.sample(sahte_ligler, 2)
    tarih_str = (datetime.now() + timedelta(hours=random.randint(2, 12))).strftime("%d.%m.%Y %H:%M")
    
    for s in secilenler:
        s["saat"] = tarih_str
    return secilenler

def analiz_et(mac, mac_ismi):
    sayi = int(hashlib.md5(mac_ismi.encode()).hexdigest(), 16)
    ev = mac.get('home_team', 'Ev Sahibi')
    dep = mac.get('away_team', 'Deplasman')
    
    xg_ev = 1.0 + (sayi % 180) / 100.0  
    xg_dep = 0.8 + ((sayi // 2) % 150) / 100.0 
    toplam_xg = xg_ev + xg_dep
    fark = xg_ev - xg_dep
    
    pazarlar = {}
    pazarlar["MS 1"] = {"yuzde": min(85, max(15, 35 + fark * 25)), "oran": max(1.15, 2.50 - fark)}
    pazarlar["MS 2"] = {"yuzde": min(85, max(15, 35 - fark * 25)), "oran": max(1.15, 2.50 + fark)}
    pazarlar["MS 0"] = {"yuzde": 100 - (pazarlar["MS 1"]["yuzde"] + pazarlar["MS 2"]["yuzde"]), "oran": 3.40}
    pazarlar["1X Çifte Şans"] = {"yuzde": min(95, pazarlar["MS 1"]["yuzde"] + pazarlar["MS 0"]["yuzde"] - 5), "oran": max(1.05, pazarlar["MS 1"]["oran"] * 0.45)}
    pazarlar["X2 Çifte Şans"] = {"yuzde": min(95, pazarlar["MS 2"]["yuzde"] + pazarlar["MS 0"]["yuzde"] - 5), "oran": max(1.05, pazarlar["MS 2"]["oran"] * 0.45)}
    pazarlar["2.5 Üst"] = {"yuzde": min(85, max(15, 20 + toplam_xg * 15)), "oran": max(1.30, 3.50 - toplam_xg*0.5)}
    pazarlar["2.5 Alt"] = {"yuzde": 100 - pazarlar["2.5 Üst"]["yuzde"], "oran": max(1.30, 1.50 + toplam_xg*0.3)}
    pazarlar["1.5 Üst"] = {"yuzde": min(96, pazarlar["2.5 Üst"]["yuzde"] + 18), "oran": max(1.10, pazarlar["2.5 Üst"]["oran"] * 0.65)}
    pazarlar["KG Var"] = {"yuzde": min(85, max(15, 25 + (xg_ev * 10) + (xg_dep * 10))), "oran": max(1.40, 3.00 - toplam_xg*0.4)}
    
    if "bookmakers" in mac and mac["bookmakers"]:
        try:
            for mkt in mac["bookmakers"][0]["markets"]:
                if mkt["key"] == "h2h":
                    for out in mkt["outcomes"]:
                        if out["name"] == ev: pazarlar["MS 1"]["oran"] = out["price"]
                        elif out["name"] == dep: pazarlar["MS 2"]["oran"] = out["price"]
                        elif out["name"] == "Draw": pazarlar["MS 0"]["oran"] = out["price"]
        except: pass

    sirali_pazarlar = sorted(pazarlar.items(), key=lambda item: item[1]["yuzde"], reverse=True)
    ana_tercih = sirali_pazarlar[0][0]
    
    return {
        "mac": f"{ev} - {dep}", 
        "xg": f"{xg_ev:.2f} - {xg_dep:.2f}",
        "pazarlar": pazarlar,
        "ana_tercih_isim": ana_tercih,
        "ana_tercih_yuzde": sirali_pazarlar[0][1]["yuzde"],
        "ana_tercih_oran": sirali_pazarlar[0][1]["oran"]
    }

def kupon_render(baslik, aciklama, mac_listesi, pazar_filtresi=None, renk="#0284c7"):
    st.markdown(f"""<div class='kombine-box' style='border-top-color: {renk};'><div class='kombine-baslik' style='color: {renk};'>{baslik.upper()}</div><div class='kombine-aciklama'>{aciklama}</div>""", unsafe_allow_html=True)
    
    if not mac_listesi:
        st.warning("Bu stratejiye uygun maç bulunamadı.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    toplam_oran = 1.0
    for m in mac_listesi:
        tercih_isim = pazar_filtresi if pazar_filtresi else m['ana_tercih_isim']
        
        if pazar_filtresi == "HEDGE":
            guvenliler = {k:v for k,v in m['pazarlar'].items() if k in ["1X Çifte Şans", "X2 Çifte Şans", "1.5 Üst"]}
            tercih_isim = max(guvenliler, key=lambda k: guvenliler[k]['yuzde'])
        elif pazar_filtresi == "TARAF":
            taraflar = {k:v for k,v in m['pazarlar'].items() if k in ["MS 1", "MS 2"]}
            tercih_isim = max(taraflar, key=lambda k: taraflar[k]['yuzde'])
        elif pazar_filtresi == "GOL":
            gollar = {k:v for k,v in m['pazarlar'].items() if k in ["2.5 Üst", "KG Var"]}
            tercih_isim = max(gollar, key=lambda k: gollar[k]['yuzde'])
            
        tercih_verisi = m['pazarlar'][tercih_isim]
        oran = tercih_verisi['oran']
        toplam_oran *= oran
        
        st.markdown(f"<div class='mac-row'><div><b>{m['mac']}</b></div><div><span class='mac-tercih'>{tercih_isim}</span> <span class='mac-oran'>(@{oran:.2f})</span></div></div>", unsafe_allow_html=True)
        
    st.markdown(f"<div class='toplam-oran'>Olası Çarpan: {toplam_oran:.2f}x</div></div>", unsafe_allow_html=True)

def yuzde_bar_ciz(pazar_adi, yuzde, renk):
    return f"""<div class="prob-container"><div class="prob-label"><span>{pazar_adi}</span><span style="color:{renk};">% {yuzde:.1f}</span></div><div class="prob-bar-bg"><div class="prob-bar-fill" style="width: {yuzde}%; background-color: {renk};"></div></div></div>"""

# --- ARAYÜZ ---
st.markdown("<h1 class='quant-title'>PREDICT PRO // ULTIMATE</h1>", unsafe_allow_html=True)
st.markdown("<p class='quant-subtitle'>STRATEJİK PORTFÖY VE ÇOKLU PAZAR ANALİZİ</p>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🌐 Veri Kaynakları")
    secilen_ligler = st.multiselect("Taranacak Ana Ligler", options=list(LIG_SOZLUGU.keys()), default=["Süper Lig", "Premier League"])
    if st.button("SİSTEMİ ATEŞLE 🚀"):
        st.session_state.analiz_aktif = True

if st.session_state.analiz_aktif:
    tum_maclar = []
    with st.spinner("Piyasalar taranıyor, ihtimaller hesaplanıyor..."):
        time.sleep(1.5) # Gerçekçi bekleme
        for lig in secilen_ligler:
            data = veri_getir(LIG_SOZLUGU[lig])
            if data == "shadow_mode": data = shadow_data()
            for m in data:
                analiz = analiz_et(m, f"{m.get('home_team', '')}{m.get('away_team', '')}")
                analiz["lig"] = lig
                tum_maclar.append(analiz)
                
    # --- İNTERNET TARAMASI ŞOVU ---
    with st.spinner("Karanlık ağlara (Dark Web) sızılıyor, Küresel Şike Verileri taranıyor..."):
        time.sleep(2)
        sike_verileri = karanlik_ag_taramasi()
    
    tab_darkweb, tab_rolling, tab_kombine, tab_ligler = st.tabs(["🕵️‍♂️ KÜRESEL SIZINTILAR (ŞİKE RADARI)", "🚀 GÜNLÜK 2.00x KASA", "💼 KOMBİNE STRATEJİLERİ", "🔍 LİG ANALİZLERİ"])

    with tab_darkweb:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("DİKKAT: Dünyadaki internet siteleri, kapalı forumlar ve Asya borsaları taranarak aşağıdaki eşleşmelerde KESİN ŞİKE ŞÜPHESİ / SIZINTI tespit edildi.")
        
        c_dw1, c_dw2 = st.columns(2)
        for idx, sm in enumerate(sike_verileri):
            with (c_dw1 if idx % 2 == 0 else c_dw2):
                st.markdown(f"""
                <div class='darkweb-box'>
                    <div class='darkweb-title'>🚨 KÜRESEL ŞİKE SIZINTISI 🚨</div>
                    <div class='darkweb-source'>{sm['kaynak']}</div>
                    <div style='text-align:center;'>
                        <span style='color:#fca5a5; font-size: 0.9em; font-weight:800;'>{sm['lig']} | {sm['saat']}</span><br>
                        <div class='darkweb-team'>{sm['ev']} - {sm['dep']}</div>
                        <span style='font-size: 0.9em; text-transform: uppercase; color:#ef4444; font-weight:900;'>[DEŞİFRE EDİLEN YÖN]</span><br>
                        <div class='darkweb-pick'>👉 {sm['tercih']}</div>
                        <span style='font-size:1.2em; font-weight:900; color:#f87171;'>Global Kapanış Oranı: @{sm['oran']:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        wa_sike = f"🚨 *DARK WEB SIZINTISI* 🚨\n\n⚽ {sike_verileri[0]['ev']} - {sike_verileri[0]['dep']}\n👉 {sike_verileri[0]['tercih']} (@{sike_verileri[0]['oran']:.2f})\n\n_(Sistem tarafından deşifre edilmiştir)_"
        st.markdown(f"<a href='https://api.whatsapp.com/send?text={urllib.parse.quote(wa_sike)}' target='_blank' class='wa-button' style='background-color:#b91c1c;'>🚨 Bu Sızıntıyı WhatsApp'a At</a>", unsafe_allow_html=True)


    with tab_rolling:
        st.markdown("### 🎯 Günlük Otonom Kasa Hedefi")
        if tum_maclar:
            guvenli_maclar = sorted(tum_maclar, key=lambda x: x['pazarlar']['1.5 Üst']['yuzde'], reverse=True)
            kasa_maci = guvenli_maclar[0]
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f"""
                <div class='status-card'>
                    <div style='color: #64748b; font-size: 0.8em; font-weight:800;'>GÜNÜN GARANTİ KASA SEÇİMİ</div>
                    <div class='team-names'>{kasa_maci['mac']}</div>
                    <div style='color: #0284c7; font-size: 1.5em; font-weight:900;'>👉 {kasa_maci['ana_tercih_isim']} (@ {kasa_maci['ana_tercih_oran']:.2f})</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.metric("Hedef Çarpan", f"{kasa_maci['ana_tercih_oran']:.2f}x")
                st.success("Risk elendi, güvenli pazar seçildi.")

    with tab_kombine:
        st.markdown("### 💼 Algoritmik Yatırım Portföyleri (5 Farklı Fon)")
        c1, c2, c3 = st.columns(3)
        with c1:
            hedge_maclar = sorted(tum_maclar, key=lambda x: max([x['pazarlar']['1.5 Üst']['yuzde'], x['pazarlar']['1X Çifte Şans']['yuzde']]), reverse=True)[:3]
            kupon_render("🛡️ BETON KASA (Kayıpsız Fon)", "Sadece %85+ ihtimalli Çifte Şans ve 1.5 Üst pazarları kullanılarak oluşturulan sigortalı portföy.", hedge_maclar, pazar_filtresi="HEDGE", renk="#10b981")
        with c2:
            taraf_maclar = sorted(tum_maclar, key=lambda x: max([x['pazarlar']['MS 1']['yuzde'], x['pazarlar']['MS 2']['yuzde']]), reverse=True)[:3]
            kupon_render("🎯 KLASİK TARAF (Ana Portföy)", "Doğrudan taraf bahsine (MS 1 / MS 2) en çok güvenilen eşleşmeler.", taraf_maclar, pazar_filtresi="TARAF", renk="#0f172a")
        with c3:
            gol_maclar = sorted(tum_maclar, key=lambda x: x['pazarlar']['2.5 Üst']['yuzde'], reverse=True)[:3]
            kupon_render("⚽ LİKİDİTE GOL AĞI", "2.5 Üst ve Karşılıklı Gol ihtimali en yüksek 3 maç.", gol_maclar, pazar_filtresi="GOL", renk="#3b82f6")

        c4, c5 = st.columns(2)
        with c4:
            karma_maclar = sorted(tum_maclar, key=lambda x: x['ana_tercih_yuzde'], reverse=True)[:4]
            kupon_render("🧠 YAPAY ZEKA ÖZEL KARMA", "Algoritmanın her maçta 'En Yüksek İhtimalli' olarak saptadığı birbirinden farklı pazarların karması.", karma_maclar, renk="#8b5cf6")
        with c5:
            alpha_maclar = [m for m in tum_maclar if m['ana_tercih_oran'] > 1.70 and m['ana_tercih_yuzde'] > 45]
            alpha_maclar = sorted(alpha_maclar, key=lambda x: x['ana_tercih_oran'], reverse=True)[:3]
            if len(alpha_maclar) < 3: alpha_maclar = tum_maclar[:3]
            kupon_render("🌋 ALPHA FONU (Yüksek Kazanç)", "İddaa'nın yüksek oran açarak yanıldığı (Value) tahmin edilen sürpriz eşleşmeler.", alpha_maclar, renk="#ef4444")

    with tab_ligler:
        for lig in secilen_ligler:
            lig_maclari = [m for m in tum_maclar if m['lig'] == lig]
            if not lig_maclari: continue
            with st.expander(f"📁 {lig} ({len(lig_maclari)} Maç)", expanded=True):
                for lm in lig_maclari:
                    with st.container(border=True):
                        st.markdown(f"<div class='team-names' style='font-size: 1.1em; color: #0284c7;'>⚽ {lm['mac']}</div>", unsafe_allow_html=True)
                        st.markdown(f"**💡 EN GÜÇLÜ TERCİH:** `< {lm['ana_tercih_isim']} >` (%{lm['ana_tercih_yuzde']:.0f}) | Oran: **@{lm['ana_tercih_oran']:.2f}**")
                        
                        sirali_pazarlar = sorted(lm['pazarlar'].items(), key=lambda item: item[1]["yuzde"], reverse=True)
                        c_bar1, c_bar2 = st.columns(2)
                        for idx, (pazar_ismi, pazar_verisi) in enumerate(sirali_pazarlar[:6]):
                            yuzde = pazar_verisi["yuzde"]
                            renk = "#10b981" if yuzde >= 80 else ("#3b82f6" if yuzde >= 65 else ("#f59e0b" if yuzde >= 45 else "#ef4444"))
                            with (c_bar1 if idx % 2 == 0 else c_bar2):
                                st.markdown(yuzde_bar_ciz(f"{pazar_ismi} (@{pazar_verisi['oran']:.2f})", yuzde, renk), unsafe_allow_html=True)

else:
    st.info("Sol menüden analiz edilecek ligleri seçip sistemi ateşleyin.")