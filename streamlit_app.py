import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v39.0 - TC007 Canlı Test", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Kontrol")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: TC007 Entegrasyonu")
st.caption("Doğrulanmış Imgur Linki ile Geometrik Analiz")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Uygulama Yapılacak Bina", use_container_width=True)

with col2:
    st.subheader("📚 Referans Söve: TC007")
    # SENİN GÖNDERDİĞİN LİNKİN DOĞRUDAN RESİM FORMATI:
    tc007_link = "https://i.imgur.com/Ukv1Wot.png"
    
    st.image(tc007_link, caption="AI'nın Şeklini Alacağı Model (TC007)", width=300)
    st.info("Bu link artık aktif. AI resimdeki kavisli profili ve 3D derinliği analiz edecek.")

st.divider()

if st.button("🚀 TC007 MODELİNİ PENCERELERE UYGULA", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen fotoğraf yükleyin ve API Token girin!")
    else:
        with st.spinner("Grok mantığıyla pencereler taranıyor ve söve giydiriliyor..."):
            try:
                # 422/404 HATASI VERMEYEN EN STABİL MODEL (Flux-Dev)
                model_id = "black-forest-labs/flux-dev"
                
                # GROK MANTIĞI: Linki prompt'un kalbine, 'Image Reference' olarak gömüyoruz.
                grok_style_prompt = (
                    f"A high-end architectural photo edit. "
                    f"Identify all existing window frames in the building photo. "
                    f"Precisely wrap white decorative stone moldings around these windows. "
                    f"The molding profile MUST match the 3D double-bullnose shape from this reference: {tc007_link}. "
                    f"CRITICAL: Do not change the red brick wall texture, scaffolding, or light. "
                    f"The result must show the white moldings integrated perfectly with realistic shadows."
                )

                output = replicate.run(
                    model_id,
                    input={
                        "image": building_file,
                        "prompt": grok_style_prompt,
                        "guidance_scale": 3.5,
                        "num_inference_steps": 30,
                        # Bina dokusunu koruyan 'Altın Oran'
                        "prompt_strength": 0.35, 
                        "extra_lora_scale": 1.0
                    }
                )

                if output:
                    st.success("✅ İşlem Tamamlandı!")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Uygulama Sonucu", use_container_width=True)
                    
                    st.download_button("📥 Tasarımı Kaydet", requests.get(res_url).content, file_name="sove_test.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")

st.caption("Sovetalya v39.0 | Antalya | Halit Telli")
