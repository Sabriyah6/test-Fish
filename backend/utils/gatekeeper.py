import os
from config import Config

def is_valid_extension(filename):
    """
    Filter 0: Cek apakah file yang diupload adalah gambar yang diizinkan.
    Menolak file selain .jpg, .jpeg, .png
    """
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


def is_confident_species(confidence):
    """
    Filter 1: Cek apakah model cukup yakin dengan prediksi spesiesnya.
    Diubah menjadi 0.999 (99.9%) agar foto objek non-ikan seperti buaya (99.85%) 
    atau benda acak lainnya otomatis ditolak oleh sistem.
    """
    # Mengabaikan threshold config lama dan langsung menguncinya ke 0.999
    return confidence >= 0.999


def is_known_species(species_label):
    """
    Filter 2: Cek apakah spesies hasil prediksi termasuk yang didukung sistem.
    Sebagai lapisan kedua jika model memaksakan prediksi dengan confidence tinggi
    tapi labelnya tidak valid (misal bug index).
    """
    return species_label in Config.KNOWN_SPECIES


def is_confident_freshness(confidence):
    """
    Filter 3: Cek apakah model freshness cukup yakin.
    Menghindari hasil kesegaran yang meragukan.
    """
    # Diubah menjadi 0.995 (99.5%) agar deteksi kesegaran mata/insang juga lebih ketat
    return confidence >= 0.995
