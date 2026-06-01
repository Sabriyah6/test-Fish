from tensorflow.keras.models import load_model
import numpy as np

from utils.preprocess import preprocess_image
from config import Config

# Load model sekali saja saat server start
model = load_model(Config.FRESHNESS_MODEL_PATH, compile=False)

def predict_freshness(img_path):
    """
    Menjalankan Model Tahap 2: Penilaian Kesegaran.

    Model menggunakan sigmoid (binary classification):
    - Nilai mendekati 1.0 → Fresh
    - Nilai mendekati 0.0 → Non-Fresh

    PENTING: confidence yang dikembalikan adalah seberapa yakin model
    terhadap keputusannya, bukan raw sigmoid value.
    Contoh: sigmoid=0.1 → yakin Non-Fresh → confidence=0.9
    """
    processed_image = preprocess_image(img_path)

    raw_score = float(model.predict(processed_image)[0][0])

    if raw_score >= 0.5:
        freshness = "Fresh"
        confidence = raw_score           # misal 0.85 → 85% yakin Fresh
    else:
        freshness = "Non-Fresh"
        confidence = 1.0 - raw_score     # misal raw=0.1 → 90% yakin Non-Fresh

    return freshness, confidence