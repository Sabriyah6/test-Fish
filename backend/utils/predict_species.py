import sys
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np

from utils.preprocess import preprocess_image
from utils.labels import SPECIES_LABELS
from config import Config

# =====================================================================
# TAMENG BACKEND PAMUNGKAS: SUNTIKKAN AS_LIST() LANGSUNG KE KELAS STR DASAR
# =====================================================================
def string_as_list(self):
    """
    Suntikan paksa agar tipe data teks (str) apa pun di Python 
    memiliki metode .as_list() ketika dipanggil oleh rekonstruksi internal Keras.
    """
    return [self]

# Menambahkan fungsi .as_list() secara runtime ke dalam kelas 'str' bawaan Python
str.as_list = string_as_list
# =====================================================================

# Load model secara aman di Backend tanpa gangguan ketidakcocokan framework
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