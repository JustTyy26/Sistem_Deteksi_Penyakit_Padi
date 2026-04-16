import streamlit as st
import tensorflow as tf
import cv2
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Deteksi Penyakit Padi AI",
    page_icon="🌾",
    layout="centered"
)

# --- CSS CUSTOM (TEMA DARK BLUE PROFESIONAL) ---
st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Background Utama Biru Gelap */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
        background-attachment: fixed !important;
    }

    /* Warna Teks Putih */
    h1, h2, h3, p, li, span, div {
        color: #ffffff !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #081218 !important;
        border-right: 1px solid #1f3a4b;
    }

    /* Tombol Diagnosa */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #00b09b 0%, #96c93d 100%);
        color: white !important;
        font-weight: 700;
        border-radius: 10px;
        border: none;
        padding: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Kartu Hasil (Glassmorphism) */
    .result-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
st.title("🌾 Sistem Deteksi Penyakit Padi")
st.markdown("---")

# --- 3. SIDEBAR ---
st.sidebar.header("⚙️ Panel Kontrol")
model_choice = st.sidebar.selectbox("Pilih Model AI:", ("EfficientNetV2-S (Rekomendasi)", "ResNet50"))
st.sidebar.info("Gunakan EfficientNetV2-S untuk akurasi terbaik.")

# --- 4. LOAD MODEL ---
@st.cache(allow_output_mutation=True)
def load_prediction_models(model_name):
    try:
        if "EfficientNet" in model_name:
            return load_model('efficientnetv2s_best.h5')
        elif "ResNet" in model_name:
            return load_model('resnet50_best.h5')
    except:
        return None

model = load_prediction_models(model_choice)

if model is None:
    st.error("❌ File model tidak ditemukan. Pastikan file .h5 ada di folder yang sama.")

# --- 5. LOGIKA ---
CLASS_NAMES = ['Bacterial Leaf Blight', 'Brown Spot', 'Healthy Rice Leaf', 'Leaf Blast']

def process_image(image_file):
    file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(file_bytes, 1)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # Hitung Severity (Warna)
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    lower_green = np.array([30, 40, 40]); upper_green = np.array([90, 255, 255])
    lower_dis1 = np.array([0, 40, 40]); upper_dis1 = np.array([30, 255, 255])
    lower_dis2 = np.array([150, 40, 40]); upper_dis2 = np.array([180, 255, 255])

    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_disease = cv2.inRange(hsv, lower_dis1, upper_dis1) + cv2.inRange(hsv, lower_dis2, upper_dis2)

    total = np.count_nonzero(mask_green) + np.count_nonzero(mask_disease)
    if total == 0: ratio = 0
    else: ratio = (np.count_nonzero(mask_disease) / total) * 100
    
    if ratio == 0: grade = 0
    elif 0.1 <= ratio <= 10: grade = 1
    elif 10.1 <= ratio <= 25: grade = 2
    elif ratio > 25: grade = 3
    else: grade = 0
        
    return img_rgb, grade, ratio, mask_disease

# --- 6. TAMPILAN UTAMA ---
uploaded_file = st.file_uploader("📂 Upload Foto Daun (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and model is not None:
    uploaded_file.seek(0)
    img_rgb, grade, ratio, mask = process_image(uploaded_file)

    col1, col2 = st.columns(2)
    with col1:
        st.image(img_rgb, caption="Foto Asli", use_column_width=True)
    with col2:
        st.image(mask, caption="Area Penyakit", use_column_width=True)

    if st.button("🚀 MULAI DIAGNOSA"):
        # Resize & Prediksi
        img_resized = cv2.resize(img_rgb, (224, 224))
        img_array = np.expand_dims(img_resized, axis=0) / 255.0
        
        preds = model.predict(img_array)
        idx = np.argmax(preds[0])
        conf = np.max(preds[0])
        disease = CLASS_NAMES[idx]
        
        # Tentukan Warna
        if disease == "Healthy Rice Leaf":
            grade = 0; ratio = 0.0; severity = "Sehat"; color = "#00E676"
        else:
            if grade == 0: severity="Sangat Ringan"; color="#00E676"
            elif grade == 1: severity="Ringan"; color="#FFEA00"
            elif grade == 2: severity="Sedang"; color="#FF9100"
            elif grade == 3: severity="Berat"; color="#FF1744"

        # --- HTML KARTU HASIL (TANPA INDENTASI BIAR TIDAK ERROR) ---
        html_code = f"""
<div class="result-container" style="border-left: 10px solid {color};">
    <h3 style="text-align:center; margin-bottom:20px;">📋 Hasil Diagnosa AI</h3>
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap;">
        <div style="margin-bottom:10px;">
            <span style="font-size:14px; color:#b0bec5; font-weight:600;">JENIS PENYAKIT</span><br>
            <span style="font-size:24px; font-weight:bold; color:#4FC3F7;">{disease}</span>
        </div>
        <div style="margin-bottom:10px;">
            <span style="font-size:14px; color:#b0bec5; font-weight:600;">TINGKAT KEPARAHAN</span><br>
            <span style="font-size:24px; font-weight:bold; color:{color};">{severity} (Grade {grade})</span>
        </div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.2);">
    <div style="background:rgba(0,0,0,0.3); padding:15px; border-radius:10px;">
        <ul style="margin:0; padding-left:20px;">
            <li style="margin-bottom:5px;">Akurasi Model: <b>{conf*100:.2f}%</b></li>
            <li>Kerusakan Fisik: <b>{ratio:.2f}%</b> (Analisis Piksel)</li>
        </ul>
    </div>
</div>
"""
        st.markdown(html_code, unsafe_allow_html=True)

        # Rekomendasi
        st.write("")
        if grade >= 2:
            st.error("⚠️ PERINGATAN: Infeksi meluas! Lakukan pengendalian segera.")
        elif disease == "Healthy Rice Leaf":
            st.success("✅ TANAMAN SEHAT: Lanjutkan perawatan rutin.")
        else:
            st.warning("ℹ️ SARAN: Pantau terus perkembangan bercak.")