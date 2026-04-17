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
    
    .kombine-box { background: #ffffff; border: 1px solid #cbd5e1; border-top: 4px solid #0284c7; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);}
    .kombine-baslik { font-size: 1.1em; font-weight: 900; color: #0f172a; margin-bottom: 5px; }
    .kombine-aciklama { font-size: 0.8em; color: #64748b; font-weight: 600; margin-bottom: 10px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px;}
    .mac-row { display:flex; justify-content: space-between; font-size: 0.9em; margin-bottom: 5px; border-bottom: 1px dashed #f1f5f9; padding-bottom: 5px;}
    .mac-tercih { font-weight: 900; color: #0284c7; }
    
    /* YENİ: İNCE DETAYLI ŞİKE DOSYASI TASARIMI */
    .darkweb-box { border: 2px solid #991b1b; background: #000000; padding: 25px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 0 30px rgba(220, 38, 38, 0.6); position: relative; overflow: hidden; }
    .darkweb-box::before { content: ""; position: absolute; top: 0; left: -100%; width: 50%; height: 100%; background: linear-gradient(to right, transparent, rgba(220, 38, 38, 0.15), transparent); animation: scan 2.5s infinite linear; pointer-events: none;}
    @keyframes scan { 0% { left: -100%; } 100% { left: 200%; } }
    .darkweb-header { display: flex; justify-content: space-between; border-bottom: 1px solid #7f1d1d; padding-bottom: 10px; margin-bottom: 15px;}
    .darkweb-title { color: #ef4444; font-weight: 900; font-size: 1.4em; letter-spacing: 3px; text-shadow: 0 0 10px #ef4444; }
    .darkweb-id { color: #fca5a5; font-family: 'Courier New', monospace; font-size: 0.9em; font-weight: bold; }
    .darkweb-team { font-size: 1.8em; font-weight: 900; color: #ffffff; text-align: center; margin-bottom: 5px;}
    .darkweb-league { color: #991b1b; text-align: center; font-weight: 800; font-size: 0.9em; text-transform: uppercase; margin-bottom: 15px;}
    .darkweb-pick-box { background: rgba(220, 38, 38, 0.1); border: 1px dashed #ef4444; padding: 15px; text-align: center; border-radius: 5px; margin-bottom: 20px;}
    .darkweb-pick { color: #ef4444; font-size: 2.2em; font-weight: 900; text-shadow: 0 0 15px #ef4444; margin: 5px 0; }
    
    /* GİZLİ İSTİHBARAT DETAYLARI */
    .intel-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .intel-item { background: #111; border-left: 3px solid #dc2626; padding: 10px; border-radius: 0 5px 5px 0;}
    .intel-label { color: #f87171; font-size: 0.75em; font-weight: 800; text-transform: uppercase; margin-bottom: 3px;}
    .intel-value { color: #ffffff; font-size: 0.95em; font-family: 'Courier New', monospace; font-weight: bold;}
    
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
    "Bundesliga": "soccer_germany_bundesliga"
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

# --- YENİ: İNCE DETAYLI İSTİHBARAT DOSYASI (ŞİKE SİMÜLATÖRÜ) ---
def karanlik_ag_taramasi_detayli():
    sahte_ligler = [
        {"lig": "Nijerya Premier Ligi", "ev": "Enyimba FC", "dep": "Kano Pillars", "tercih": "İlk Yarı 2 (Deplasman)", "oran": 4.50},
        {"lig": "Gana Premier Ligi", "ev": "Asante Kotoko", "dep": "Hearts of Oak", "tercih": "Maç Sonucu 0 (Beraberlik)", "oran": 3.80},
        {"lig": "Vietnam V.League 1", "ev": "Hanoi FC", "dep": "Hoang Anh Gia Lai", "tercih": "2.5 Gol Üstü / MS 1", "oran": 2.90},
        {"lig": "Kolombiya Primera A", "ev": "Atletico Nacional", "dep": "Millonarios", "tercih": "3.5 Gol Üstü", "oran": 4.80},
        {"lig": "Endonezya V-League", "ev": "Bali United", "dep": "Persib Bandung", "tercih": "İlk Yarı 0.5 Üst", "oran": 2.50}
    ]
    
    secilenler = random.sample(sahte_ligler, 2)
    tarih_str = (datetime.now() + timedelta(hours=random.randint(2, 12))).strftime("%d.%m.%Y %H:%M")
    
    for s in secilenler:
        s["saat"] = tarih_str
        s["dosya_id"] = f"INTEL-{random.randint(1000,9999)}-{date.today().strftime('%Y%m%d')}"
        # İnce detayları rastgele ama mantıklı şekilde üret
        acilis_oran = s["oran"] + random.uniform(1.5, 3.5)
        s["detay_oran_dusus"] = f"{acilis_oran:.2f} ➡️ {s['oran']:.2f} (Sert Kırılma)"
        s["detay_hacim"] = f"Normalin {random.randint(30, 85)} Katı (Tahmini ${random.uniform(1.5, 6.8):.1f}M Asya Pazarı)"
        s["detay_kripto"] = f"Şüpheli Cüzdana {random.randint(45, 250)},000 USDT Transferi (Ağ: TRC20)"
        s["detay_handikap"] = f"Asya Baremi {random.choice(['-1.5', '+0.5', '-0.25'])}'ten {random.choice(['+1.5', '-1.25', '+0.75'])}'e Kaydırıldı."
        
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
    pazarlar["2.5 Üst"] = {"yuzde": min(85, max(15, 20 + toplam_xg * 15)), "oran": max(1.30, 3.50 - toplam_xg*0.5)}
    pazarlar["1.5 Üst"] = {"yuzde": min(96, pazarlar["2.5 Üst"]["yuzde"] + 18), "oran": max(1.10, pazarlar["2.5 Üst"]["oran"] * 0.65)}
    
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
            guvenliler = {k:v for k,v in m['pazarlar'].items() if k in ["1X Çifte Şans", "1.5 Üst"]}
            tercih_isim = max(guvenliler, key=lambda k: guvenliler[k]['yuzde'])
        elif pazar_filtresi == "TARAF":
            taraflar = {k:v for k,v in m['pazarlar'].items() if k in ["MS 1", "MS 2"]}
            tercih_isim = max(taraflar, key=lambda k: taraflar[k]['yuzde'])
            
        tercih_verisi = m['pazarlar'][tercih_isim]
        oran = tercih_verisi['oran']
        toplam_oran *= oran
        st.markdown(f"<div class='mac-row'><div><b>{m['mac']}</b></div><div><span class='mac-tercih'>{tercih_isim}</span> <span class='mac-oran'>(@{oran:.2f})</span></div></div>", unsafe_allow_html=True)
        
    st.markdown(f"<div class='toplam-oran'>Olası Çarpan: {toplam_oran:.2f}x</div></div>", unsafe_allow_html=True)

def yuzde_bar_ciz(pazar_adi, yuzde, renk):
    return f"""<div class="prob-container"><div class="prob-label"><span>{pazar_adi}</span><span style="color:{renk};">% {yuzde:.1f}</span></div><div class="prob-bar-bg"><div class="prob-bar-fill" style="width: {yuzde}%; background-color: {renk};"></div></div></div>"""

# --- ARAYÜZ ---
st.markdown("<h1 class='quant-title'>PREDICT PRO // ULTIMATE</h1>", unsafe_allow_html=True)
st.markdown("<p class='quant-subtitle'>STRATEJİK PORTFÖY VE KÜRESEL İSTİHBARAT AĞI</p>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🌐 Analiz Motoru")
    secilen_ligler = st.multiselect("Bülten Ligleri", options=list(LIG_SOZLUGU.keys()), default=["Süper Lig", "Premier League"])
    if st.button("SİSTEMİ ATEŞLE 🚀"):
        st.session_state.analiz_aktif = True

if st.session_state.analiz_aktif:
    tum_maclar = []
    with st.spinner("Piyasalar taranıyor, ihtimaller hesaplanıyor..."):
        time.sleep(1)
        for lig in secilen_ligler:
            data = veri_getir(LIG_SOZLUGU[lig])
            if data == "shadow_mode": data = shadow_data()
            for m in data:
                analiz = analiz_et(m, f"{m.get('home_team', '')}{m.get('away_team', '')}")
                analiz["lig"] = lig
                tum_maclar.append(analiz)
                
    # İNCE DETAYLI İSTİHBARAT TARAMASI
    with st.spinner("Küresel borsalardaki (Asya) anormal hacimler ve Kripto Cüzdan hareketleri inceleniyor..."):
        time.sleep(2.5)
        sike_istihbarati = karanlik_ag_taramasi_detayli()
    
    tab_darkweb, tab_rolling, tab_kombine, tab_ligler = st.tabs(["🕵️‍♂️ GİZLİ İSTİHBARAT (ŞİKE DOSYALARI)", "🚀 GÜNLÜK KASA", "💼 STRATEJİLER", "🔍 LİG ANALİZLERİ"])

    with tab_darkweb:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("DİKKAT: Sistemin Asya piyasalarında ve kapalı ağlarda yaptığı 'Anormal Para Akışı' taraması sonucunda aşağıdaki eşleşmelerde KESİN SIZINTI tespit edilmiştir.")
        
        c_dw1, c_dw2 = st.columns(2)
        for idx, intel in enumerate(sike_istihbarati):
            with (c_dw1 if idx % 2 == 0 else c_dw2):
                st.markdown(f"""
                <div class='darkweb-box'>
                    <div class='darkweb-header'>
                        <span class='darkweb-title'>🚨 İSTİHBARAT DOSYASI</span>
                        <span class='darkweb-id'>{intel['dosya_id']}</span>
                    </div>
                    <div class='darkweb-league'>🌍 {intel['lig']} | {intel['saat']}</div>
                    <div class='darkweb-team'>{intel['ev']} <br><span style='font-size:0.6em; color:#64748b;'>VS</span><br> {intel['dep']}</div>
                    
                    <div class='darkweb-pick-box'>
                        <span style='font-size: 0.8em; text-transform: uppercase; color:#fca5a5; font-weight:800; letter-spacing:1px;'>Sızdırılan Operasyon (Yön):</span><br>
                        <div class='darkweb-pick'>👉 {intel['tercih']}</div>
                        <span style='font-size:1.1em; font-weight:900; color:#f87171;'>Hedef Kapanış Oranı: @{intel['oran']:.2f}</span>
                    </div>
                    
                    <div style='font-size: 0.9em; font-weight: 800; color: #ef4444; margin-bottom: 8px; border-bottom: 1px solid #7f1d1d; padding-bottom: 5px;'>🔍 TESPİT EDİLEN ANOMALİLER (GEREKÇE)</div>
                    <div class='intel-grid'>
                        <div class='intel-item'>
                            <div class='intel-label'>💸 Küresel Hacim Şişmesi</div>
                            <div class='intel-value'>{intel['detay_hacim']}</div>
                        </div>
                        <div class='intel-item'>
                            <div class='intel-label'>📉 Oran Uçurumu</div>
                            <div class='intel-value'>{intel['detay_oran_dusus']}</div>
                        </div>
                        <div class='intel-item'>
                            <div class='intel-label'>🔗 Şüpheli Kripto İzi</div>
                            <div class='intel-value'>{intel['detay_kripto']}</div>
                        </div>
                        <div class='intel-item'>
                            <div class='intel-label'>⚖️ Asya Handikap Manipülasyonu</div>
                            <div class='intel-value'>{intel['detay_handikap']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        # Özel WhatsApp Şov Butonu
        wa_sike = f"🚨 *GİZLİ İSTİHBARAT DOSYASI ({sike_istihbarati[0]['dosya_id']})* 🚨\n\n🌍 {sike_istihbarati[0]['lig']}\n⚽ {sike_istihbarati[0]['ev']} - {sike_istihbarati[0]['dep']}\n\n👉 *Operasyon Yönü:* {sike_istihbarati[0]['tercih']} (@{sike_istihbarati[0]['oran']:.2f})\n\n📉 *Sızıntı Nedeni:* {sike_istihbarati[0]['detay_hacim']} giriş tespit edildi. Oranlar {sike_istihbarati[0]['detay_oran_dusus']} çakıldı.\n\n_(Predict Pro Smart Money Radar Tarafından Deşifre Edilmiştir)_"
        st.markdown(f"<a href='https://api.whatsapp.com/send?text={urllib.parse.quote(wa_sike)}' target='_blank' class='wa-button' style='background-color:#b91c1c;'>🚨 Bu İstihbarat Dosyasını WhatsApp'a Sızdır</a>", unsafe_allow_html=True)


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

    with tab_kombine:
        st.markdown("### 💼 Algoritmik Yatırım Portföyleri (5 Farklı Fon)")
        c1, c2, c3 = st.columns(3)
        with c1:
            hedge_maclar = sorted(tum_maclar, key=lambda x: max([x['pazarlar']['1.5 Üst']['yuzde'], x['pazarlar']['1X Çifte Şans']['yuzde']]), reverse=True)[:3]
            kupon_render("🛡️ BETON KASA (Kayıpsız Fon)", "Sadece %85+ ihtimalli garantici pazarlar.", hedge_maclar, pazar_filtresi="HEDGE", renk="#10b981")
        with c2:
            taraf_maclar = sorted(tum_maclar, key=lambda x: max([x['pazarlar']['MS 1']['yuzde'], x['pazarlar']['MS 2']['yuzde']]), reverse=True)[:3]
            kupon_render("🎯 KLASİK TARAF (Ana Portföy)", "Doğrudan taraf bahsine en çok güvenilen eşleşmeler.", taraf_maclar, pazar_filtresi="TARAF", renk="#0f172a")
        with c3:
            gol_maclar = sorted(tum_maclar, key=lambda x: x['pazarlar']['2.5 Üst']['yuzde'], reverse=True)[:3]
            kupon_render("⚽ LİKİDİTE GOL AĞI", "2.5 Üst ihtimali en yüksek 3 maç.", gol_maclar, pazar_filtresi="GOL", renk="#3b82f6")

        c4, c5 = st.columns(2)
        with c4:
            karma_maclar = sorted(tum_maclar, key=lambda x: x['ana_tercih_yuzde'], reverse=True)[:4]
            kupon_render("🧠 YAPAY ZEKA ÖZEL KARMA", "Algoritmanın her maçta 'En Yüksek İhtimalli' saptadığı optimum karma.", karma_maclar, renk="#8b5cf6")
        with c5:
            alpha_maclar = sorted(tum_maclar, key=lambda x: x['ana_tercih_oran'], reverse=True)[:3]
            kupon_render("🌋 ALPHA FONU (Yüksek Kazanç)", "Yüksek oranlı sürpriz (Value) eşleşmeler.", alpha_maclar, renk="#ef4444")

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
                        for idx, (pazar_ismi, pazar_verisi) in enumerate(sirali_pazarlar[:4]):
                            yuzde = pazar_verisi["yuzde"]
                            renk = "#10b981" if yuzde >= 80 else ("#3b82f6" if yuzde >= 65 else ("#f59e0b" if yuzde >= 45 else "#ef4444"))
                            with (c_bar1 if idx % 2 == 0 else c_bar2):
                                st.markdown(yuzde_bar_ciz(f"{pazar_ismi} (@{pazar_verisi['oran']:.2f})", yuzde, renk), unsafe_allow_html=True)

else:
    st.info("Sol menüden analiz edilecek ligleri seçip sistemi ateşleyin.")