import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Layer, InputLayer
import numpy as np

from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# =====================================================================
# ULTIMATE COMPATIBILITY PATCH: MENJINAKKAN KEBUTUHAN AS_LIST PADA KERAS 2
# =====================================================================

# 1. Buat kelas string buatan yang meniru objek tipe data dengan fungsi .as_list()
class Keras2StringCompat(str):
    def as_list(self):
        return [self]

# 2. Cegat inisialisasi InputLayer secara spesifik
original_input_init = InputLayer.__init__
def patched_input_init(self, *args, **kwargs):
    if 'batch_shape' in kwargs:
        batch_shape = kwargs.pop('batch_shape')
        if batch_shape and len(batch_shape) > 1:
            kwargs['input_shape'] = batch_shape[1:]
    if 'optional' in kwargs:
        kwargs.pop('optional')
        
    # Jika tipenya string teks biasa ('float32'), bungkus dengan kelas kompatibilitas kita
    if 'dtype' in kwargs and isinstance(kwargs['dtype'], str):
        kwargs['dtype'] = Keras2StringCompat(kwargs['dtype'])
        
    original_input_init(self, *args, **kwargs)
InputLayer.__init__ = patched_input_init

# 3. Cegat inisialisasi seluruh lapisan dasar arsitektur (Conv2D, BatchNorm, dll)
original_layer_init = Layer.__init__
def patched_layer_init(self, *args, **kwargs):
    if 'dtype' in kwargs and isinstance(kwargs['dtype'], dict):
        dtype_config = kwargs['dtype'].get('config', {})
        kwargs['dtype'] = Keras2StringCompat(dtype_config.get('name', 'float32'))
    elif 'dtype' in kwargs and isinstance(kwargs['dtype'], str):
        kwargs['dtype'] = Keras2StringCompat(kwargs['dtype'])
        
    if 'quantization_config' in kwargs:
        kwargs.pop('quantization_config')
    if 'optional' in kwargs:
        kwargs.pop('optional')
        
    original_layer_init(self, *args, **kwargs)
Layer.__init__ = patched_layer_init
# =====================================================================

# Load model secara aman tanpa kompilasi beban metrik lama
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