import streamlit as st
import requests
import pandas as pd # EKSİK OLAN SATIR BURASIYDI!
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# GÜVENLİK UYARISI: Lütfen panelinden yeni bir şifre alıp buraya yaz!
API_KEY = "9aaaf3814b469af593c5067d1fa71337"

st.set_page_config(page_title="YZ İddaa Tahmin Pro", layout="centered", page_icon="⚽")
st.title("⚽ Günün Maçları ve Yapay Zeka Analizi")

# --- YAPAY ZEKA MODELİ ---
@st.cache_resource 
def yapay_zeka_modeli_olustur():
    try:
        # 1000 maçlık CSV dosyamızı okuyoruz!
        df = pd.read_csv("gecmis_maclar.csv")
        
        # X: Öğreneceği veriler (Güç ve Form)
        X_egitim_verisi = df[["Ev_Gucu", "Dep_Gucu", "Ev_Form", "Dep_Form"]]
        
        # y: Bu verilerin sonucunda maçın nasıl bittiği (1, 0, 2)
        y_sonuclar = df["Sonuc"]
        
        # Modeli Eğitiyoruz
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_egitim_verisi, y_sonuclar)
        
        return model
    except FileNotFoundError:
        st.error("HATA: 'gecmis_maclar.csv' dosyası bulunamadı! Lütfen önce veri_olustur.py dosyasını çalıştırın.")
        return None

yapay_zeka = yapay_zeka_modeli_olustur()

def takim_istatistikleri_getir(takim_adi):
    guc = (len(takim_adi) % 5) + 5  
    form = (len(takim_adi) % 6) + 4 
    return guc, form

# --- API'DEN VERİ ÇEKME VE GÖRSELLEŞTİRME ---
@st.cache_data(ttl=3600)
def bugunun_maclarini_getir():
    bugun = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {"date": bugun}
    headers = {"x-apisports-key": API_KEY}
    
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

# --- ARAYÜZ (KULLANICI EKRANI) ---
st.markdown("### 🤖 Algoritma Tahminleri")
st.write("Aşağıdaki maçlar gerçek zamanlı çekilip, 1000 maçlık geçmiş veri seti ile eğitilmiş model tarafından analiz edilmektedir.")

if st.button("Bugünün Maçlarını Analiz Et"):
    with st.spinner("Veriler çekiliyor ve yapay zeka düşünüyor..."):
        data = bugunun_maclarini_getir()
        
        if "response" in data and len(data["response"]) > 0:
            st.success(f"Günün {len(data['response'])} maçı analiz edildi!")
            st.markdown("---")
            
            for mac in data["response"][:20]:
                ev_sahibi = mac["teams"]["home"]["name"]
                ev_logo = mac["teams"]["home"]["logo"]
                deplasman = mac["teams"]["away"]["name"]
                dep_logo = mac["teams"]["away"]["logo"]
                lig = mac["league"]["name"]
                saat = mac["fixture"]["date"][11:16] 
                
                ev_guc, ev_form = takim_istatistikleri_getir(ev_sahibi)
                dep_guc, dep_form = takim_istatistikleri_getir(deplasman)
                
                if yapay_zeka:
                    karar = yapay_zeka.predict([[ev_guc, dep_guc, ev_form, dep_form]])[0]
                    olasilik = yapay_zeka.predict_proba([[ev_guc, dep_guc, ev_form, dep_form]])[0]
                    
                    if karar == 1:
                        sonuc_metni = f"🏆 **MS 1** ({ev_sahibi})"
                        guven = olasilik[1] * 100
                    elif karar == 2:
                        sonuc_metni = f"🏆 **MS 2** ({deplasman})"
                        guven = olasilik[2] * 100
                    else:
                        sonuc_metni = "🤝 **MS 0** (Beraberlik)"
                        guven = olasilik[0] * 100
                else:
                     sonuc_metni = "Model Hatası"
                     guven = 0

                # GÖRSEL KART TASARIMI
                with st.container():
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        st.image(ev_logo, width=60)
                        st.markdown(f"**{ev_sahibi}**")
                        
                    with col2:
                        st.markdown(f"<div style='text-align: center; color: gray;'>{lig} • ⏰ {saat}</div>", unsafe_allow_html=True)
                        st.info(f"Yapay Zeka: {sonuc_metni}")
                        st.progress(int(guven))
                        st.caption(f"Modelin Karar Güveni: %{guven:.0f}")
                        
                    with col3:
                        st.image(dep_logo, width=60)
                        st.markdown(f"**{deplasman}**")
                    
                    st.markdown("---") 
        else:
            st.error("Bugün oynanacak maç bulunamadı veya API limiti doldu.")