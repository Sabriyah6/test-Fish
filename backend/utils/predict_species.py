import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Layer, InputLayer
import numpy as np

from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# =====================================================================
# PATCH COMPATIBILITY BACKEND: UTK MODEL KERAS 3 DI LINGKUNGAN KERAS 2
# =====================================================================

# 1. Amankan InputLayer (Mengonversi string konfigurasi ke Objek DataType Resmi)
original_input_init = InputLayer.__init__
def patched_input_init(self, *args, **kwargs):
    if 'batch_shape' in kwargs:
        batch_shape = kwargs.pop('batch_shape')
        if batch_shape and len(batch_shape) > 1:
            kwargs['input_shape'] = batch_shape[1:]
    if 'optional' in kwargs:
        kwargs.pop('optional')
        
    # Mengubah string menjadi objek tipe data resmi TensorFlow agar memiliki metode .as_list()
    if 'dtype' in kwargs and isinstance(kwargs['dtype'], str):
        kwargs['dtype'] = tf.as_dtype(kwargs['dtype'])
        
    original_input_init(self, *args, **kwargs)
InputLayer.__init__ = patched_input_init

# 2. Amankan Seluruh Lapisan Lain (Conv2D, BatchNormalization, Dense, dll)
original_layer_init = Layer.__init__
def patched_layer_init(self, *args, **kwargs):
    if 'dtype' in kwargs and isinstance(kwargs['dtype'], dict):
        dtype_config = kwargs['dtype'].get('config', {})
        dtype_name = dtype_config.get('name', 'float32')
        kwargs['dtype'] = tf.as_dtype(dtype_name)
    elif 'dtype' in kwargs and isinstance(kwargs['dtype'], str):
        kwargs['dtype'] = tf.as_dtype(kwargs['dtype'])
        
    if 'quantization_config' in kwargs:
        kwargs.pop('quantization_config')
    if 'optional' in kwargs:
        kwargs.pop('optional')
        
    original_layer_init(self, *args, **kwargs)
Layer.__init__ = patched_layer_init
# =====================================================================

# Load model milik Elfa secara aman di Backend
model = load_model(Config.SPECIES_MODEL_PATH, compile=False)

def predict_species(img_path):
    """
    Menjalankan Model Tahap 1: Klasifikasi Spesies.
    Mengembalikan: (nama_spesies, confidence_score)
    """
    processed_image = preprocess_image(img_path)
    prediction = model.predict(processed_image)

    predicted_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    species = SPECIES_LABELS[predicted_index]

    return species, confidence