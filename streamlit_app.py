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
        st.warning("İşlem için geçerli bir Replicate API Token gereklidir.")

st.title("🏠 Evimde Gör: Akıllı Söve Katalog Sistemi")
st.markdown("---")

# --- ANA SÜTUNLAR ---
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
    selected_code = st.selectbox("Uygulanacak Söve Modelini Seçin", tc_codes, index=0)
    
    st.markdown(f"**Seçilen Model:** `{selected_code}`")
    
    # KESİN GITHUB ADRESİ (Ekran görüntüsüne göre halittelli ve main branch)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(preview_url, headers=headers, timeout=10)
        if response.status_code == 200:
            st.image(preview_url, caption=f"{selected_code} Kesit Görünümü", width=300)
        else:
            st.error(f"⚠️ {selected_code} görseli GitHub'da bulunamadı.")
            st.caption(f"Denenen URL: {preview_url}")
    except Exception as e:
        st.warning(f"Kütüphane bağlantı sorunu: {e}")

st.markdown("---")

# --- PRO İŞLEMCİ (REPLICATE SDXL CANNY) ---
if st.button("🚀 Söveyi Binaya Giydir", type="primary", use_container_width=True):
    if not uploaded_file or not replicate_api_token:
        st.error("Lütfen önce bina fotoğrafı yükleyin ve API Token girin!")
    else:
        with st.spinner(f"AI Analiz Yapıyor: {selected_code} modeli uygulanıyor..."):
            try:
                # REPLICATE ÜZERİNDE ŞU AN AKTİF VE STABİL OLAN SDXL-CANNY MODELİ
                # Versiyon 422 hatasını önlemek için güncel sürüm hash kodu kullanılmıştır.
                model_id = "lucataco/sdxl-controlnet:db21e45d3f051393749a435ad9998e75147348ca3ca30467a84594c736561110"
                
                # AI Talimatı (Prompt)
                # Binadaki pencerelere beyaz söve giydirmesi gerektiğini net bir şekilde söylüyoruz.
                prompt = (f"Professional architectural photo of a building facade. "
                          f"The windows are decorated with white decorative {selected_code} window moldings. "
                          f"Photorealistic, high quality, exterior design, realistic shadows.")
                
                negative_prompt = "blurry, low quality, distorted architecture, messy windows, colorful frames, cartoon"

                # İşlemi Başlat
                output = replicate.run(
                    model_id,
                    input={
                        "image": uploaded_file,
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "controlnet_conditioning_scale": 0.8,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                )

                if output:
                    st.success("✅ Tasarım Başarıyla Oluşturuldu!")
                    result_url = output[0] if isinstance(output, list) else output
                    st.image(result_url, caption=f"Sonuç: {selected_code} Uygulaması", use_container_width=True)
                    
                    # İndirme Butonu
                    img_res = requests.get(result_url)
                    st.download_button("📥 Sonucu Kaydet", data=img_res.content, file_name=f"{selected_code}_uygulama.png")

            except Exception as e:
                st.error(f"Yapay zeka motoru hatası: {str(e)}")
                st.info("İpucu: Replicate panelinizden bakiyenizi ve API Token yetkilerinizi kontrol edin.")

st.divider()
st.caption("Evimde Gör v8.7 PRO | Halit Telli | Tüm Hakları Saklıdır")
