import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Dense, InputLayer, Conv2D
import numpy as np

from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# =====================================================================
# PATCH TRIK ULTIMATE: BYPASS STRUKTUR DATA KERAS 3 DI LINGKUNGAN RENDER
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
    if 'batch_shape' in kwargs:
        batch_shape = kwargs.pop('batch_shape')
        if batch_shape and len(batch_shape) > 1:
            kwargs['input_shape'] = batch_shape[1:]
    if 'optional' in kwargs:
        kwargs.pop('optional')
    original_input_init(self, *args, **kwargs)
InputLayer.__init__ = patched_input_init

# 3. Patch untuk Lapisan Conv2D (Mengatasi DTypePolicy Keras 3)
original_conv2d_init = Conv2D.__init__
def patched_conv2d_init(self, *args, **kwargs):
    if 'dtype' in kwargs and isinstance(kwargs['dtype'], dict):
        # Jika berbentuk config dictionary Keras 3, ekstrak nama metodenya (misal: 'float32')
        dtype_config = kwargs['dtype'].get('config', {})
        kwargs['dtype'] = dtype_config.get('name', 'float32')
    original_conv2d_init(self, *args, **kwargs)
Conv2D.__init__ = patched_conv2d_init
# =====================================================================

# Load model (Sekarang aman dari pemeriksaan InputLayer, Dense, dan Conv2D)
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