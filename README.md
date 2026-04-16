# Sistem Deteksi Penyakit Daun Padi 🌾

Proyek ini adalah sistem deteksi penyakit pada daun padi menggunakan pendekatan Deep Learning dengan arsitektur **EfficientNet** dan **ResNet50**. Sistem ini dirancang untuk membantu petani atau peneliti dalam mengidentifikasi penyakit pada tanaman padi secara cepat melalui gambar daun.

## 📋 Daftar Kelas / Kategori
Sistem ini mampu mendeteksi 4 kondisi daun padi, yaitu:
1. **Bacterial Leaf Blight** (Hawar Daun Bakteri)
2. **Brown Spot** (Bercak Coklat)
3. **Leaf Blast** (Blas Daun)
4. **Healthy Rice Leaf** (Daun Padi Sehat)

## 🏗️ Struktur Proyek
- `Model_EfficientNet.ipynb` & `Model_ResNet50.ipynb`: Notebook untuk proses pelatihan model (training).
- `Preprocessing.ipynb`: Notebook untuk prapemrosesan dataset dan augmentasi gambar.
- `web_app/`: Direktori berisi aplikasi berbasis web (Flask) untuk antarmuka pengguna (UI).
- `dataset_ta_final/` & `Rice_Leaf_AUG/`: Folder dataset (tidak diunggah ke GitHub aslinya karena keterbatasan ukuran file).
- `*.h5`: File model bobot (weights) hasil pelatihan (juga diabaikan dari repositori karena ukurannya besar).

## 🚀 Teknologi yang Digunakan
- Python
- TensorFlow / Keras (Deep Learning)
- Flask (Web Framework)
- Jupyter Notebook
- HTML, CSS, JavaScript (untuk antarmuka web)

## 💻 Cara Menjalankan Aplikasi Web (Lokal)
1. **Clone repository ini:**
   ```bash
   git clone https://github.com/JustTyy26/Sistem_Deteksi_Penyakit_Padi.git
   cd Sistem_Deteksi_Penyakit_Padi
   ```

2. **Siapkan model `.h5`:**
   Pastikan Anda memperoleh file model `efficientnetv2s_best.h5` atau `resnet50_best.h5` lalu letakkan di dalam folder `Sistem_Deteksi_Penyakit_Padi` atau sesuai pengaturan pada skrip Anda.

3. **Install dependensi yang diperlukan:**
   Pastikan Anda telah menginstal `tensorflow`, `flask`, `numpy`, `pillow`, dll. (Bisa menggunakan lingkungan virtual `venv` khusus).

4. **Jalankan aplikasi:**
   ```bash
   cd web_app
   python app.py
   ```
5. Buka browser dan akses **`http://localhost:5000`** (atau sesuai port yang tampil di terminal).

## 👨‍💻 Penulis
**Muhammad Fathi Farhat**
Tugas Akhir - 2024/2025