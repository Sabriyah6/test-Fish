import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import BatchNormalization
from utils.preprocess import preprocess_image
from config import Config

class CompatBatchNorm(BatchNormalization):
    def __init__(self, **kwargs):
        kwargs.pop('renorm', None)
        kwargs.pop('renorm_clipping', None)
        kwargs.pop('renorm_momentum', None)
        super().__init__(**kwargs)

_model = None

def get_model():
    global _model
    if _model is None:
        _model = load_model(
            Config.FRESHNESS_MODEL_PATH,
            custom_objects={'BatchNormalization': CompatBatchNorm},
            compile=False
        )
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