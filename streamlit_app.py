import streamlit as st
import replicate
import requests

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")
st.title("🏠 Söve Oturucu Pro - Gerçek Sovetalya Modelleri")

with st.sidebar:
    st.header("🔑 Replicate API Token")
    replicate_token = st.text_input(
        "Replicate Token", 
        type="password",
        help="replicate.com/account/api-tokens adresinden kopyala ve buraya yapıştır"
    )

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    building_file = st.file_uploader("JPG / PNG / WEBP", type=["jpg", "jpeg", "png", "webp"])
    if building_file:
        st.image(building_file, caption="Yüklenen Bina", use_container_width=True)

with col2:
    st.subheader("📚 Sovetalya Söve Kütüphanesi")

    # Gerçek kodlar (TC001-TC024 + TC035-TC040)
    tc_codes = (
        [f"TC{i:03d}" for i in range(1, 25)] + 
        [f"TC{i:03d}" for i in range(35, 41)]
    )

    selected_code = st.selectbox("Söve Kodunu Seçin", tc_codes)

    # Gerçek ürün fotoğrafı (sove_images klasöründen)
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/sove_images/{selected_code}.png"
    st.image(preview_url, caption=f"{selected_code} - Sovetalya Söve", use_container_width=True)

if st.button("🔥 SÖVEYİ OTURT - Gerçek Sovetalya Modeli", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Bina fotoğrafı yükleyin!")
    elif not replicate_token:
        st.error("❌ Lütfen Replicate Token girin!")
    else:
        with st.spinner(f"{selected_code} modeli oturtuluyor... (20-45 saniye)"):
            try:
                client = replicate.Client(api_token=replicate_token)

                prompt = f"""
                Bu binadaki TÜM pencerelere {selected_code} kodlu Sovetalya XPS söve modelini 
                mükemmel perspektif, gerçekçi ışık, gölge, cam yansıması ve seamless blending ile oturt. 
                Söve tam olarak orijinal ürün gibi dursun. Binada başka hiçbir şeyi değiştirme. 
                Çok profesyonel mimari render kalitesinde olsun.
                """

                output = client.run(
                    "black-forest-labs/flux-1.1-pro",
                    input={
                        "image": building_file,
                        "prompt": prompt,
                        "num_outputs": 1,
                        "aspect_ratio": "1:1",
                        "output_format": "jpg",
                        "guidance_scale": 8.5,
                        "num_inference_steps": 30
                    }
                )

                result_url = output if isinstance(output, str) else output[0]
                img_data = requests.get(result_url).content

                st.success("✅ Sovetalya sövesi başarıyla oturtuldu!")
                st.image(img_data, caption="Sonuç", use_container_width=True)

                st.download_button(
                    label="📥 Sonucu İndir (JPG)",
                    data=img_data,
                    file_name=f"sove_{selected_code}.jpg",
                    mime="image/jpeg"
                )

            except Exception as e:
                st.error(f"Hata: {str(e)}")

st.caption("🚀 Gerçek Sovetalya fotoğrafları yüklendi. Resimleri sove_images klasörüne TCxxx.png olarak yükle.")
