import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Evimde Gör PRO", page_icon="🏠", layout="wide")

# --- GÜVENLİK VE API AYARI (SIDEBAR) ---
with st.sidebar:
    st.header("🔑 Pro Bağlantı")
    replicate_api_token = st.text_input("Replicate API Token giriniz:", type="password")
    if replicate_api_token:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
        st.success("Bağlantı Başarılı!")
    else:
        st.warning("Lütfen Replicate API Token giriniz.")

st.title("🏠 Evimde Gör: Akıllı Söve Katalog Sistemi")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# --- SOL SÜTUN: BİNA FOTOĞRAFI ---
with col1:
    st.subheader("📸 Bina Fotoğrafı")
    uploaded_file = st.file_uploader("Binanın fotoğrafını yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uygulama Yapılacak Bina", use_container_width=True)

# --- SAĞ SÜTUN: MODEL SEÇİMİ VE ÖN İZLEME ---
with col2:
    st.subheader("🛠️ Model Kütüphanesi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Söve Modelini Seçin", tc_codes, index=0)
    
    # Kullanıcı adındaki 'halittelli' (çift t) kontrol edildi
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    
    try:
        res = requests.get(preview_url, timeout=5)
        if res.status_code == 200:
            st.image(preview_url, caption=f"Model: {selected_code}", width=300)
        else:
            st.error(f"Görsel bulunamadı: {selected_code}")
    except:
        st.warning("Kütüphane bağlantı hatası.")

st.markdown("---")

# --- PRO İŞLEMCİ: EN STABİL MODEL (422 HATASINI ÖNLEYEN YAPI) ---
if st.button("🚀 Söveyi Binaya Giydir", type="primary", use_container_width=True):
    if not uploaded_file or not replicate_api_token:
        st.error("Lütfen önce bina fotoğrafı yükleyin ve API Token girin!")
    else:
        with st.spinner(f"AI Analiz Yapıyor: {selected_code} modeli binaya uyarlanıyor..."):
            try:
                # 422 HATASINI ÖNLEYEN RESMİ MODEL ADRESİ:
                # 'replicate/controlnet-canny' her zaman en güncel versiyonu seçer.
                output = replicate.run(
                    "fofr/sdxl-controlnet-canny:44ef130f1d120937a07502c342f534e626e2a225103c80e1a8a3a936a5360f04",
                    input={
                        "image": uploaded_file,
                        "prompt": f"Professional architectural photo of a building, white {selected_code} window moldings, detailed facade, realistic shadows, high resolution",
                        "negative_prompt": "cartoon, blurry, low quality, distorted architecture, messy windows, colors",
                        "condition_scale": 0.8,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                )

                if output:
                    st.success("✅ Tasarım Başarıyla Oluşturuldu!")
                    # Çıktı formatını kontrol ediyoruz
                    result_url = output[0] if isinstance(output, list) else output
                    st.image(result_url, caption=f"Sonuç: {selected_code} Uygulaması", use_container_width=True)
                    
                    # İndirme Butonu
                    img_res = requests.get(result_url)
                    st.download_button("📥 Sonucu Bilgisayara Kaydet", data=img_res.content, file_name=f"{selected_code}_uygulama.png")

            except Exception as e:
                st.error(f"Teknik bir hata oluştu: {str(e)}")
                st.info("Eğer hata devam ederse, Token'ı Replicate panelinden 'Reset' yapıp yeni anahtarı deneyin.")

st.divider()
st.caption("Evimde Gör v8.9 PRO | Halit Telli")
