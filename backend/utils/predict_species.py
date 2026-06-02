import numpy as np
import keras
from tensorflow.keras.models import load_model
from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# Patch BatchNormalization agar toleran parameter lama
_orig_bn_init = keras.layers.BatchNormalization.__init__

def _patched_bn_init(self, **kwargs):
    kwargs.pop('renorm', None)
    kwargs.pop('renorm_clipping', None)
    kwargs.pop('renorm_momentum', None)
    _orig_bn_init(self, **kwargs)

keras.layers.BatchNormalization.__init__ = _patched_bn_init

_model = None

def get_model():
    global _model
    if _model is None:
        _model = load_model(Config.SPECIES_MODEL_PATH, compile=False)
    return _model

def predict_species(img_path):
    model = get_model()
    processed_image = preprocess_image(img_path)
    prediction = model.predict(processed_image)
    predicted_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    species = SPECIES_LABELS[predicted_index]
    return species, confidence