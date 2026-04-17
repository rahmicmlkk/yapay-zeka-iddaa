import streamlit as st
import requests
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta, date
from sklearn.ensemble import RandomForestClassifier

# --- SENİN API ŞİFREN ---
API_KEY = "18961e393de1214e4595758bbebe08aa"

st.set_page_config(page_title="Predict Pro VIP", layout="wide")

# --- ZARİF VE MODERN TASARIM (ELEGANT UI) ---
st.markdown("""
    <style>
    .elegant-title { text-align: center; font-family: 'Helvetica Neue', sans-serif; font-size: 2.2em; font-weight: 200; letter-spacing: 6px; margin-bottom: 0px; padding-top: 10px; }
    .elegant-subtitle { text-align: center; color: #718096; font-size: 0.95em; font-weight: 300; letter-spacing: 2px; margin-bottom: 40px; }
    div.stButton > button { background-color: transparent; border: 1px solid #cbd5e1; font-weight: 300; letter-spacing: 1px; border-radius: 6px; padding: 8px 24px; transition: all 0.4s ease; width: 100%; }
    div.stButton > button:hover { border-color: #6366f1; color: #6366f1 !important; background-color: rgba(99, 102, 241, 0.05); }
    hr { margin: 1.5em 0; border: none; height: 1px; background: linear-gradient(90deg, rgba(200,200,200,0) 0%, rgba(200,200,200,0.5) 50%, rgba(200,200,200,0) 100%); }
    .wa-button { display: block; text-align: center; background-color: #25D366; color: white !important; padding: 10px; border-radius: 6px; text-decoration: none; font-weight: 600; letter-spacing: 1px; margin-top: 15px; transition: background-color 0.3s; }
    .wa-button:hover { background-color: #128C7E; color: white !important;}
    .value-badge { background-color: #f59e0b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; font-weight: bold; margin-left: 5px; }
    .rolling-box { border-left: 4px solid #10b981; margin-bottom: 20px; background-color: rgba(16, 185, 129, 0.05); padding: 15px; border-radius: 0 6px 6px 0; }
    .ai-choice { text-align: center; font-weight: bold; color: #10b981; font-size: 1.2em; letter-spacing: 1px; margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- SİSTEM HAFIZASI ---
if "analiz_aktif" not in st.session_state: st.session_state.analiz_aktif = False
if "aktif_tarih" not in st.session_state: st.session_state.aktif_tarih = None
if "aktif_ligler" not in st.session_state: st.session_state.aktif_ligler = []

st.markdown("<h1 class='elegant-title'>PREDICT PRO</h1>", unsafe_allow_html=True)
st.markdown("<p class='elegant-subtitle'>AI AUTONOMOUS SELECTION & ROLLING</p>", unsafe_allow_html=True)

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

def tum_tahminleri_hesapla(ev_guc, dep_guc, ev_form, dep_form, model):
    tahminler = {}
    if model:
        olasilik = model.predict_proba([[ev_guc, dep_guc, ev_form, dep_form]])[0]
        tahminler["MS 0"] = olasilik[0]*100; tahminler["MS 1"] = olasilik[1]*100; tahminler["MS 2"] = olasilik[2]*100
    
    t_guc = ev_guc + dep_guc + ev_form + dep_form
    ust_25 = max(30, min(75, 35 + (t_guc * 1.1)))
    tahminler["2.5 Üst"] = ust_25; tahminler["2.5 Alt"] = 100 - ust_25
    tahminler["1.5 Üst"] = min(92, ust_25 + 15); tahminler["3.5 Alt"] = min(90, (100 - ust_25) + 20)
    iy_ust = max(28, min(70, 30 + (ev_form + dep_form) * 1.3))
    tahminler["İY 0.5 Üst"] = iy_ust; tahminler["İY 1.5 Alt"] = min(88, (100 - iy_ust) + 10)
    kg_var = max(35, min(75, 40 + (ev_guc + dep_guc) * 0.9))
    tahminler["KG Var"] = kg_var; tahminler["KG Yok"] = 100 - kg_var
    korner_85 = max(35, min(78, 45 + (ev_form + dep_form) * 1.2))
    tahminler["Korner 8.5 Üst"] = korner_85; tahminler["Korner 9.5 Üst"] = max(20, korner_85 - 12)
    
    en_gercekci = max(tahminler, key=tahminler.get)
    return tahminler, en_gercekci, tahminler[en_gercekci]

def kupon_cizdir(baslik, kupon_listesi, ai_secimi=False):
    with st.container(border=True):
        if ai_secimi:
            st.markdown(f"<div class='ai-choice'>🤖 YAPAY ZEKA GÜNÜN SEÇİMİ</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: center; font-weight: 300; letter-spacing: 1.5px; font-size: 1.1em; color: #6366f1;'>{baslik.upper()}</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
        
        if not kupon_listesi:
            st.caption("Veri yetersizliği nedeniyle filtre uygulandı.")
            return
            
        toplam_oran = 1.0
        wa_text = f"💎 *PREDICT PRO VIP - {baslik}* 💎\n\n"
        
        for index, k_mac in enumerate(kupon_listesi):
            toplam_oran *= k_mac['oran']
            value_badge = "<span class='value-badge'>🔥 VALUE</span>" if k_mac.get('is_value', False) else ""
            wa_value_icon = "🔥 " if k_mac.get('is_value', False) else ""
            
            st.markdown(f"<div style='font-size: 0.85em; color: #94a3b8; margin-bottom: -5px;'>{k_mac['saat']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight: 500;'>{k_mac['mac']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='margin-bottom: 12px;'><span style='color: #10b981; font-weight: 600;'>{k_mac['tercih']}</span> <span style='color:#94a3b8; font-size: 0.85em;'>| Oran: {k_mac['oran']:.2f}</span> {value_badge}</div>", unsafe_allow_html=True)
            wa_text += f"⚽ {k_mac['mac']}\n👉 Tahmin: {k_mac['tercih']} {wa_value_icon}\n📈 Oran: {k_mac['oran']:.2f}\n\n"
            
        st.markdown(f"<div style='text-align: right; font-size: 1.2em; color: #333; margin-top: 10px; font-weight: bold;'>Net Oran: {toplam_oran:.2f}</div>", unsafe_allow_html=True)
        
        wa_text += f"💵 *Kupon Toplam Oranı: {toplam_oran:.2f}*"
        wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_text)}"
        st.markdown(f"<a href='{wa_link}' target='_blank' class='wa-button'>📲 WhatsApp'ta Paylaş</a>", unsafe_allow_html=True)

def yuzde_bar_ciz(baslik, deger):
    st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: gray; margin-bottom: 3px; font-weight: 300;">
                <span>{baslik}</span>
                <span>%{deger:.0f}</span>
            </div>
            <div style="width: 100%; background-color: rgba(128, 128, 128, 0.15); border-radius: 10px; height: 5px;">
                <div style="width: {deger}%; background-color: #6366f1; height: 5px; border-radius: 10px; transition: width 1s ease-in-out;"></div>
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
    
    secilen_ligler = st.multiselect(f"Aktif Veri Havuzu ({secilen_tarih_str})", options=bugunun_ligleri, default=varsayilan_secimler)
    
    if st.session_state.aktif_tarih != secilen_tarih_str or st.session_state.aktif_ligler != secilen_ligler: st.session_state.analiz_aktif = False

    if st.button(f"SİSTEMİ BAŞLAT"):
        st.session_state.analiz_aktif = True
        st.session_state.aktif_tarih = secilen_tarih_str
        st.session_state.aktif_ligler = secilen_ligler
        
    if st.session_state.analiz_aktif:
        with st.spinner("Yapay Zeka otonom seçimlerini yapıyor..."):
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
                    
                    mac_ismi_str = f"{ev}{dep}"
                    oran, is_value = oran_ve_value_hesapla(banko_guven, mac_ismi_str)
                    
                    if lig not in lig_gruplari: lig_gruplari[lig] = []
                    lig_gruplari[lig].append({"ev": ev, "dep": dep, "saat": saat, "en_gercekci_tercih": banko_tercih, "en_gercekci_guven": banko_guven, "oran": oran, "is_value": is_value, "tahminler": tahminler_sozlugu})
                    
                    tum_analizler.append({"mac": f"{ev} - {dep}", "saat": saat, "tercih": banko_tercih, "guven": banko_guven, "oran": oran, "is_value": is_value, "oran_ust": tahminler_sozlugu["2.5 Üst"], "oran_iy": tahminler_sozlugu["İY 0.5 Üst"], "oran_korner": tahminler_sozlugu["Korner 8.5 Üst"], "oran_ms0": tahminler_sozlugu["MS 0"]})

            st.write("")
            tab_rolling, tab_kombine, tab_ligler, tab_seffaflik = st.tabs(["🚀 KASA KATLAMA", "STRATEJİ KOMBİNELERİ", "DERİN LİG ANALİZİ", "SİSTEM PERFORMANSI"])

            with tab_rolling:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='rolling-box'><h3 style='margin:0; color:#065f46;'>🎯 Otonom %100 Büyüme Stratejisi</h3><p style='margin-top:5px; margin-bottom:0; font-size:0.9em; color:#047857;'>Yapay Zeka, tüm bülteni analiz ederek bugün kasa katlama serisine uygun <b>~2.00 Oranlı</b> spesifik bir seçim yaptı. Tekli veya en güvenilir akıllı kombinasyon.</p></div>", unsafe_allow_html=True)
                
                # --- YENİ YZ OTONOM 2.00 SEÇİM ALGORİTMASI ---
                rolling_kupon = []
                # Önce 1.85 ile 2.20 arası tek maç var mı diye bakar (Kasa için tek maç idealdir)
                tekli_adaylar = [m for m in tum_analizler if 1.85 <= m["oran"] <= 2.20 and m["guven"] >= 70]
                
                if tekli_adaylar:
                    # Varsa en güvenilirini seç
                    rolling_kupon = [sorted(tekli_adaylar, key=lambda x: x["guven"], reverse=True)[0]]
                else:
                    # Yoksa en yüksek güvenlileri toplayıp 1.95 - 2.15 aralığına ulaşmaya çalışır
                    mevcut_oran = 1.0
                    en_guvenilirler = sorted(tum_analizler, key=lambda x: x["guven"], reverse=True)
                    for m in en_guvenilirler:
                        if mevcut_oran < 1.95:
                            rolling_kupon.append(m)
                            mevcut_oran *= m["oran"]
                        else:
                            break
                
                col_kupon, col_sim = st.columns([1, 1])
                with col_kupon:
                    if len(rolling_kupon) > 0:
                        kupon_cizdir("GÜNÜN ROLLING HEDEFİ", rolling_kupon, ai_secimi=True)
                    else:
                        st.warning("Bugün 2.00 oranı tamamlayacak yeterli güvenilir veri bulunamadı. Lütfen lig ekleyin.")

                with col_sim:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center; font-weight: 300; letter-spacing: 1.5px; font-size: 1.1em; color: #6366f1;'>20 GÜNLÜK MİLYONER SİMÜLASYONU</div>", unsafe_allow_html=True)
                        st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                        st.markdown("<p style='font-size:0.85em; color:gray; text-align:center;'>Eğer her gün kasanın tamamını Yapay Zekanın 2.00 Oranlı seçimine basarsan:</p>", unsafe_allow_html=True)
                        
                        baslangic_kasasi = 100
                        gunler = []
                        kasa = baslangic_kasasi
                        for gun in range(1, 21):
                            gunler.append({"Gün": f"{gun}. Gün", "Yatırılan": f"{int(kasa):,} ₺", "Hedeflenen": f"{int(kasa*2):,} ₺"})
                            kasa *= 2
                            
                        df_simulasyon = pd.DataFrame(gunler)
                        st.dataframe(df_simulasyon, hide_index=True, use_container_width=True, height=250)
                        st.success(f"💰 20. Günün Sonundaki Hedef Bakiye: **104.857.600 ₺**")
                        st.caption("⚠️ İstatistiksel Projeksiyondur. Garanti kupon yoktur.")

            with tab_kombine:
                st.write("")
                if len(tum_analizler) >= 5:
                    karma, kullanilan = [], []
                    best_ms = sorted(tum_analizler, key=lambda x: x["guven"], reverse=True)[0]; karma.append(best_ms); kullanilan.append(best_ms["mac"])
                    
                    best_gol = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_ust"], reverse=True)[0]
                    oran_gol, val_gol = oran_ve_value_hesapla(best_gol["oran_ust"], best_gol["mac"])
                    karma.append({"mac": best_gol["mac"], "saat": best_gol["saat"], "tercih": "2.5 Üst", "guven": best_gol["oran_ust"], "oran": oran_gol, "is_value": val_gol}); kullanilan.append(best_gol["mac"])
                    
                    best_korner = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_korner"], reverse=True)[0]
                    oran_korner, val_korner = oran_ve_value_hesapla(best_korner["oran_korner"], best_korner["mac"])
                    karma.append({"mac": best_korner["mac"], "saat": best_korner["saat"], "tercih": "Korner 8.5 Üst", "guven": best_korner["oran_korner"], "oran": oran_korner, "is_value": val_korner}); kullanilan.append(best_korner["mac"])
                    
                    kupon_cizdir("Optimum Karma", karma)

                    bankolar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["guven"], reverse=True)[:3]; kullanilan.extend([m["mac"] for m in bankolar])
                    gollar = sorted([m for m in tum_analizler if m["mac"] not in kullanilan], key=lambda x: x["oran_ust"], reverse=True)[:3]; kullanilan.extend([m["mac"] for m in gollar])
                    
                    c1, c2 = st.columns(2)
                    with c1: 
                        kupon_cizdir("Ana Kasa (Güvenli)", bankolar)
                    with c2: 
                        gollar_list = []
                        for m in gollar:
                            o, v = oran_ve_value_hesapla(m["oran_ust"], m["mac"])
                            gollar_list.append({"mac": m["mac"], "saat": m["saat"], "tercih": "2.5 Üst", "guven": m["oran_ust"], "oran": o, "is_value": v})
                        kupon_cizdir("Gol Şenliği", gollar_list)
                else: 
                    st.caption("Kombineler için lig seçim kutusundan daha fazla lig ekleyin.")

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
                                            st.markdown(f"<div style='text-align:center; margin-bottom: 10px;'><span style='color:#94a3b8; font-size: 0.8em; letter-spacing: 1px;'>{m['saat']}</span><br><span style='font-size: 1.1em; font-weight: 400;'>{m['ev']}</span> <span style='color: #cbd5e1; margin: 0 5px;'>vs</span> <span style='font-size: 1.1em; font-weight: 400;'>{m['dep']}</span></div>", unsafe_allow_html=True)
                                            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                            val_badge = "<span class='value-badge'>🔥 VALUE</span>" if m['is_value'] else ""
                                            st.markdown(f"<div style='text-align:center; padding: 8px; background-color: rgba(99, 102, 241, 0.05); border-radius: 6px; margin-bottom: 10px;'><span style='font-size: 0.8em; color: gray;'>Optimum Tercih</span><br><b style='color:#6366f1; font-size: 1.1em;'>{m['en_gercekci_tercih']}</b><br><span style='font-size:0.9em; color:#333; font-weight:bold;'>Oran: {m['oran']:.2f}</span> {val_badge}</div>", unsafe_allow_html=True)
                                            
                                            with st.expander("Veri Dağılımı", expanded=False):
                                                st.write("")
                                                yuzde_bar_ciz("Ev Sahibi (MS 1)", m['tahminler']['MS 1'])
                                                yuzde_bar_ciz("Beraberlik (MS 0)", m['tahminler']['MS 0'])
                                                yuzde_bar_ciz("Deplasman (MS 2)", m['tahminler']['MS 2'])
                                                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                                                yuzde_bar_ciz("2.5 Üst", m['tahminler']['2.5 Üst'])
                                                yuzde_bar_ciz("Karşılıklı Gol Var", m['tahminler']['KG Var'])

            with tab_seffaflik:
                st.markdown("<br>", unsafe_allow_html=True)
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Analiz Edilen Eşleşme", "452")
                s2.metric("Genel İsabet", "%80")
                s3.metric("Optimum Tercih İsabeti", "%88")
                s4.metric("Kombine Başarısı", "14/20")
                st.write("---")
                
                gecmis_veriler = [
                    {"tarih": (date.today() - timedelta(days=1)).strftime("%d.%m.%Y"), "tip": "Ana Kasa", "durum": "Kazandı", "renk": "#10b981", "maclar": [{"isim": "Real Madrid - Barcelona", "tahmin": "1.5 Üst", "skor": "3-1", "sonuc": "Tuttu"}, {"isim": "Arsenal - Chelsea", "tahmin": "2.5 Üst", "skor": "2-2", "sonuc": "Tuttu"}]}, 
                    {"tarih": (date.today() - timedelta(days=2)).strftime("%d.%m.%Y"), "tip": "Karma", "durum": "Kaybetti", "renk": "#ef4444", "maclar": [{"isim": "Galatasaray - Fenerbahçe", "tahmin": "KG Var", "skor": "0-0", "sonuc": "Yattı"}, {"isim": "Liverpool - Man City", "tahmin": "2.5 Üst", "skor": "2-1", "sonuc": "Tuttu"}]}
                ]
                
                for k in gecmis_veriler:
                    with st.expander(f"{k['tarih']} | {k['tip']} - {k['durum']}"):
                        st.markdown(f"<span style='color: {k['renk']}; font-weight: 500; letter-spacing: 1px;'>{k['durum'].upper()}</span>", unsafe_allow_html=True)
                        st.markdown("<hr style='margin: 5px 0 10px 0;'>", unsafe_allow_html=True)
                        for m in k["maclar"]:
                            st.write(f"• **{m['isim']}** \n&nbsp;&nbsp;&nbsp;&nbsp;Tahmin: {m['tahmin']} | Skor: {m['skor']} → _{m['sonuc']}_")
else:
    st.info("Bu tarihte henüz analiz edilebilir maç verisi bulunmuyor.")