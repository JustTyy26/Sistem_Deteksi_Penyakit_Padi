import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import DepthwiseConv2D

# Custom DepthwiseConv2D yang mengabaikan parameter 'groups' untuk kompatibilitas
class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, *args, **kwargs):
        # Hapus parameter 'groups' jika ada (untuk kompatibilitas versi lama)
        kwargs.pop('groups', None)
        super().__init__(*args, **kwargs)

# Path ke model (folder parent dari web_app)
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EFFICIENTNET_PATH = os.path.join(MODEL_DIR, 'efficientnetv2s_best.h5')
RESNET_PATH = os.path.join(MODEL_DIR, 'resnet50_best.h5')

# Debug: print paths saat startup
print(f"[DEBUG] MODEL_DIR: {MODEL_DIR}")
print(f"[DEBUG] TensorFlow version: {tf.__version__}")
print(f"[DEBUG] EFFICIENTNET exists: {os.path.exists(EFFICIENTNET_PATH)}")
print(f"[DEBUG] RESNET exists: {os.path.exists(RESNET_PATH)}")

# Nama kelas penyakit
CLASS_NAMES = ['Bacterial Leaf Blight', 'Brown Spot', 'Healthy Rice Leaf', 'Leaf Blast']

# Informasi penyakit
DISEASE_INFO = {
    'Bacterial Leaf Blight': {
        'nama_id': 'Hawar Daun Bakteri',
        'deskripsi': 'Penyakit yang disebabkan oleh bakteri Xanthomonas oryzae. Ditandai dengan bercak kuning-oranye pada tepi daun.',
        'penanganan': 'Gunakan varietas tahan, hindari pemupukan nitrogen berlebihan, dan aplikasikan bakterisida.'
    },
    'Brown Spot': {
        'nama_id': 'Bercak Coklat',
        'deskripsi': 'Penyakit jamur yang disebabkan oleh Cochliobolus miyabeanus. Ditandai dengan bercak oval berwarna coklat.',
        'penanganan': 'Perbaiki drainase, gunakan benih sehat, dan aplikasikan fungisida jika diperlukan.'
    },
    'Healthy Rice Leaf': {
        'nama_id': 'Daun Sehat',
        'deskripsi': 'Daun padi dalam kondisi sehat tanpa gejala penyakit.',
        'penanganan': 'Lanjutkan perawatan rutin dan pantau kondisi tanaman secara berkala.'
    },
    'Leaf Blast': {
        'nama_id': 'Blast Daun',
        'deskripsi': 'Penyakit jamur yang disebabkan oleh Pyricularia oryzae. Ditandai dengan bercak berbentuk berlian.',
        'penanganan': 'Gunakan varietas tahan, atur jarak tanam, dan aplikasikan fungisida sistemik.'
    }
}

# Cache model
_models = {}

# Custom objects untuk load model dengan kompatibilitas
CUSTOM_OBJECTS = {
    'DepthwiseConv2D': CustomDepthwiseConv2D
}

