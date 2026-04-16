from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import base64
from utils import process_and_predict

app = Flask(__name__)
CORS(app)  # Enable CORS untuk akses dari mobile

@app.route('/')
def index():
    """Halaman utama"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint untuk prediksi penyakit"""
    try:
        image_bytes = None
        model_name = 'efficientnet'
        
        # Cek apakah ada file upload (multipart/form-data)
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'Tidak ada file yang dipilih'}), 400
            
            image_bytes = file.read()
            model_name = request.form.get('model', 'efficientnet')
        
        # Cek apakah ada base64 image (dari kamera - application/json)
        elif request.is_json:
            json_data = request.get_json()
            if json_data and 'image' in json_data:
                image_data = json_data['image']
                # Hapus header base64 jika ada
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                image_bytes = base64.b64decode(image_data)
                model_name = json_data.get('model', 'efficientnet')
        
        if image_bytes is None:
            return jsonify({'error': 'Tidak ada gambar yang dikirim'}), 400
        
        # Proses dan prediksi
        result = process_and_predict(image_bytes, model_name)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("=" * 50)
    print("[PADI] Sistem Deteksi Penyakit Padi")
    print("=" * 50)
    print("Server berjalan di: http://localhost:5000")
    print("Untuk akses dari HP, gunakan IP lokal komputer")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
