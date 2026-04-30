import streamlit as st
import requests
import base64

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")
st.title("🏠 Söve Oturucu Pro - Grok Imagine (xAI Resmi Altyapısı)")

with st.sidebar:
    st.header("🔑 xAI API Key")
    xai_api_key = st.text_input(
        "xAI API Key", 
        type="password",
        help="console.x.ai → API Keys → kopyala ve buraya yapıştır"
    )

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    building_file = st.file_uploader("JPG / PNG / WEBP", type=["jpg", "jpeg", "png", "webp"])
    if building_file:
        st.image(building_file, caption="Yüklenen Bina", use_container_width=True)

with col2:
    st.subheader("📚 Sovetalya Söve Kütüphanesi")
    tc_codes = (
        [f"TC{i:03d}" for i in range(1, 25)] + 
        [f"TC{i:03d}" for i in range(35, 41)]
    )
    selected_code = st.selectbox("Söve Kodunu Seçin", tc_codes)

    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/sove_images/{selected_code}.png"
    st.image(preview_url, caption=f"{selected_code} - Sovetalya Söve", use_container_width=True)

if st.button("🔥 SÖVEYİ OTURT - Grok Imagine ile", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Bina fotoğrafı yükleyin!")
    elif not xai_api_key or len(xai_api_key) < 10:
        st.error("❌ Lütfen xAI API Key girin!")
    else:
        with st.spinner("Grok Imagine (xAI resmi) çalışıyor... (15-35 saniye)"):
            try:
                building_bytes = building_file.getvalue()
                building_b64 = base64.b64encode(building_bytes).decode()

                prompt = f"""
                Bu binadaki TÜM pencerelere {selected_code} kodlu Sovetalya XPS söve modelini 
                mükemmel perspektif, gerçekçi ışık, gölge, cam yansıması ve seamless blending ile oturt. 
                Söve tam olarak orijinal ürün gibi dursun. Binada başka hiçbir şeyi değiştirme. 
                Çok profesyonel mimari render kalitesinde olsun.
                """

                response = requests.post(
                    "https://api.x.ai/v1/images/edits",
                    headers={
                        "Authorization": f"Bearer {xai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-imagine-image",
                        "prompt": prompt,
                        "image": {
                            "url": f"data:image/jpeg;base64,{building_b64}"
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    image_url = result.get("output", {}).get("url") or result.get("url")
                    img_data = requests.get(image_url).content

                    st.success("✅ Grok Imagine ile mükemmel şekilde oturtuldu!")
                    st.image(img_data, caption="Sonuç", use_container_width=True)

                    st.download_button(
                        label="📥 Sonucu İndir (JPG)",
                        data=img_data,
                        file_name=f"sove_{selected_code}.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.error(f"API Hatası: {response.status_code} - {response.text[:400]}")

            except Exception as e:
                st.error(f"Hata: {str(e)}")

st.caption("🚀 Güvenli mod: API Key artık kodda değil, sidebar'dan giriliyor.")
