"""
"""
Repository link: https://github.com/JustTyy26/Sistem_Deteksi_Penyakit_Padi
"""
/*************  ✨ Smart Paste 📚  *************/
/*******  6e1ba938-a978-4e97-b757-1c601d857450  *******/
Script untuk memperbaiki cell pengujian di Sistem_Deteksi_Penyakit_Padi.ipynb:
- 10 sampel total
- Setiap kelas penyakit: 3 sampel (Grade 1, 2, 3) 
- Healthy: 1 sampel
- Sampel diambil secara ACAK dari folder test
"""
import json

notebook_path = "Sistem_Deteksi_Penyakit_Padi.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# === Ubah cell pengujian (cell terakhir) ===
cell_test = nb["cells"][-1]

new_test_source = [
    "import glob\n",
    "import os\n",
    "import random\n",
    "\n",
    "# --- TEST 10 GAMBAR: SEMUA KELAS & SEMUA GRADE TERWAKILI (BALANCED) ---\n",
    "# Penyakit: masing-masing 3 sampel (Grade 1, 2, 3)\n",
    "# Healthy: 1 sampel\n",
    "# Total: 10 sampel\n",
    "\n",
    "random.seed(42)\n",
    "\n",
    "targets = [\n",
    "    ('Bacterial Leaf Blight', 'Grade_1'),\n",
    "    ('Bacterial Leaf Blight', 'Grade_2'),\n",
    "    ('Bacterial Leaf Blight', 'Grade_3'),\n",
    "    ('Brown Spot', 'Grade_1'),\n",
    "    ('Brown Spot', 'Grade_2'),\n",
    "    ('Brown Spot', 'Grade_3'),\n",
    "    ('Leaf Blast', 'Grade_1'),\n",
    "    ('Leaf Blast', 'Grade_2'),\n",
    "    ('Leaf Blast', 'Grade_3'),\n",
    "    ('Healthy Rice Leaf', 'Grade_0'),\n",
    "]\n",
    "\n",
    "test_images = []\n",
    "for class_name, grade in targets:\n",
    "    # Cari file yang cocok dengan grade tertentu\n",
    "    pattern = f\"Rice_Leaf_AUG_split/test/{class_name}/{grade}*.*\"\n",
    "    files = [f for f in glob.glob(pattern) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]\n",
    "    \n",
    "    if files:\n",
    "        # Ambil 1 file ACAK dari yang cocok\n",
    "        test_images.append(random.choice(files))\n",
    "    else:\n",
    "        # Fallback: ambil gambar acak dari kelas tersebut\n",
    "        fallback = f\"Rice_Leaf_AUG_split/test/{class_name}/*.*\"\n",
    "        fallback_files = [f for f in glob.glob(fallback) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]\n",
    "        if fallback_files:\n",
    "            test_images.append(random.choice(fallback_files))\n",
    "        else:\n",
    "            print(f\"\\u26a0\\ufe0f Peringatan: Gambar untuk {class_name} ({grade}) tidak ditemukan!\")\n",
    "\n",
    "print(f\"\\U0001f52c PENGUJIAN {len(test_images)} SAMPEL GAMBAR (BALANCED)\")\n",
    "print(\"=\"*50)\n",
    "print(\"\\U0001f4ca Distribusi sampel:\")\n",
    "print(\"  - Bacterial Leaf Blight: Grade 1, 2, 3 (3 sampel)\")\n",
    "print(\"  - Brown Spot          : Grade 1, 2, 3 (3 sampel)\")\n",
    "print(\"  - Leaf Blast          : Grade 1, 2, 3 (3 sampel)\")\n",
    "print(\"  - Healthy Rice Leaf   : Grade 0       (1 sampel)\")\n",
    "print(\"=\"*50)\n",
    "\n",
    "for i, img_path in enumerate(test_images, 1):\n",
    "    print(f\"\\n\\U0001f4f8 SAMPEL {i:02d}: {os.path.basename(img_path)}\")\n",
    "    print(\"-\"*50)\n",
    "    if os.path.exists(img_path):\n",
    "        predict_final(img_path)\n",
    "    else:\n",
    "        print(f\"\\u274c File tidak ditemukan: {img_path}\")"
]

cell_test["source"] = new_test_source
cell_test["outputs"] = []
cell_test["execution_count"] = None

# === SAVE ===
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("[OK] Notebook berhasil diupdate!")
print("     10 sampel: 3 penyakit x 3 grade + 1 healthy")
print("     Sekarang buka notebook dan Run All Cells.")
