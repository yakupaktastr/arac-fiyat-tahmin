import streamlit as st
import pandas as pd
import joblib
import json
import os

st.set_page_config(page_title="Fiyat Tahmin", page_icon="🚗", layout="wide")

# JSON verisini önbelleğe alalım, her tıkta tekrar okumasın
@st.cache_data
def load_catalog():
    with open("super_katalog.json", "r", encoding="utf-8") as f:
        return json.load(f)

catalog = load_catalog()

st.title("🚗 Araç Değerleme Asistanı")
st.markdown("---")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Araç Seçimi")
    
    # Katalogdan verileri çek
    markalar = sorted(catalog.keys())
    marka = st.selectbox("Marka", markalar)
    
    seriler = sorted(catalog[marka].keys())
    seri = st.selectbox("Seri", seriler)
    
    paketler = sorted(catalog[marka][seri].keys())
    paket = st.selectbox("Paket", paketler)
    
    # Otomatik veriler
    specs = catalog[marka][seri][paket]
    st.info(f"Motor: {specs['cc']} cc / {specs['hp']} HP | Yakıt: {specs['yakit']} | Kasa: {specs['kasa']}")

with col2:
    st.subheader("Detaylar")
    
    # Akıllı seçimler (Varsayılanları katalogdan al)
    yakit_opts = ["Dizel", "Benzin", "LPG & Benzin", "Hibrit", "Elektrik"]
    kasa_opts = ["Sedan", "Hatchback", "SUV", "Station Wagon", "Coupe", "Cabrio"]
    
    yakit = st.selectbox("Yakıt", yakit_opts, index=yakit_opts.index(specs['yakit']) if specs['yakit'] in yakit_opts else 0)
    kasa = st.selectbox("Kasa", kasa_opts, index=kasa_opts.index(specs['kasa']) if specs['kasa'] in kasa_opts else 0)
    vites = st.selectbox("Vites", ["Otomatik", "Manuel", "Yarı Otomatik"])
    
    c1, c2 = st.columns(2)
    cc = c1.number_input("Motor (cc)", value=specs['cc'], step=50)
    hp = c2.number_input("Güç (HP)", value=specs['hp'], step=5)
    
    st.divider()
    
    c3, c4 = st.columns(2)
    yil = c3.number_input("Model Yılı", 1990, 2025, 2017)
    km = c4.number_input("KM", 0, 2000000, 100000, step=1000)
    
    c5, c6 = st.columns(2)
    degisen = c5.slider("Değişen", 0, 15, 0)
    boyali = c6.slider("Boyalı", 0, 15, 0)

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([3, 2, 3])

if btn_col.button("Fiyatı Hesapla", type="primary", use_container_width=True):
    model_path = f"models/model_{marka.replace(' ', '_')}.pkl"
    
    # Dosya kontrolünü basit tutuyoruz
    if not os.path.exists(model_path):
        st.error(f"Model dosyası eksik: {model_path}")
        st.stop()

    model = joblib.load(model_path)
    
    df_pred = pd.DataFrame({
        'seri': [seri],
        'vites_tipi': [vites],
        'yakit_tipi': [yakit],
        'kasa_tipi': [kasa],
        'yas': [2025 - yil],
        'kilometre': [km],
        'motor_hacmi': [cc],
        'motor_gucu': [hp],
        'degisen_sayisi': [degisen],
        'boyali_sayisi': [boyali]
    })

    fiyat = model.predict(df_pred)[0]

    # Sonuç Dialog'u
    @st.dialog("Sonuç")
    def show_result():
        st.write(f"**{marka} {seri}** - {paket}")
        st.markdown(f"<h1 style='text-align: center; color: #2e7d32;'>{fiyat:,.0f} ₺</h1>", unsafe_allow_html=True)
        st.caption("Tahmini piyasa değeridir.")
        
    show_result()