def get_model(model_name):
    """Load model dengan caching"""
    global _models
    
    if model_name not in _models:
        try:
            if 'efficientnet' in model_name.lower():
                print(f"[DEBUG] Loading EfficientNet from: {EFFICIENTNET_PATH}")
                if not os.path.exists(EFFICIENTNET_PATH):
                    print(f"[ERROR] File not found: {EFFICIENTNET_PATH}")
                    return None
                _models[model_name] = load_model(EFFICIENTNET_PATH, custom_objects=CUSTOM_OBJECTS, compile=False)
            elif 'resnet' in model_name.lower():
                print(f"[DEBUG] Loading ResNet from: {RESNET_PATH}")
                if not os.path.exists(RESNET_PATH):
                    print(f"[ERROR] File not found: {RESNET_PATH}")
                    return None
                _models[model_name] = load_model(RESNET_PATH, custom_objects=CUSTOM_OBJECTS, compile=False)
            print(f"[DEBUG] Model loaded successfully: {model_name}")
        except Exception as e:
            print(f"[ERROR] Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    return _models.get(model_name)

def calculate_severity(img_rgb):
    """Hitung tingkat keparahan berdasarkan analisis warna HSV"""
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    
    # Range warna hijau (sehat)
    lower_green = np.array([30, 40, 40])
    upper_green = np.array([90, 255, 255])
    
    # Range warna penyakit (kuning-coklat-merah)
    lower_dis1 = np.array([0, 40, 40])
    upper_dis1 = np.array([30, 255, 255])
    lower_dis2 = np.array([150, 40, 40])
    upper_dis2 = np.array([180, 255, 255])
    
    # Buat mask
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_disease = cv2.inRange(hsv, lower_dis1, upper_dis1) + cv2.inRange(hsv, lower_dis2, upper_dis2)
    
    # Hitung rasio
    total = np.count_nonzero(mask_green) + np.count_nonzero(mask_disease)
    if total == 0:
        ratio = 0
    else:
        ratio = (np.count_nonzero(mask_disease) / total) * 100
    
    # Tentukan grade
    if ratio == 0:
        grade = 0
    elif 0.1 <= ratio <= 10:
        grade = 1
    elif 10.1 <= ratio <= 25:
        grade = 2
    elif ratio > 25:
        grade = 3
    else:
        grade = 0
    
    return grade, ratio, mask_disease

def get_severity_label(grade):
    """Dapatkan label severity berdasarkan grade"""
    labels = {
        0: {'label': 'Sehat', 'color': '#00E676'},
        1: {'label': 'Ringan', 'color': '#FFEA00'},
        2: {'label': 'Sedang', 'color': '#FF9100'},
        3: {'label': 'Berat', 'color': '#FF1744'}
    }
    return labels.get(grade, labels[0])

def encode_image_to_base64(img):
    """Encode gambar ke base64 string"""
    import base64
    _, buffer = cv2.imencode('.png', img)
    return base64.b64encode(buffer).decode('utf-8')

def is_likely_rice_leaf(img_rgb):
    """
    Cek apakah gambar kemungkinan adalah daun padi berdasarkan:
    - Dominasi warna hijau (karakteristik daun)
    - Bentuk memanjang (aspect ratio daun padi)
    """
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    
    # Range warna hijau (daun)
    lower_green = np.array([25, 30, 30])
    upper_green = np.array([95, 255, 255])
    
    # Mask hijau
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    # Hitung persentase area hijau
    total_pixels = img_rgb.shape[0] * img_rgb.shape[1]
    green_pixels = np.count_nonzero(mask_green)
    green_ratio = (green_pixels / total_pixels) * 100
    
    # Jika area hijau < 15%, kemungkinan bukan daun
    return green_ratio >= 15, green_ratio

# Threshold confidence minimum untuk dianggap valid
MIN_CONFIDENCE_THRESHOLD = 75.0  # Minimal 75% confidence

def process_and_predict(image_bytes, model_name='efficientnet'):
    """Proses gambar dan lakukan prediksi"""
    # Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img_bgr is None:
        return {'error': 'Gambar tidak valid'}
    
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # Validasi apakah terlihat seperti daun
    is_likely_leaf, green_ratio = is_likely_rice_leaf(img_rgb)
    
    # Load model
    model = get_model(model_name)
    if model is None:
        return {'error': 'Model tidak ditemukan'}
    
    # Hitung severity dan dapatkan mask
    grade, ratio, mask_disease = calculate_severity(img_rgb)
    
    # Preprocessing untuk prediksi
    img_resized = cv2.resize(img_rgb, (224, 224))
    img_array = np.expand_dims(img_resized, axis=0) / 255.0
    
    # Prediksi
    predictions = model.predict(img_array, verbose=0)
    idx = np.argmax(predictions[0])
    confidence = float(np.max(predictions[0]))
    confidence_percent = confidence * 100
    disease = CLASS_NAMES[idx]
    
    # Cek validitas prediksi
    is_valid_prediction = True
    warning_message = None
    
    # Jika confidence rendah ATAU bukan daun hijau, berikan peringatan
    if confidence_percent < MIN_CONFIDENCE_THRESHOLD:
        is_valid_prediction = False
        warning_message = f"Gambar tidak terdeteksi sebagai daun padi. Confidence hanya {confidence_percent:.1f}%. Pastikan menggunakan foto daun padi yang jelas."
    elif not is_likely_leaf:
        is_valid_prediction = False
        warning_message = f"Gambar tidak terlihat seperti daun padi. Area hijau hanya {green_ratio:.1f}%. Gunakan foto daun padi yang jelas."
    
    # Jika sehat, reset severity
    if disease == "Healthy Rice Leaf":
        grade = 0
        ratio = 0.0
    
    severity = get_severity_label(grade)
    disease_info = DISEASE_INFO.get(disease, {})
    
    # Encode gambar original dan mask ke base64
    original_base64 = encode_image_to_base64(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
    mask_base64 = encode_image_to_base64(mask_disease)
    
    result = {
        'success': True,
        'disease': disease,
        'disease_id': disease_info.get('nama_id', disease),
        'deskripsi': disease_info.get('deskripsi', ''),
        'penanganan': disease_info.get('penanganan', ''),
        'confidence': round(confidence_percent, 2),
        'severity': {
            'grade': grade,
            'label': severity['label'],
            'color': severity['color'],
            'ratio': round(ratio, 2)
        },
        'images': {
            'original': f'data:image/png;base64,{original_base64}',
            'mask': f'data:image/png;base64,{mask_base64}'
        },
        'is_valid_prediction': is_valid_prediction,
        'warning': warning_message
    }
    
    return result
