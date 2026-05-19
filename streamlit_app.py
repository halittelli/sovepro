import streamlit as st
import requests
import base64
import time

VERSION = "v1.6 - FLUX Kontext Pro (Düzeltilmiş)"

st.set_page_config(page_title="Söve Oturucu Pro", page_icon="🏠", layout="wide")

st.title("🏠 Söve Oturucu Pro - FLUX.1 Kontext Pro")
st.caption(f"**Versiyon:** {VERSION}")

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
        with st.spinner("FLUX Kontext Pro çalışıyor..."):
            try:
                building_bytes = building_file.getvalue()
                building_b64 = base64.b64encode(building_bytes).decode()

                prompt = f"""
                Apply the exact {selected_code} Sovetalya XPS decorative window molding to ALL windows and balcony doors on this building.
                Maintain perfect perspective, realistic lighting, shadows, and glass reflections.
                Seamless blending, must look like real physical product installed. 
                Do not change anything else on the building or its surroundings.
                High quality professional architectural rendering.
                """

                response = requests.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {replicate_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "black-forest-labs/flux-kontext-pro",
                        "input": {
                            "prompt": prompt.strip(),
                            "image": f"data:image/jpeg;base64,{building_b64}",
                            "num_outputs": 1,
                            "aspect_ratio": "match_input_image"   # ← Düzeltilen kısım
                        }
                    }
                )

                if response.status_code == 429:
                    st.warning("Rate limit. 5-10 saniye bekleyip tekrar deneyin.")
                    st.stop()

                if response.status_code != 201:
                    st.error("Hata oluştu")
                    st.json(response.json())
                    st.stop()

                pred_id = response.json()["id"]

                # Polling
                for i in range(60):
                    time.sleep(3)
                    r = requests.get(
                        f"https://api.replicate.com/v1/predictions/{pred_id}",
                        headers={"Authorization": f"Token {replicate_key}"}
                    )
                    data = r.json()
                    status = data.get("status")

                    if status == "succeeded":
                        output_url = data["output"][0]
                        img_data = requests.get(output_url).content
                        st.success("✅ FLUX Kontext Pro ile başarıyla tamamlandı!")
                        st.image(img_data, caption="Sonuç", use_container_width=True)
                        st.download_button("📥 Sonucu İndir", img_data, f"sove_{selected_code}_flux.jpg", "image/jpeg")
                        break
                    elif status in ["failed", "canceled"]:
                        st.error("İşlem başarısız oldu")
                        st.json(data)
                        break
                    else:
                        st.info(f"İşleniyor... ({status})")

            except Exception as e:
                st.error(f"Genel Hata: {str(e)}")

st.caption(f"**Versiyon:** {VERSION}")
