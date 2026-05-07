import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v45.0 - Grok Engine", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: TC007 Teknik Entegrasyonu")
st.caption("Grok Tarzı İskelet Kilitleme Teknolojisi (Canny ControlNet)")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Analizi")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Hatları Kilitlenecek Yapı", use_container_width=True)

with col2:
    st.subheader("📚 Referans Söve: TC007")
    tc007_link = "https://i.imgur.com/Ukv1Wot.png"
    st.image(tc007_link, caption="Şekli Kopyalanacak Model", width=250)

st.divider()

if st.button("🚀 TC007 SÖVESİNİ TEKNİK OLARAK MONTE ET", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("Grok Motoru: Bina iskeleti kilitleniyor, söve geometrisi enjekte ediliyor..."):
            try:
                # 404 VEYA 422 VERMESİ MUHTEMEL AMA BU İŞİ TEK ÇÖZEN MODEL
                output = replicate.run(
                    "lucataco/flux-dev-controlnet-canny:7077759d571871f308ce387063063f272c724771239066601445903b44b82d3e",
                    input={
                        "image": building_file,
                        "control_image": building_file, # Binayı kilitlemek için iskelet rehberi
                        # PROMPT: Grok Tarzı "Gömülü" Mimarî Emirler
                        "prompt": f"Professional architectural photography. Strictly apply white decorative stone moldings (söve) with the exact double-bullnose profile geometry of {tc007_link} around every window frame. CRITICAL: Match the building's perspective and cast realistic 3D shadows. KEEP the original concrete texture, scaffolding, and environmental ground 100% SAME. Do not paint walls, only window perimeters. No text or logos.",
                        "control_strength": 0.8, # Binayı koruma gücü (Çok Yüksek)
                        "num_inference_steps": 30,
                        "guidance_scale": 4.5
                    }
                )

                if output:
                    st.success("✅ Teknik Entegrasyon Tamamlandı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Grok-Style Render Sonucu", use_container_width=True)
                    
                    st.download_button("📥 Kaydet", requests.get(res_url).content, file_name="sovetalya_grok.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")
                if "422" in str(e) or "404" in str(e):
                    st.warning("Replicate bu modeli silmiş. Bu işi Replicate'te yapmanın başka yolu kalmadı.")

st.caption("Sovetalya v45.0 | Antalya | Halit Telli")
