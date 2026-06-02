import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import custom_object_scope
from utils.preprocess import preprocess_image
from config import Config

# =====================================================================
# MONKEY PATCH
# =====================================================================
try:
    from keras.src.engine import base_layer
    original_base_from_config = base_layer.Layer.from_config

    @classmethod
    def patched_base_from_config(cls, config):
        config.pop('quantization_config', None)
        return original_base_from_config.__func__(cls, config)

    base_layer.Layer.from_config = patched_base_from_config
except Exception:
    pass

class FakeDTypePolicy:
    def __init__(self, *args, **kwargs):
        config = kwargs.get('config', {})
        self.name = config.get('name', 'float32') if isinstance(config, dict) else 'float32'
    def __getattr__(self, name):
        return 'float32'
# =====================================================================

_model = None

def get_model():
    global _model
    if _model is None:
        with custom_object_scope({'DTypePolicy': FakeDTypePolicy}):
            _model = load_model(Config.FRESHNESS_MODEL_PATH, compile=False)
    return _model

def predict_freshness(img_path):
    model = get_model()
    processed_image = preprocess_image(img_path)
    raw_score = float(model.predict(processed_image)[0][0])
    if raw_score >= 0.5:
        freshness = "Fresh"
        confidence = raw_score
    else:
        freshness = "Non-Fresh"
        confidence = 1.0 - raw_score
    return freshness, confidence