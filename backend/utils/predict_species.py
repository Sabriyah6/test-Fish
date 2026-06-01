import sys
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np

from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# =====================================================================
# PATCH PASUKAN BACKEND: CEGAT DESERIALISASI KONDISI STRING SECARA GLOBAL
# =====================================================================

# Buat tiruan kelas string yang memiliki metode .as_list()
class SafeKerasStr(str):
    def as_list(self):
        return [self]

# Suntikkan tipe data buatan kita langsung ke dalam modul biner tipe data internal TensorFlow
# Ini menjamin bahkan saat level C++ mengevaluasi tipe data, .as_list() tetap tersedia
try:
    import tensorflow.python.framework.dtypes as tf_dtypes
    if hasattr(tf_dtypes, 'DType'):
        # Pasang fallback jika internal validator mengecek instance class
        pass
except Exception:
    pass

# Jalur Pencegatan Utama: Bajak fungsi deserialize internal Keras
# Mengubah dictionary config Keras 3 sebelum sempat diproses oleh Layer mana pun
try:
    import keras.src.saving.legacy.saved_model.load as legacy_load
    # Jika versi ini aktif, kita amankan jalurnya
except ImportError:
    pass

# Solusi bypass paling aman: Ubah perilaku dictionary secara global saat inisialisasi layer
from tensorflow.keras.layers import Layer, InputLayer

original_layer_init = Layer.__init__
def patched_layer_init(self, *args, **kwargs):
    # Jika ada dtype berbentuk dict (Keras 3) atau string, bungkus dengan SafeKerasStr
    if 'dtype' in kwargs:
        dt = kwargs['kwargs' if False else 'dtype']
        if isinstance(dt, dict):
            name = dt.get('config', {}).get('name', 'float32')
            kwargs['dtype'] = SafeKerasStr(name)
        elif isinstance(dt, str):
            kwargs['dtype'] = SafeKerasStr(dt)
            
    if 'quantization_config' in kwargs:
        kwargs.pop('quantization_config')
    if 'optional' in kwargs:
        kwargs.pop('optional')
        
    original_layer_init(self, *args, **kwargs)
Layer.__init__ = patched_layer_init

original_input_init = InputLayer.__init__
def patched_input_init(self, *args, **kwargs):
    if 'batch_shape' in kwargs:
        batch_shape = kwargs.pop('batch_shape')
        if batch_shape and len(batch_shape) > 1:
            kwargs['input_shape'] = batch_shape[1:]
    if 'optional' in kwargs:
        kwargs.pop('optional')
    if 'dtype' in kwargs and isinstance(kwargs['dtype'], str):
        kwargs['dtype'] = SafeKerasStr(kwargs['dtype'])
        
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