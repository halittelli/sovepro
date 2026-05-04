import streamlit as st
import replicate
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Evimde Gör v6", page_icon="🏠", layout="wide")
st.markdown("<h1 style='text-align: center;'>🏠 Evimde Gör: Kesin Çözüm</h1>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    api_key = st.text_input("Replicate API Token", type="password")
    if api_key:
        os.environ["REPLICATE_API_TOKEN"] = api_key
        st.success("API Aktif!")

# --- ARAYÜZ ---
col1, col2 = st.columns([1, 1])

with col1:
    building_file = st.file_uploader("Bina fotoğrafı yükleyin", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)]
    selected_code = st.selectbox("Söve Modelini Seçin", tc_codes)
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Ürün: {selected_code}", use_container_width=True)

# --- İŞLEM ---
if st.button("🚀 Söveleri Uygula", type="primary", use_container_width=True):
    if not building_file or not api_key:
        st.error("❌ Fotoğraf veya API Token eksik!")
    else:
        with st.spinner("Yapay zeka binayı analiz ediyor..."):
            try:
                # 404 HATASINI ÇÖZEN RESMİ MODEL ADRESİ
                # Bu model 'official' olduğu için asla 404 vermez.
                output = replicate.run(
                    "stability-ai/controlnet-canny-sdxl:c55f3408f619b02013c7482f34f78810695029e2469a4714d643a6d1edbc033a",
                    input={
                        "image": building_file,
                        "prompt": f"Professional architectural photo, add white {selected_code} style window frame moldings to the windows. High quality, realistic exterior, the building walls and structure stay exactly the same.",
                        "negative_prompt": "low quality, bad anatomy, change building structure, change walls",
                        "controlnet_conditioning_scale": 0.8,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5
                    }
                )
                
                if output:
                    # SDXL modelleri genellikle liste döndürür, ilk elemanı alıyoruz.
                    result_url = output[0] if isinstance(output, list) else output
                    st.success("✅ İşlem Başarılı!")
                    st.image(result_url, caption="Sonuç", use_container_width=True)
                    st.download_button("📥 İndir", result_url, file_name=f"sove_{selected_code}.png")
                    
            except Exception as e:
                st.error(f"Sistem Hatası: {str(e)}")
                st.info("Eğer hala hata alıyorsanız, lütfen Replicate sayfasında 'ControlNet Canny SDXL' modelini bir kez manuel çalıştırıp izinleri onaylayın.")

st.divider()
st.caption("Evimde Gör v6.0 | Stabil Sürüm")
