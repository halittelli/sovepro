import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v36.0 - TC007 Test", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Bağlantısı")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: TC007 Geometrik Testi")
st.caption("Görsel Referanslı Mimari Uygulama (IP-Adapter Teknolojisi)")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Analizi")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Uygulama Yapılacak Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("📚 Referans Söve: TC007")
    # Imgur linkini doğrudan AI'nın okuyabileceği 'direct link' formatına çevirdim
    tc007_url = "https://i.imgur.com/kF1fX7J.png" 
    st.image(tc007_url, caption="Şekli Kopyalanacak Referans (TC007)", width=300)
    st.info("AI bu görseldeki kavisleri ve derinliği baz alarak pencereleri giydirecek.")

st.divider()

if st.button("🚀 TC007 MODELİNİ BİNAYA GİYDİR", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen bina fotoğrafını yükleyin ve API Token girin!")
    else:
        with st.spinner("Grok algoritması TC007 geometrisini binaya işliyor..."):
            try:
                # REPLICATE ÜZERİNDEKİ EN GÜÇLÜ GÖRSEL REFERANS MOTORU
                model_id = "lucataco/flux-dev-ip-adapter:8119ca88a6d4b8344186f916e6d1c86e00049f5799978a3c6130932a392e2764"
                
                output = replicate.run(
                    model_id,
                    input={
                        "image": building_file, # Ana bina (Hedef)
                        "input_image": tc007_url, # Referans Söve (Kaynak)
                        # PROMPT: Grok mantığıyla binayı koruma ve şekli kopyalama talimatı
                        "prompt": "Professional architectural photography. Apply the exact white decorative stone window molding profile from the reference image onto every window. The moldings must follow the building's perspective and show realistic 3D depth and shadows. STRICTLY KEEP the original red brick texture and scaffolding. No other changes.",
                        "num_inference_steps": 30,
                        "guidance_scale": 3.5,
                        # Şekli kopyalama gücü (Grok'un yaptığı gibi yüksek tutuyoruz)
                        "ip_adapter_scale": 0.85, 
                        # Bina dokusunu (tuğlaları) koruma gücü
                        "prompt_strength": 0.35 
                    }
                )

                if output:
                    st.success("✅ İşlem Tamamlandı! TC007 başarıyla referans alındı.")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="TC007 Uygulama Sonucu", use_container_width=True)
                    
                    st.download_button("📥 Kaydet", requests.get(res_url).content, file_name="sovetalya_tc007.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")

st.caption("Sovetalya v36.0 | Antalya | Halit Telli")
