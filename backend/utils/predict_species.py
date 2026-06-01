import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Layer
import numpy as np

from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# =====================================================================
# GLOBAL SUPER PATCH: BYPASS STRUKTUR DATA KERAS 3 DI LINGKUNGAN RENDER
# =====================================================================
original_layer_init = Layer.__init__

def patched_layer_init(self, *args, **kwargs):
    # 1. Bersihkan masalah DTypePolicy di SEMUA jenis lapisan (Conv2D, BatchNormalization, dll)
    if 'dtype' in kwargs and isinstance(kwargs['dtype'], dict):
        dtype_config = kwargs['dtype'].get('config', {})
        kwargs['dtype'] = dtype_config.get('name', 'float32')
        
    # 2. Bersihkan parameter spesifik milik Keras 3 lainnya jika ada
    if 'quantization_config' in kwargs:
        kwargs.pop('quantization_config')
    if 'optional' in kwargs:
        kwargs.pop('optional')
        
    # 3. Sesuaikan batch_shape menjadi input_shape jika dibaca oleh InputLayer
    if 'batch_shape' in kwargs:
        batch_shape = kwargs.pop('batch_shape')
        if batch_shape and len(batch_shape) > 1:
            kwargs['input_shape'] = batch_shape[1:]

    # Jalankan inisialisasi asli dengan argumen yang sudah dibersihkan
    original_layer_init(self, *args, **kwargs)

# Suntikkan fungsi modifikasi ke kelas induk dasar Keras
Layer.__init__ = patched_layer_init
# =====================================================================

# Sekarang load_model akan berjalan mulus melewati seluruh jenis lapisan arsitektur
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