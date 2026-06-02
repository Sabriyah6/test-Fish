import sys
import tensorflow as tf
import numpy as np

# =====================================================================
# AGGRESSIVE MONKEY PATCH: BAJAK FUNGSI INTERNAL REKONSTRUKSI KERAS
# =====================================================================
try:
    # Paksa muat modul functional Keras sebelum load_model dieksekusi
    import keras.src.engine.functional as keras_functional
    
    # Simpan fungsi asli bawaan Keras
    original_process_node = keras_functional.process_node

    def patched_process_node(node, layer_dict, dictionary):
        """
        Cegat proses rekonstruksi node secara global.
        Jika input data terdeteksi berupa string biasa saat pemrosesan,
        konversi secara otomatis menjadi list agar tidak memicu error .as_list().
        """
        if hasattr(node, 'input_tensors'):
            inputs = node.input_tensors
            if isinstance(inputs, str):
                node.input_tensors = [inputs]
        return original_process_node(node, layer_dict, dictionary)

    # Ganti fungsi asli Keras dengan fungsi tameng buatan kita
    keras_functional.process_node = patched_process_node
except Exception:
    pass

# Definisikan kelas tiruan untuk DTypePolicy agar aman dari skema Keras 3
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

# Muat model secara aman dengan mendaftarkan semua komponen kustom
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