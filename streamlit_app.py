import streamlit as st
import replicate
import os
import requests

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sovetalya v34.0 - Vision Engine", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 API Bağlantısı")
    api_token = st.text_input("Replicate Token:", type="password")
    if api_token:
        os.environ["REPLICATE_API_TOKEN"] = api_token.strip()

st.title("🏠 Sovetalya: Görsel Referanslı Mimari Motor")
st.caption("Söve Resmine Bakarak Uygulama Modu (Grok Mantığı)")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Analizi")
    building_file = st.file_uploader("Cephe fotoğrafını yükle", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Uygulama Yapılacak Bina", use_container_width=True)

with col2:
    st.subheader("📚 Söve Modeli (Referans)")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] + [f"TC{i:03d}" for i in range(35, 41)]
    selected_code = st.selectbox("Söve Seçin", tc_codes)
    
    # Söve resmi URL'si
    preview_url = f"https://raw.githubusercontent.com/halittelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"AI'nın Bakacağı Şekil: {selected_code}", width=250)

st.divider()

if st.button("🚀 SÖVEYİ REFERANS ALARAK UYGULA", type="primary", use_container_width=True):
    if not building_file or not api_token:
        st.error("Lütfen bina fotoğrafını yükleyin ve API Token girin!")
    else:
        with st.spinner("Grok mantığıyla söve şekli analiz ediliyor ve binaya işleniyor..."):
            try:
                # BU MODEL 'IMAGE-TO-IMAGE' DEĞİL, 'INSTANT-ID' VEYA 'STYLIZED' MANTIĞIDIR
                # Söveyi 'input_image' olarak, binayı 'base_image' olarak kullanır.
                model_id = "lucataco/instantid:9487c5690b22030f02758156d68b9d31d4e0e8e9" 
                
                # ALTERNATİF OLARAK FLUX-IP-ADAPTER KULLANIYORUZ
                # Bu yöntem söveyi 'görsel bir emir' olarak görür.
                
                output = replicate.run(
                    "lucataco/flux-dev-ip-adapter:8119ca88a6d4b8344186f916e6d1c86e00049f5799978a3c6130932a392e2764",
                    input={
                        "image": building_file, # Ana bina
                        "input_image": preview_url, # AI'nın bakıp şekli alacağı söve resmi
                        "prompt": f"Professional architectural installation. Apply the exact white {selected_code} stone molding profile from the reference image around every window of the building. KEEP THE ORIGINAL BRICK WALLS AND SCAFFOLDING. The molding must follow the perspective of the building.",
                        "num_inference_steps": 30,
                        "guidance_scale": 4.5,
                        "ip_adapter_scale": 0.8, # Söve resmine ne kadar sadık kalacağı (Yüksek = Söveyi kopyalar)
                        "prompt_strength": 0.4 # Bina dokusunu koruma oranı
                    }
                )

                if output:
                    st.success("✅ İşlem Tamamlandı! Söve şekli referans alındı.")
                    res_url = str(output[0]) if isinstance(output, list) else str(output)
                    st.image(res_url, caption="Final Sonuç", use_container_width=True)
                    
                    st.download_button("📥 Kaydet", requests.get(res_url).content, file_name=f"sove_{selected_code}.png")

            except Exception as e:
                st.error(f"Hata detayı: {str(e)}")

st.caption("Sovetalya v34.0 | Görsel Referans Teknolojisi")
