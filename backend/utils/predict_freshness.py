import numpy as np
import keras
from tensorflow.keras.models import load_model
from utils.preprocess import preprocess_image
from config import Config

_orig_base_init = keras.layers.Layer.__init__

def _patched_base_init(self, **kwargs):
    kwargs.pop('renorm', None)
    kwargs.pop('renorm_clipping', None)
    kwargs.pop('renorm_momentum', None)
    kwargs.pop('quantization_config', None)
    _orig_base_init(self, **kwargs)

keras.layers.Layer.__init__ = _patched_base_init

# 4 label sesuai urutan kelas model
FRESHNESS_LABELS = ['eye-fresh', 'eye-non-fresh', 'gill-fresh', 'gill-non-fresh']

_model = None

def get_model():
    global _model
    if _model is None:
        _model = load_model(Config.FRESHNESS_MODEL_PATH, compile=False)
    return _model

def predict_freshness(img_path):
    model = get_model()
    processed_image = preprocess_image(img_path)
    prediction = model.predict(processed_image)

    predicted_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    label = FRESHNESS_LABELS[predicted_index]

    if 'non' in label:
        freshness = 'Non-Fresh'
    else:
        freshness = 'Fresh'

    if 'eye' in label:
        part = 'Mata'
    else:
        part = 'Insang'

    return freshness, confidence, part