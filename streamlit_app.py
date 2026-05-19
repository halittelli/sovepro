import streamlit as st
import requests
import base64
import time

VERSION = "v1.6 - FLUX Kontext Pro Edition - 19 Mayıs 2026"

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")

st.title("🏠 Söve Oturucu Pro - FLUX.1 Kontext Pro")
st.caption(f"**Versiyon:** {VERSION} | Replicate'teki En Güçlü Editing Modeli")

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
    st.image(preview_url, caption=f"{selected_code} - Sovetalya Söve", use_container_width=True)

if st.button("🔥 SÖVEYİ OTURT - FLUX Kontext Pro ile", type="primary", use_container_width=True):
    if not building_file:
        st.error("❌ Bina fotoğrafı yükleyin!")
    elif not replicate_key:
        st.error("❌ Replicate API Key girin!")
    else:
        with st.spinner("FLUX Kontext Pro çalışıyor... (Genellikle 8-20 saniye)"):
            try:
                building_bytes = building_file.getvalue()
                building_b64 = base64.b64encode(building_bytes).decode()

                prompt = f"""
                Add the exact {selected_code} Sovetalya XPS decorative window molding to ALL windows and balcony doors on this building.
                Perfect perspective match, realistic lighting, shadows, glass reflections and seamless blending.
                The moldings must look like the original physical product. Do not change anything else on the building.
                Professional architectural visualization quality.
                """

                response = requests.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {replicate_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "black-forest-labs/flux-kontext-pro",   # En güçlü versiyon
                        "input": {
                            "prompt": prompt.strip(),
                            "image": f"data:image/jpeg;base64,{building_b64}",
                            "num_outputs": 1,
                            "aspect_ratio": "original"
                        }
                    }
                )

                if response.status_code != 201:
                    st.error("Başlatılamadı")
                    st.json(response.json())
                    st.stop()

                pred = response.json()
                pred_id = pred["id"]

                # Polling
                for _ in range(40):
                    time.sleep(2.5)
                    r = requests.get(
                        f"https://api.replicate.com/v1/predictions/{pred_id}",
                        headers={"Authorization": f"Token {replicate_key}"}
                    )
                    data = r.json()
                    status = data.get("status")

                    if status == "succeeded":
                        output_url = data["output"][0]
                        img_data = requests.get(output_url).content
                        st.success("✅ FLUX Kontext Pro ile tamamlandı!")
                        st.image(img_data, caption="Sonuç", use_container_width=True)
                        st.download_button("📥 İndir", img_data, f"sove_{selected_code}_flux.jpg", "image/jpeg")
                        break
                    elif status in ["failed", "canceled"]:
                        st.error("İşlem başarısız oldu")
                        st.json(data)
                        break
                else:
                    st.warning("Çok uzun sürdü, tekrar deneyin.")

            except Exception as e:
                st.error(f"Hata: {str(e)}")
