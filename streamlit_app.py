import streamlit as st
import replicate
import os
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Sovetalya v40.0 - Grok Engine", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: TC007 Görsel Entegrasyon")
st.caption("Yapısal Analiz ve Şekil Projeksiyonu (Kesin Uygulama)")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Hedef Bina")
    building_file = st.file_uploader("Bina fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="İskeleti Korunacak Yapı", use_container_width=True)

with col2:
    st.subheader("📚 Söve Referansı (TC007)")
    # Doğrulanmış Imgur Ham Linki
    tc007_link = "https://i.imgur.com/Ukv1Wot.png"
    st.image(tc007_link, caption="Şekli Kopyalanacak Model", width=250)

st.divider()

if st.button("🚀 SÖVEYİ BİNAYA MONTE ET", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("Grok Algoritması: Bina hatları kilitleniyor ve söve profili işleniyor..."):
            try:
                # Bu model binanın iskeletini (Canny) çıkarır ve söveyi üzerine 'basar'
                model_id = "lucataco/flux-dev-controlnet-canny:7077759d571871f308ce387063063f272c724771239066601445903b44b82d3e"
                
                output = replicate.run(
                    model_id,
                    input={
                        "image": building_file,
                        "control_image": building_file, # Binanın tuğlalarını ve hatlarını korumak için
                        "prompt": f"Architectural photo. Add white stone moldings with the exact profile of {tc007_link} around every window. The moldings must have a 3D double-bullnose shape. KEEP the original brick wall and scaffolding 100% same. Realistic shadows and sunlight.",
                        "control_strength": 0.7, # Binayı koruma gücü (Yüksek)
                        "num_inference_steps": 30,
                        "guidance_scale": 4.5
                    }
                )

                if output:
                    st.success("✅ Uygulama Tamamlandı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Render Sonucu", use_container_width=True)
                    
                    st.download_button("📥 Kaydet", requests.get(res_url).content, file_name="sovetalya_final.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")
                st.info("Eğer 422 hatası alırsanız, bu modelin 'public' sürümünü kullanacak alternatif bir köprü kuracağım.")

st.caption("Sovetalya v40.0 | Antalya | Halit Telli")
