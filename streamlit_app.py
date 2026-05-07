import streamlit as st
from PIL import Image, ImageDraw
from transformers import AutoProcessor, AutoModelForCausalLM
import torch

st.set_page_config(page_title="Pencere Tespit", layout="wide")
st.title("🏠 Pencere Tespit Sistemi")
st.caption("Microsoft Florence-2-large • Hugging Face Spaces")

@st.cache_resource(show_spinner=True)
def load_model():
    model = AutoModelForCausalLM.from_pretrained(
        "microsoft/Florence-2-large",
        trust_remote_code=True,
        torch_dtype=torch.float16,   # GPU'da bellek tasarrufu
    ).to("cuda")
    
    processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large", trust_remote_code=True)
    return model, processor

model, processor = load_model()

uploaded_file = st.file_uploader("Bina fotoğrafı yükleyin", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Yüklenen Fotoğraf", use_container_width=True)

    confidence = st.slider("Güven Eşiği", 0.1, 0.95, 0.35)

    if st.button("🔍 Pencereleri Tespit Et ve Kırmızı İşaretle", type="primary", use_container_width=True):
        with st.spinner("Model pencereleri analiz ediyor... (10-20 saniye)"):
            try:
                task_prompt = "<OD>"
                text_input = "window, door, balcony door, window frame, french window"

                inputs = processor(text=text_input, images=image, return_tensors="pt").to("cuda")

                generated_ids = model.generate(
                    input_ids=inputs["input_ids"],
                    pixel_values=inputs["pixel_values"],
                    max_new_tokens=1024,
                    do_sample=False,
                    num_beams=3
                )

                generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

                results = processor.post_process_generation(
                    generated_text, 
                    task=task_prompt, 
                    image_size=(image.width, image.height)
                )

                detections = results[task_prompt]

                # Çizim
                draw_image = image.copy()
                draw = ImageDraw.Draw(draw_image, "RGBA")
                count = 0

                for bbox, label, score in zip(detections["bboxes"], 
                                            detections.get("labels", ["window"]*len(detections["bboxes"])),
                                            detections.get("scores", [0.8]*len(detections["bboxes"]))):
                    if score < confidence:
                        continue
                    x1, y1, x2, y2 = map(int, bbox)
                    draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0, 220), width=8)
                    draw.text((x1 + 8, y1 - 28), f"{label} {score:.2f}", fill=(255, 0, 0, 255))
                    count += 1

                st.success(f"✅ {count} adet pencere / kapı tespit edildi")
                st.image(draw_image, caption="Kırmızı İşaretli Sonuç", use_container_width=True)

                # İndirme
                draw_image.save("pencereler_isaretli.jpg")
                with open("pencereler_isaretli.jpg", "rb") as f:
                    st.download_button("📥 İndir", f, "pencereler_kirmizi.jpg", "image/jpeg")

            except Exception as e:
                st.error(f"Hata: {str(e)}")
