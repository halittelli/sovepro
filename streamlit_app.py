import streamlit as st
import replicate
import os
import tempfile

st.set_page_config(page_title="Evimde Gör Pro v5", page_icon="🏠", layout="wide")
st.markdown("<h1 style='text-align: center;'>Evimde Gör: Söve Giydirme</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Ayarlar")
    api_key = st.text_input("Replicate API Token", type="password")
    if api_key:
        os.environ["REPLICATE_API_TOKEN"] = api_key
        st.success("API Bağlantısı Aktif!")

col1, col2 = st.columns([1, 1])

with col1:
    building_file = st.file_uploader("Bina fotoğrafı yükleyin", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal", use_container_width=True)

with col2:
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)]
    selected_code = st.selectbox("Söve Modelini Seçin", tc_codes)
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Seçilen: {selected_code}", use_container_width=True)

if st.button("🚀 Söveleri Uygula", type="primary", use_container_width=True):
    if not building_file or not api_key:
        st.error("Fotoğraf veya API Token eksik!")
    else:
        with st.spinner("Yapay zeka binayı işliyor..."):
            try:
                # 1. Dosyayı geçici olarak diske kaydet (API dosya okuma hatalarını %100 çözer)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_file.write(building_file.getvalue())
                    temp_path = tmp_file.name

                # 2. Replicate API'sine gönder (VERSİYONSUZ ve İZİN İSTEMEYEN MODEL)
                with open(temp_path, "rb") as image_data:
                    output = replicate.run(
                        "lucataco/sdxl-controlnet", 
                        input={
                            "image": image_data,
                            "prompt": f"photorealistic architecture photography, adding white {selected_code} luxury classic window frame moldings to all windows. The building walls and structure remain exactly the same.",
                            "negative_prompt": "change building structure, change walls, deformed, blurry, low resolution",
                            "condition_scale": 0.85, # Binayı koruma oranı
                            "num_inference_steps": 30
                        }
                    )
                
                if output:
                    result_url = output[0] if isinstance(output, list) else output
                    st.success("✅ İşlem Başarılı!")
                    st.image(result_url, caption="Sonuç", use_container_width=True)
                    st.download_button("📥 İndir", result_url, file_name=f"sove_{selected_code}.png")
                    
                # Temizlik
                os.remove(temp_path)

            except Exception as e:
                st.error(f"Sistem Hatası: {str(e)}")
