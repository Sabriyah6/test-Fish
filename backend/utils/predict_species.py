import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np

from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# =====================================================================
# ULTIMATE CORE PATCH: INTERSEPSI LANGSUNG PADA INTERNAL FUNCTIONAL KERAS
# =====================================================================
try:
    # Lacak langsung modul functional tempat letak eror 'as_list' terjadi
    from keras.src.engine import functional
except ImportError:
    try:
        from tensorflow.python.keras.engine import functional
    except ImportError:
        import keras.engine.functional as functional

# Amankan fungsi process_node asli bawaan framework Keras
original_process_node = functional.process_node

def patched_process_node(layer, node_data, *args, **kwargs):
    """
    Tameng Inti Backend: Menjamin apa pun yang dibaca oleh process_node 
    dan tidak sengaja berubah jadi string primitive, akan disuntik kembali 
    dengan metode .as_list() palsu agar grafik model Keras 2 sukses tersusun.
    """
    # Amankan node_data atau parameter input di dalam lapisan jika tipenya terdeteksi string mentah
    if isinstance(node_data, str):
        # Definisikan kelas instan dinamis agar string primitive memiliki metode .as_list()
        class SafeString(str):
            def as_list(self):
                return [self]
        node_data = SafeString(node_data)
        
    # Lakukan sanitasi paksa jika config data di dalam layer memuat string peninggalan Keras 3
    if hasattr(layer, '_dtype') and isinstance(layer._dtype, str):
        class SafeDtypeStr(str):
            def as_list(self): return [self]
        layer._dtype = SafeDtypeStr(layer._dtype)

    return original_process_node(layer, node_data, *args, **kwargs)

# Suntikkan patch fungsional ini ke runtime core engine Keras sebelum load_model dieksekusi
functional.process_node = patched_process_node
# =====================================================================

# Load model milik Elfa secara aman di Backend tanpa kompilasi metrik lama
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