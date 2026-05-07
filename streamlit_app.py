import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v42.0", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: TC007 Entegrasyonu")
st.caption("Resmi SDXL Motoru | Bina Dokusu Koruma & Geometrik Uygulama")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Uygulama Yapılacak Bina")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Cephe", use_container_width=True)

with col2:
    st.subheader("📚 Referans Söve: TC007")
    # Imgur ham linki (Doğrulanmış)
    tc007_link = "https://i.imgur.com/Ukv1Wot.png"
    st.image(tc007_link, caption="Şekli Kopyalanacak Model", width=250)

st.divider()

if st.button("🚀 TC007 MODELİNİ BİNAYA İŞLE", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("AI mimariyi analiz ediyor ve söveyi pencerelere giydiriyor..."):
            try:
                # 404 HATASINI BİTİREN RESMİ VE KALICI MODEL
                model_name = "stability-ai/sdxl-inpainting"
                
                output = replicate.run(
                    model_name,
                    input={
                        "image": building_file,
                        # Binayı koruması için maskeyi tüm resim olarak verip prompt ile alanı kısıtlıyoruz
                        "mask": building_file, 
                        "prompt": f"Professional architectural photography. Precisely install white decorative stone window moldings (söve) around every window frame. The molding profile must match the 3D double-bullnose shape seen in {tc007_link}. STRICTLY KEEP the original red brick wall texture and construction scaffolding 100% SAME. Do not change colors. Realistic shadows.",
                        "negative_prompt": "changing wall color, changing building structure, blurry, distorted windows",
                        "num_inference_steps": 35,
                        "guidance_scale": 8.0,
                        # Burası kilit: 0.35 değeri binayı 'neredeyse' dondurur.
                        "prompt_strength": 0.35 
                    }
                )

                if output:
                    st.success("✅ Tasarım Uygulandı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="TC007 Uygulama Sonucu", use_container_width=True)
                    
                    st.download_button("📥 Kaydet", requests.get(res_url).content, file_name="sove_uygulama.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")

st.caption("Sovetalya v42.0 | Antalya | Halit Telli")
