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
        st.warning("İşlem için API Token gereklidir.")

st.title("🏠 Evimde Gör: Akıllı Söve Katalog Sistemi")
st.markdown("---")

# --- ANA SÜTUNLARIN TANIMLANMASI ---
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
    
    # DÜZELTİLMİŞ GITHUB URL (halittelli - ÇİFT T İLE)
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(preview_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            st.image(preview_url, caption=f"{selected_code} Kesit Görünümü", width=300)
        else:
            # Eğer küçük .png olmazsa büyük .PNG dene
            preview_url_upper = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.PNG"
            response_upper = requests.get(preview_url_upper, headers=headers)
            if response_upper.status_code == 200:
                st.image(preview_url_upper, caption=f"{selected_code} Kesit Görünümü", width=300)
            else:
                st.error(f"⚠️ {selected_code} görseli bulunamadı.")
                st.write(f"Denenen adres: {preview_url}")
    except Exception as e:
        st.warning(f"Bağlantı sorunu: {e}")

st.markdown("---")

# --- PRO İŞLEMCİ (REPLICATE SDXL CANNY) ---
if st.button("🚀 Söveyi Binaya Giydir", type="primary", use_container_width=True):
    if not uploaded_file or not replicate_api_token:
        st.error("Lütfen önce fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner(f"AI Analiz Yapıyor: {selected_code} modeli uygulanıyor..."):
            try:
                # Replicate Resmi SDXL Canny Modeli
                model_name = "replicate/sdxl-controlnet-canny:da770d1033f9e8a7199416a246835be293526da25701a57e335532588b39447d"
                
                # AI Talimatı
                prompt = (f"professional architectural photography of a building facade, "
                          f"windows are decorated with white architectural {selected_code} moldings, "
                          f"high quality, photorealistic, clean design, detailed texture, realistic shadows")
                
                negative_prompt = "cartoon, anime, drawing, low quality, distorted windows, messy facade, colorful frames"

                output = replicate.run(
                    model_name,
                    input={
                        "image": uploaded_file,
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "condition_scale": 0.8,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                )

                if output:
                    st.success("✅ Tasarım Hazır!")
                    result_url = output[0] if isinstance(output, list) else output
                    st.image(result_url, caption=f"Sonuç: {selected_code} Uygulaması", use_container_width=True)
                    
                    img_res = requests.get(result_url)
                    st.download_button("📥 Tasarımı Bilgisayara Kaydet", data=img_res.content, file_name=f"{selected_code}_tasarim.png")

            except Exception as e:
                st.error(f"Yapay zeka motorunda bir hata oluştu: {str(e)}")

st.divider()
st.caption("Evimde Gör v8.5 PRO | Halit Telli")
