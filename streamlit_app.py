import streamlit as st
import requests
import base64
import time

VERSION = "v1.8 - FLUX Kontext Pro (Ultra Katı Koruma)"

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")

st.title("🏠 Söve Oturucu Pro - FLUX.1 Kontext Pro")
st.caption(f"**Versiyon:** {VERSION} | Ultra Koruma Modu")

with st.sidebar:
    st.header("🔑 Replicate API Key")
    replicate_key = st.text_input("Replicate API Key", type="password")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📸 Bina Fotoğrafı Yükle")
    building_file = st.file_uploader("JPG / PNG / WEBP", type=["jpg", "jpeg", "png", "webp"])
    if building_file:
        st.image(building_file, caption="Yüklenen Bina", use_container_width=True)

with col2:
    st.subheader("📚 Sovetalya Söve Kütüphanesi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] + [f"TC{i:03d}" for i in range(35, 41)]
    selected_code = st.selectbox("Söve Kodunu Seçin", tc_codes)
    
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    try:
        st.image(preview_url, caption=f"{selected_code} - Sovetalya Söve", use_container_width=True)
    except:
        st.warning(f"{selected_code}.png önizlemesi yüklenemedi.")

if st.button("🔥 SÖVEYİ OTURT - FLUX Kontext Pro ile", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Bina fotoğrafı yükleyin!")
    elif not replicate_key:
        st.error("❌ Replicate API Key girin!")
    else:
        with st.spinner("FLUX çalışıyor..."):
            try:
                building_bytes = building_file.getvalue()
                building_b64 = base64.b64encode(building_bytes).decode()

                prompt = f"""
                This is a precise architectural photo editing task.

                STRICT RULES:
                - ONLY add {selected_code} Sovetalya XPS window molding to ALL existing windows and balcony doors.
                - Do NOT change the building's architecture, shape, materials, color, texture, lighting, background, or any other element.
                - Keep the exact same building structure, windows positions, and proportions.
                - The new moldings must blend seamlessly as if they were physically installed.
                - Photorealistic, professional architectural edit.

                Do not generate a new building. Edit the existing image only on the window frames.
                """

                response = requests.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={"Authorization": f"Token {replicate_key}", "Content-Type": "application/json"},
                    json={
                        "version": "black-forest-labs/flux-kontext-pro",
                        "input": {
                            "prompt": prompt.strip(),
                            "image": f"data:image/jpeg;base64,{building_b64}",
                            "num_outputs": 1,
                            "aspect_ratio": "match_input_image"
                        }
                    }
                )

                pred_id = response.json()["id"]

                for _ in range(60):
                    time.sleep(3)
                    data = requests.get(
                        f"https://api.replicate.com/v1/predictions/{pred_id}",
                        headers={"Authorization": f"Token {replicate_key}"}
                    ).json()

                    if data.get("status") == "succeeded":
                        output_url = data["output"][0]
                        img_data = requests.get(output_url).content
                        st.success("✅ Tamamlandı!")
                        st.image(img_data, caption="Sonuç", use_container_width=True)
                        st.download_button("📥 İndir", img_data, f"sove_{selected_code}.jpg", "image/jpeg")
                        break
                    elif data.get("status") in ["failed", "canceled"]:
                        st.error("Başarısız")
                        st.json(data)
                        break

            except Exception as e:
                st.error(f"Hata: {str(e)}")
