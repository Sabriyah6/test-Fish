import numpy as np
import keras
from tensorflow.keras.models import load_model
from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

_orig_base_init = keras.layers.Layer.__init__

def _patched_base_init(self, **kwargs):
    kwargs.pop('renorm', None)
    kwargs.pop('renorm_clipping', None)
    kwargs.pop('renorm_momentum', None)
    kwargs.pop('quantization_config', None)
    _orig_base_init(self, **kwargs)

keras.layers.Layer.__init__ = _patched_base_init

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

    # Cek entropy — kalau model bingung (gambar bukan ikan), entropy tinggi
    probs = prediction[0]
    entropy = -np.sum(probs * np.log(probs + 1e-10))
    max_entropy = np.log(len(probs))
    normalized_entropy = entropy / max_entropy

    print(f"[Species] Entropy: {normalized_entropy:.4f} | Confidence: {confidence:.2%}")

    # Kalau entropy > 0.8 berarti model tidak yakin → paksa confidence rendah
    if normalized_entropy > 0.8:
        confidence = 0.0

    species = SPECIES_LABELS[predicted_index]
    return species, confidence