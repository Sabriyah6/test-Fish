import sys
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np

from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# =====================================================================
# PATCH PASUKAN BACKEND: CEGAT PROSES DESERIALISASI INTERNAL KERAS
# =====================================================================

# 1. Buat kelas string kustom yang ramah terhadap pemanggilan .as_list()
class SafeKerasStr(str):
    def as_list(self):
        return [self]

# 2. Bajak metode inisialisasi Layer internal TensorFlow secara aman
from tensorflow.keras.layers import Layer, InputLayer

original_layer_init = Layer.__init__
def patched_layer_init(self, *args, **kwargs):
    # Jika parameter dtype terdeteksi berbentuk string biasa, bungkus dengan SafeKerasStr
    if 'dtype' in kwargs and isinstance(kwargs['dtype'], str):
        kwargs['dtype'] = SafeKerasStr(kwargs['dtype'])
    if 'quantization_config' in kwargs:
        kwargs.pop('quantization_config')
    if 'optional' in kwargs:
        kwargs.pop('optional')
    original_layer_init(self, *args, **kwargs)
Layer.__init__ = patched_layer_init

original_input_init = InputLayer.__init__
def patched_input_init(self, *args, **kwargs):
    if 'dtype' in kwargs and isinstance(kwargs['dtype'], str):
        kwargs['dtype'] = SafeKerasStr(kwargs['dtype'])
    if 'batch_shape' in kwargs:
        batch_shape = kwargs.pop('batch_shape')
        if batch_shape and len(batch_shape) > 1:
            kwargs['input_shape'] = batch_shape[1:]
    if 'optional' in kwargs:
        kwargs.pop('optional')
    original_input_init(self, *args, **kwargs)
InputLayer.__init__ = patched_input_init
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