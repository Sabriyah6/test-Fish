import os

class Config:

    # Folder upload
    UPLOAD_FOLDER = 'uploads'

    # Threshold gatekeeper spesies
    # Ditingkatkan dari 0.70 ke 0.95 agar lebih ketat (gatekeeper).
    # Ini membantu menolak ikan yang BUKAN 3 ikan utama (Horse Mackerel, Red Sea Bream, Sea Bass)
    SPECIES_CONFIDENCE_THRESHOLD = 0.95

    # Threshold gatekeeper freshness
    FRESHNESS_CONFIDENCE_THRESHOLD = 0.60

    # Daftar spesies yang dikenali sistem
    KNOWN_SPECIES = ["Horse Mackerel", "Red Sea Bream", "Sea Bass"]

    # Model paths
    SPECIES_MODEL_PATH = 'models/model_spesies_v2.keras'
    FRESHNESS_MODEL_PATH = 'models/freshness_v2.keras'

    # Allowed extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # Max upload size (10MB) — sesuai dengan info yang ditampilkan di frontend
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024