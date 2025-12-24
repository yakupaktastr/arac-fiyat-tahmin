import streamlit as st
import pandas as pd
import joblib
import os
import json

# 1. AYARLAR
st.set_page_config(page_title="Makine Öğrenmesi ile Fiyat Tahmini", page_icon="logo.png", layout="wide")

st.title("Makine Öğrenmesi ile Fiyat Tahmin Sistemi")
st.markdown("---")

# 2. KATALOG YÜKLEME
with open("super_katalog.json", "r", encoding="utf-8") as f:
    arac_katalogu = json.load(f)

MODEL_KLASORU = "models"

# 3. POP-UP
@st.dialog("Tahmin Sonucu")
def sonuc_goster(fiyat, marka, seri, paket):
    st.write(f"**{marka} {seri}** - {paket}")
    st.markdown(f"<h1 style='text-align: center; color: #2e7d32;'>{fiyat:,.0f} ₺</h1>", unsafe_allow_html=True)
    st.caption("Piyasa koşullarına göre tahmini değerdir.")

# 4. ARAYÜZ
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Model Bilgileri")
    
    # Seçimler
    markalar = sorted(list(arac_katalogu.keys()))
    secilen_marka = st.selectbox("Marka", markalar)
    
    seriler = sorted(list(arac_katalogu[secilen_marka].keys()))
    secilen_seri = st.selectbox("Seri", seriler)
    
    paketler = sorted(list(arac_katalogu[secilen_marka][secilen_seri].keys()))
    secilen_paket = st.selectbox("Paket / Versiyon", paketler)
    
    # --- AKILLI OTOMATİK DOLDURMA MANTIĞI ---
    # JSON'dan veriyi çekiyoruz
    oto_bilgi = arac_katalogu[secilen_marka][secilen_seri][secilen_paket]
    
    # Katalogdan gelen değerler (Varsayılanlar)
    oto_yakit = oto_bilgi["yakit"]
    oto_kasa = oto_bilgi["kasa"]
    oto_vites = "Otomatik" # Varsayılan (Veri setinden de çekebilirdik)
    oto_cc = oto_bilgi["cc"]
    oto_hp = oto_bilgi["hp"]

    st.info("ℹ️ Aşağıdaki teknik veriler paket seçiminize göre otomatik önerilmiştir. Hatalıysa değiştirebilirsiniz.")

with col2:
    st.subheader("Teknik Özellikler")
    
    # 1. YAKIT TİPİ (Akıllı Seçim)
    yakit_secenekleri = ["Dizel", "Benzin", "LPG & Benzin", "Hibrit", "Elektrik"]
    # Katalogdaki yakıt tipi listede kaçıncı sırada? Onu bulup 'index' olarak veriyoruz.
    try:
        yakit_index = yakit_secenekleri.index(oto_yakit)
    except:
        yakit_index = 0 # Bulamazsa ilkini seçsin
        
    secilen_yakit = st.selectbox("Yakıt Tipi", yakit_secenekleri, index=yakit_index)

    # 2. KASA TİPİ (Akıllı Seçim)
    kasa_secenekleri = ["Sedan", "Hatchback", "SUV", "Station Wagon", "Coupe", "Cabrio"]
    try:
        kasa_index = kasa_secenekleri.index(oto_kasa)
    except:
        kasa_index = 0
        
    secilen_kasa = st.selectbox("Kasa Tipi", kasa_secenekleri, index=kasa_index)

    # 3. VİTES (Kullanıcı seçsin ama varsayılan Otomatik olsun)
    vites_secenekleri = ["Otomatik", "Manuel", "Yarı Otomatik"]
    secilen_vites = st.selectbox("Vites Tipi", vites_secenekleri, index=0)

    # 4. MOTOR HACMİ VE GÜCÜ (Değiştirilebilir Number Input)
    c_motor1, c_motor2 = st.columns(2)
    secilen_cc = c_motor1.number_input("Motor (cc)", value=oto_cc, step=10)
    secilen_hp = c_motor2.number_input("Güç (HP)", value=oto_hp, step=5)

    st.markdown("---")
    
    # Diğerleri
    c1, c2 = st.columns(2)
    secilen_yil = c1.number_input("Yıl", 1990, 2025, 2017)
    secilen_km = c2.number_input("KM", 0, 2000000, 100000, step=5000)
    
    c3, c4 = st.columns(2)
    degisen = c3.slider("Değişen", 0, 15, 0)
    boyali = c4.slider("Boyalı", 0, 15, 0)

# 5. HESAPLA
st.markdown("<br>", unsafe_allow_html=True)
b1, b2, b3 = st.columns([3, 2, 3])
with b2:
    hesapla = st.button("FİYATI HESAPLA", use_container_width=True, type="primary")

if hesapla:
    dosya_adi = f"model_{secilen_marka.replace(' ', '_')}.pkl"
    model_yolu = os.path.join(MODEL_KLASORU, dosya_adi)
    
    # Kullanıcının ekranda son gördüğü (belki de değiştirdiği) değerleri alıyoruz
    input_data = pd.DataFrame({
        'seri': [secilen_seri],
        'vites_tipi': [secilen_vites],
        'yakit_tipi': [secilen_yakit], # Kullanıcının düzelttiği değer gider
        'kasa_tipi': [secilen_kasa],
        'yas': [2025 - secilen_yil],
        'kilometre': [secilen_km],
        'motor_hacmi': [secilen_cc],
        'motor_gucu': [secilen_hp],
        'degisen_sayisi': [degisen],
        'boyali_sayisi': [boyali]
    })

    if os.path.exists(model_yolu):
        try:
            model = joblib.load(model_yolu)
            tahmin = model.predict(input_data)[0]
            sonuc_goster(tahmin, secilen_marka, secilen_seri, secilen_paket)
        except Exception as e:
            st.error(f"Hata: {e}")
    else:
        st.error("Model dosyası bulunamadı.")