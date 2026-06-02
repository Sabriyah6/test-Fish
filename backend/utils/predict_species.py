import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import BatchNormalization
from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# Custom BatchNormalization yang toleran terhadap parameter lama
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
            Config.SPECIES_MODEL_PATH,
            custom_objects={'BatchNormalization': CompatBatchNorm},
            compile=False
        )
    return _model

def predict_species(img_path):
    model = get_model()
    processed_image = preprocess_image(img_path)
    prediction = model.predict(processed_image)
    predicted_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    species = SPECIES_LABELS[predicted_index]
    return species, confidence