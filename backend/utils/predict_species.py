import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Dense, InputLayer
import numpy as np

from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# =====================================================================
# PATCH TRIK MASTER UNTUK BYPASS EROR KERAS 3 DI LINGKUNGAN RENDER
# =====================================================================
# 1. Patch untuk Lapisan Dense (Mengatasi quantization_config)
original_dense_init = Dense.__init__
def patched_dense_init(self, *args, **kwargs):
    if 'quantization_config' in kwargs:
        kwargs.pop('quantization_config')
    original_dense_init(self, *args, **kwargs)
Dense.__init__ = patched_dense_init

# 2. Patch untuk Lapisan InputLayer (Mengatasi batch_shape & optional)
original_input_init = InputLayer.__init__
def patched_input_init(self, *args, **kwargs):
    # Keras 2 menggunakan 'input_shape' bukan 'batch_shape'
    if 'batch_shape' in kwargs:
        batch_shape = kwargs.pop('batch_shape')
        if batch_shape and len(batch_shape) > 1:
            kwargs['input_shape'] = batch_shape[1:]  # Ambil [224, 224, 3]
    if 'optional' in kwargs:
        kwargs.pop('optional')
    original_input_init(self, *args, **kwargs)
InputLayer.__init__ = patched_input_init
# =====================================================================

# Load model (Sekarang aman dari pemeriksaan InputLayer dan Dense)
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