import streamlit as st
import replicate
import os

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Evimde Gör Pro v4.5", page_icon="🏠", layout="wide")

# CSS ile başlığı güzelleştirelim
st.markdown("""
    <style>
    .main-title {text-align: center; color: #1E1E1E; margin-bottom: 10px;}
    .status-text {text-align: center; color: #666; font-size: 0.9rem;}
    </style>
    <h1 class='main-title'>🏠 Evimde Gör: Profesyonel Söve Giydirme</h1>
    <p class='status-text'>Bina mimarisi korunur, sadece pencereler güncellenir.</p>
    <hr>
""", unsafe_allow_html=True)

# --- SIDEBAR (AYARLAR) ---
with st.sidebar:
    st.header("⚙️ Sistem Ayarları")
    api_key = st.text_input("Replicate API Token", type="password", help="replicate.com/account adresinden alın")
    if api_key:
        os.environ["REPLICATE_API_TOKEN"] = api_key
        st.success("API Bağlantısı Aktif!")
    else:
        st.warning("Lütfen API Token girin.")

# --- ANA ARAYÜZ ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    building_file = st.file_uploader("Değiştirilecek binayı yükleyin", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("🏠 Söve Seçimi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)]
    selected_code = st.selectbox("Söve Modelini Seçin", tc_codes)
    # GitHub'dan ürün önizleme
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Seçilen Ürün: {selected_code}", use_container_width=True)

# --- İŞLEM BUTONU VE MANTIK ---
if st.button("🚀 Söveleri Binaya Uygula", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Lütfen önce bir bina fotoğrafı yükleyin!")
    elif not api_key:
        st.error("❌ Replicate API Token eksik!")
    else:
        with st.spinner("Yapay zeka binayı analiz ediyor ve söveleri milimetrik yerleştiriyor..."):
            try:
                # EN GÜNCEL FLUX CONTROLNET MODELİ
                # 'canny' kontrolü binanın iskeletini (çizgilerini) çıkarır ve sabit tutar.
                output = replicate.run(
                    "xlabs-ai/flux-controlnet-collections:canny",
                    input={
                        "image": building_file,
                        "prompt": f"Professional architectural photography, adding white {selected_code} style classic window frame moldings to all windows. The walls, roof, sky, and surroundings of the building must remain exactly the same. Only the window borders are modified with new moldings. High resolution, realistic texture.",
                        "negative_prompt": "change building color, change house shape, distorted architecture, blurry, low quality",
                        "controlnet_conditioning_scale": 0.95, # Binayı %95 oranında 'donmuş' tutar.
                        "guidance_scale": 3.5,
                        "num_inference_steps": 28
                    }
                )
                
                if output:
                    # Çıktı genelde liste döner, ilk elemanı alıyoruz.
                    result_url = output[0] if isinstance(output, list) else output
                    st.success("✅ İşlem Başarılı!")
                    st.image(result_url, caption="Söve Uygulanmış Sonuç", use_container_width=True)
                    st.download_button("📥 Sonucu Kaydet", result_url, file_name=f"evimdegor_{selected_code}.png")
                    
            except Exception as e:
                # Hata mesajını daha anlaşılır verelim
                error_msg = str(e)
                if "422" in error_msg:
                    st.error("Hata (422): Model sürümü veya izniyle ilgili bir sorun var.")
                    st.info("Çözüm: Replicate hesabınızda 'Billing' kısmına bir kart tanımladığınızdan emin olun. Ücretsiz kredi olsa bile bu model doğrulama isteyebilir.")
                else:
                    st.error(f"Sistem Hatası: {error_msg}")

st.markdown("---")
st.caption("Evimde Gör - AI Visualizer v4.5 | Freelance 3D Artist Halit")
