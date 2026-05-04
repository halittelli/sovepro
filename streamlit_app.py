import streamlit as st
import replicate
import os

# Sayfa Ayarları
st.set_page_config(page_title="Evimde Gör Pro", page_icon="🏠", layout="wide")
st.markdown("<h1 style='text-align: center;'>Evimde Gör: Profesyonel Söve Giydirme</h1>", unsafe_allow_html=True)

# Sol panelden API anahtarı girişi
with st.sidebar:
    st.header("⚙️ Ayarlar")
    api_key = st.text_input("Replicate API Token Girin", type="password")
    if api_key:
        os.environ["REPLICATE_API_TOKEN"] = api_key
        st.success("API Anahtarı Tanımlandı!")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    building_file = st.file_uploader("Binanın fotoğrafını yükleyin", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("🏠 Söve Seçimi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)]
    selected_code = st.selectbox("Söve Modelini Seçin", tc_codes)
    # Senin GitHub repo'ndaki ürün görseli
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Seçilen Ürün: {selected_code}", use_container_width=True)

if st.button("🚀 Söveleri Otomatik Giydir", type="primary", use_container_width=True):
    if not building_file or not api_key:
        st.error("Lütfen hem bina fotoğrafını yükleyin hem de API Token'ınızı girin!")
    else:
        with st.spinner("Yapay zeka binayı analiz ediyor ve söveleri milimetrik yerleştiriyor..."):
            try:
                # GÜNCEL VE STABİL MODEL: Flux ControlNet Canny
                # Bu model binanın hatlarını mükemmel korur.
                output = replicate.run(
                    "lucataco/flux-controlnet-canny:797960613280058b730f9c2d1b74288019a31885b51239e3f60893081e64906a",
                    input={
                        "control_image": building_file, # Binanın çizgilerini al
                        "prompt": f"Professional architectural photography of the building. Add white {selected_code} style classic window frame moldings to all windows. The building exterior walls and windows must remain exactly the same as the original image. High quality, realistic texture.",
                        "num_inference_steps": 28,
                        "control_guidance_start": 0,
                        "control_guidance_end": 1,
                        "guidance_scale": 3.5
                    }
                )
                
                if output:
                    # Bazı modeller liste bazıları tek link döndürür
                    result_url = output[0] if isinstance(output, list) else output
                    st.success("✅ İşlem Tamamlandı!")
                    st.image(result_url, caption="Söve Uygulanmış Bina", use_container_width=True)
                    
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")
                st.info("İpucu: Eğer 401 hatası alıyorsanız API Token hatalıdır. 422 alıyorsanız model henüz yükleniyor olabilir.")

st.divider()
st.caption("Not: İlk çalıştırma modelin yüklenmesi nedeniyle 1-2 dakika sürebilir. Sonraki denemeler çok daha hızlı olacaktır.")
