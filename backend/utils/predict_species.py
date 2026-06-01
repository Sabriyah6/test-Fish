import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Dense
import numpy as np

from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# =====================================================================
# PATCH TRIK UNTUK BYPASS EROR QUANTIZATION_CONFIG DI RENDER
# =====================================================================
# Kita simpan fungsi inisialisasi asli milik lapisan Dense
original_dense_init = Dense.__init__

def patched_dense_init(self, *args, **kwargs):
    # Jika parameter pengganggu terdeteksi dari file .h5, kita buang paksa
    if 'quantization_config' in kwargs:
        kwargs.pop('quantization_config')
    # Jalankan inisialisasi bawaan Keras tanpa parameter pengganggu
    original_dense_init(self, *args, **kwargs)

# Ganti constructor bawaan dengan fungsi patch kita
Dense.__init__ = patched_dense_init
# =====================================================================

# Load model sekali saja saat server start (Aman dari eror versi Keras)
model = load_model(Config.SPECIES_MODEL_PATH, compile=False)

def predict_species(img_path):
    """
    Menjalankan Model Tahap 1: Klasifikasi Spesies.
    Menggunakan softmax — nilai tiap kelas mewakili probabilitas.
    Mengembalikan: (nama_spesies, confidence_score)
    """
    processed_image = preprocess_image(img_path)

    prediction = model.predict(processed_image)  # shape: (1, 3)

    predicted_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    species = SPECIES_LABELS[predicted_index]

    return species, confidence