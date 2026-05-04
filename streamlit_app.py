import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Evimde Gör - Ücretsiz Test", page_icon="🏠", layout="wide")
st.markdown("<h1 style='text-align: center;'>🏠 Evimde Gör: Ücretsiz Test Modu</h1>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    hf_token = st.text_input("Hugging Face Token (HF_...)", type="password")
    st.info("Büyük dosyalar otomatik olarak optimize edilecektir.")

# --- GÖRSEL OPTİMİZASYON FONKSİYONU ---
def optimize_image(uploaded_file):
    img = Image.open(uploaded_file)
    # Eğer görsel çok büyükse 1024px genişliğe düşür (Hata 413'ü önler)
    if img.width > 1024 or img.height > 1024:
        img.thumbnail((1024, 1024))
    
    # Görseli bytes formatına çevir
    buffer = BytesIO()
    img = img.convert("RGB") # JPG formatı için RGB şart
    img.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()

# --- ARAYÜZ ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Bina Fotoğrafı")
    building_file = st.file_uploader("Binayı yükleyin", type=["jpg", "png", "jpeg"])
    if building_file:
        st.image(building_file, caption="Orijinal Bina", use_container_width=True)

with col2:
    st.subheader("🏠 Söve Seçimi")
    tc_codes = [f"TC{i:03d}" for i in range(1, 25)] 
    selected_code = st.selectbox("Söve Modelini Seçin", tc_codes)
    preview_url = f"https://raw.githubusercontent.com/halitelli/sovepro/main/{selected_code}.png"
    st.image(preview_url, caption=f"Seçilen Model: {selected_code}", use_container_width=True)

# --- ÜCRETSİZ MOTOR FONKSİYONU ---
def query_pix2pix(image_bytes, prompt, token):
    API_URL = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
    headers = {"Authorization": f"Bearer {token}"}
    
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    
    payload = {
        "inputs": prompt,
        "image": encoded_image,
        "parameters": {
            "num_inference_steps": 20,
            "image_guidance_scale": 1.5,
            "guidance_scale": 7.5
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"API Hatası ({response.status_code}): {response.text}")
        return None

# --- İŞLEM ---
if st.button("🚀 Ücretsiz Söve Giydirmeyi Dene", type="primary", use_container_width=True):
    if not building_file or not hf_token:
        st.error("Lütfen fotoğraf yükleyin ve HF Token girin!")
    else:
        with st.spinner("Görsel optimize ediliyor ve AI'ya gönderiliyor..."):
            try:
                # 1. Görseli optimize et (413 hatasını çözer)
                optimized_bytes = optimize_image(building_file)
                
                # 2. Talimat
                instruction = f"add white decorative architectural {selected_code} style window frame moldings to the windows. original building must be preserved."
                
                # 3. API'ye gönder
                result = query_pix2pix(optimized_bytes, instruction, hf_token)
                
                if result:
                    st.success("✅ Test tamamlandı!")
                    st.image(result, caption="AI Uygulama Sonucu (Hafifletilmiş Sürüm)", use_container_width=True)
            except Exception as e:
                st.error(f"Hata oluştu: {str(e)}")

st.divider()
st.caption("Evimde Gör v7.3 - Büyük Dosya Desteği Eklendi")
