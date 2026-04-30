import streamlit as st
import requests
import base64
import time

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")
st.title("🏠 Söve Oturucu Pro - Grok Imagine (fal.ai üzerinden)")

with st.sidebar:
    st.header("🔑 fal.ai API Key")
    fal_api_key = st.text_input(
        "fal.ai API Key", 
        type="password",
        value="c9436be0-8706-49a7-b63c-4506659a5a73:55874382a80499abca9d7d84cbcc97e0",
        help="Key otomatik yüklendi"
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
    else:
        with st.spinner("Grok Imagine çalışıyor... (15-40 saniye)"):
            try:
                building_bytes = building_file.getvalue()
                building_b64 = base64.b64encode(building_bytes).decode()

                prompt = f"""
                Bu binadaki TÜM pencerelere {selected_code} kodlu Sovetalya XPS söve modelini 
                mükemmel perspektif, gerçekçi ışık, gölge, cam yansıması ve seamless blending ile oturt. 
                Söve tam olarak orijinal ürün gibi dursun. Binada başka hiçbir şeyi değiştirme. 
                Çok profesyonel mimari render kalitesinde olsun.
                """

                # Daha stabil endpoint + retry
                for attempt in range(3):
                    try:
                        response = requests.post(
                            "https://fal.run/xai/grok-imagine-image/edit",
                            json={
                                "input": {
                                    "image_url": f"data:image/jpeg;base64,{building_b64}",
                                    "prompt": prompt
                                }
                            },
                            headers={
                                "Authorization": f"Key {fal_api_key}",
                                "Content-Type": "application/json"
                            },
                            timeout=90
                        )
                        if response.status_code == 200:
                            break
                    except:
                        time.sleep(2)
                        continue

                if response.status_code == 200:
                    result = response.json()
                    image_url = result["images"][0]["url"]
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
                st.error(f"Bağlantı hatası: {str(e)}")

st.caption("🚀 Grok Imagine (fal.run üzerinden) - Daha stabil endpoint kullanıyoruz.")
