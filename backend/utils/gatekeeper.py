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
    Jika confidence di bawah threshold, dianggap bukan ikan yang dikenal.
    Ini menangkap: ikan jenis lain, foto bukan ikan, atau foto blur/tidak jelas.
    Threshold tinggi (misal 0.95) digunakan untuk mencegah model memaksakan
    prediksi pada ikan yang bukan 3 target utama.
    """
    return confidence >= Config.SPECIES_CONFIDENCE_THRESHOLD


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
    return confidence >= Config.FRESHNESS_CONFIDENCE_THRESHOLD