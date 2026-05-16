import streamlit as st

# Sayfa ayarları
st.set_page_config(page_title="Modern POS", layout="wide")

# Veritabanı (Uygulama yenilendiğinde verilerin uçmaması için session_state kullanıyoruz)
if 'orders' not in st.session_state:
    st.session_state.orders = {f"Masa {i}": [] for i in range(1, 9)}
if 'current_table' not in st.session_state:
    st.session_state.current_table = "Masa 1"

# Menüyü artık dinamik yaptık ki admin panelinden ürün eklenip silinebilsin
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Mercimek Çorbası": 50, "Izgara Köfte": 180, "Tavuk Şiş": 150, 
        "Kola": 40, "Ayran": 25, "Künefe": 120
    }

# Günlük kasayı (ciroyu) tutacağımız kasa defteri
if 'sales' not in st.session_state:
    st.session_state.sales = {"Nakit": 0, "Kredi Kartı": 0}

st.title("🍔 Restoran POS Sistemi")

# Ekranı iki ayrı sekmeye ayırıyoruz
tab1, tab2 = st.tabs(["🛒 Sipariş Ekranı (Garson/Kasa)", "⚙️ Admin Paneli (Yönetici)"])

# ==========================================
# 1. SEKME: SİPARİŞ VE KASA EKRANI
# ==========================================
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Masalar")
        cols = st.columns(4)
        for i, table in enumerate(st.session_state.orders.keys()):
            status = "🔴" if len(st.session_state.orders[table]) > 0 else "🟢"
            if cols[i % 4].button(f"{status} {table}", key=f"btn_{table}"):
                st.session_state.current_table = table

        st.divider()

        st.subheader(f"Menü - Sipariş Ekle ({st.session_state.current_table})")
        
        if len(st.session_state.menu) == 0:
            st.warning("Menüde ürün kalmadı. Lütfen Admin panelinden yeni ürünler ekleyin.")
        else:
            menu_cols = st.columns(3)
            for i, (item, price) in enumerate(st.session_state.menu.items()):
                if menu_cols[i % 3].button(f"{item}\n{price} TL", key=f"menu_{item}"):
                    st.session_state.orders[st.session_state.current_table].append({"name": item, "price": price})

    with col2:
        st.subheader(f"🧾 Adisyon: {st.session_state.current_table}")
        
        current_order = st.session_state.orders[st.session_state.current_table]
        total = sum(item['price'] for item in current_order)
        
        if len(current_order) == 0:
            st.info("Bu masada henüz sipariş yok.")
        else:
            for item in current_order:
                st.write(f"- {item['name']} : **{item['price']} TL**")
                
            st.divider()
            st.markdown(f"### Toplam: {total} TL")
            
            # Hesap Kapatma Butonları (Kasaya para ekler)
            btn_col1, btn_col2 = st.columns(2)
            
            if btn_col1.button("💵 Nakit Kapat", use_container_width=True):
                st.session_state.sales["Nakit"] += total # Kasaya parayı ekle
                st.session_state.orders[st.session_state.current_table] = [] # Masayı boşalt
                st.success(f"{total} TL Nakit tahsil edildi!")
                st.rerun()
                
            if btn_col2.button("💳 Kart Kapat", use_container_width=True):
                st.session_state.sales["Kredi Kartı"] += total # Kasaya parayı ekle
                st.session_state.orders[st.session_state.current_table] = [] # Masayı boşalt
                st.success(f"{total} TL Kart ile tahsil edildi!")
                st.rerun()


# ==========================================
# 2. SEKME: ADMİN PANELİ (YENİ EKLENEN KISIM)
# ==========================================
with tab2:
    st.header("Yönetim Paneli")
    
    admin_col1, admin_col2 = st.columns(2)
    
    # Sol Taraf: Günlük Ciro Raporu
    with admin_col1:
        st.subheader("💰 Günlük Kasa Raporu")
        st.metric("Nakit Satışlar", f"{st.session_state.sales['Nakit']} TL")
        st.metric("Kredi Kartı Satışları", f"{st.session_state.sales['Kredi Kartı']} TL")
        
        toplam_ciro = st.session_state.sales['Nakit'] + st.session_state.sales['Kredi Kartı']
        st.metric("Günün Toplam Cirosu", f"{toplam_ciro} TL")
        
    # Sağ Taraf: Menü Yönetimi (Ekle/Sil)
    with admin_col2:
        st.subheader("🍔 Yeni Ürün Ekle")
        new_item_name = st.text_input("Eklenecek Ürün Adı")
        new_item_price = st.number_input("Ürün Fiyatı (TL)", min_value=1, step=1)
        
        if st.button("Menüye Ekle", type="primary"):
            if new_item_name:
                st.session_state.menu[new_item_name] = new_item_price
                st.success(f"{new_item_name} başarıyla eklendi!")
                st.rerun()
            else:
                st.error("Lütfen bir ürün adı yazın.")
                
        st.divider()
        
        st.subheader("🗑️ Ürün Sil")
        if len(st.session_state.menu) > 0:
            item_to_delete = st.selectbox("Silinecek ürünü seçin", list(st.session_state.menu.keys()))
            if st.button("Seçili Ürünü Sil"):
                del st.session_state.menu[item_to_delete]
                st.warning(f"{item_to_delete} menüden silindi!")
                st.rerun()