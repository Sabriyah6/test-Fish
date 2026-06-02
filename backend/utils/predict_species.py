import sys
import tensorflow as tf
import numpy as np

# =====================================================================
# MONKEY PATCH AMAN: PENJINAK STRUKTUR SKEMA MODEL KERAS GLOBAL
# =====================================================================
try:
    # 1. Bajak fungsi process_node untuk mengatasi masalah string dan as_list
    import keras.src.engine.functional as keras_functional
    original_process_node = keras_functional.process_node

    def patched_process_node(node, layer_dict, dictionary):
        if hasattr(node, 'input_tensors'):
            inputs = node.input_tensors
            if isinstance(inputs, str):
                node.input_tensors = [inputs]
        return original_process_node(node, layer_dict, dictionary)

    keras_functional.process_node = patched_process_node
except Exception:
    pass

try:
    # 2. Bajak fungsi deseralisasi InputLayer untuk membuang keyword asing
    import keras.src.engine.input_layer as keras_input_layer
    original_input_from_config = keras_input_layer.InputLayer.from_config

    @classmethod
    def patched_from_config(cls, config):
        # Bersihkan parameter baru yang tidak dikenali Keras versi lama
        if 'batch_shape' in config:
            batch_shape = config.pop('batch_shape')
            if batch_shape and len(batch_shape) > 1:
                config['input_shape'] = batch_shape[1:]
        if 'optional' in config:
            config.pop('optional')
        return original_input_from_config(config)

    keras_input_layer.InputLayer.from_config = patched_from_config
except Exception:
    pass

# Kelas tiruan DTypePolicy agar aman dari skema Keras 3
class FakeDTypePolicy:
    def __init__(self, *args, **kwargs):
        config = kwargs.get('config', {})
        self.name = config.get('name', 'float32') if isinstance(config, dict) else 'float32'
    def __getattr__(self, name):
        return 'float32'
# =====================================================================

from tensorflow.keras.models import load_model
from tensorflow.keras.utils import custom_object_scope
from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# Memuat model secara aman menggunakan ruang objek kustom
with custom_object_scope({'DTypePolicy': FakeDTypePolicy}):
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