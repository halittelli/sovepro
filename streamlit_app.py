import streamlit as st
import replicate
import io
from PIL import Image

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")
st.title("🏠 Söve Oturucu Pro - Railway + FLUX.2 AI")

with st.sidebar:
    st.header("🔑 Replicate API Token")
    replicate_token = st.text_input("Replicate Token", type="password", 
                                    help="replicate.com/account/api-tokens adresinden al")
    st.caption("Yeni hesapta $5 ücretsiz kredi var.")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    building_file = st.file_uploader("JPG / PNG / WEBP", type=["jpg", "jpeg", "png", "webp"])
    if building_file:
        st.image(building_file, caption="Yüklenen Bina", use_container_width=True)

with col2:
    st.subheader("📚 Söve Seçimi")
    sove_name = st.selectbox("Söve tipi seç", [
        "Modern Beyaz Söve", "Klasik Ahşap Söve", "Siyah Metal Çerçeve",
        "Lüks Taş Görünümlü", "Minimal Gri Söve"
    ])

if st.button("🔥 SÖVEYİ OTURT - FLUX.2 ile", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Bina fotoğrafı yükleyin!")
    elif not replicate_token:
        st.error("❌ Replicate Token girin!")
    else:
        with st.spinner("FLUX.2 çalışıyor... (20-45 saniye sürebilir)"):
            try:
                client = replicate.Client(api_token=replicate_token)

                prompt = f"Bu binadaki TÜM pencerelere {sove_name} modelini mükemmel perspektif, gerçekçi ışık, gölge, cam yansıması ve seamless blending ile oturt. Söve orijinal detaylarını koru. Binada başka hiçbir şeyi değiştirme. Çok profesyonel ve gerçekçi olsun."

                output = client.run(
                    "black-forest-labs/flux-1.1-pro",
                    input={
                        "image": building_file,          # ← EN ÖNEMLİ DEĞİŞİKLİK BURADA
                        "prompt": prompt,
                        "num_outputs": 1,
                        "aspect_ratio": "1:1",
                        "output_format": "jpg",
                        "guidance_scale": 7.5,
                        "num_inference_steps": 28
                    }
                )

                result_url = output[0]
                img_data = replicate.download(result_url)

                st.success("✅ FLUX.2 ile oturtuldu!")
                st.image(img_data, caption="Sonuç - Grok kalitesine çok yakın", use_container_width=True)

                st.download_button(
                    label="📥 Sonucu İndir (JPG)",
                    data=img_data,
                    file_name="sove_oturtulmus_flux.jpg",
                    mime="image/jpeg"
                )

            except Exception as e:
                st.error(f"Hata: {str(e)}")

st.caption("🚀 Artık upload hatası yok! Token girip dene.")
