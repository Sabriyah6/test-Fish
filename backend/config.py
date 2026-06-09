import os

class Config:

    # Folder upload
    UPLOAD_FOLDER = 'uploads'

    # Threshold gatekeeper spesies
    SPECIES_CONFIDENCE_THRESHOLD = 0.95

    # Threshold gatekeeper freshness — dinaikkan agar lebih ketat
    FRESHNESS_CONFIDENCE_THRESHOLD = 0.85

    # Daftar spesies yang dikenali sistem
    KNOWN_SPECIES = ["Horse Mackerel", "Red Sea Bream", "Sea Bass"]

    # Model paths
    SPECIES_MODEL_PATH = 'models/model_spesies_v2.keras'
    FRESHNESS_MODEL_PATH = 'models/freshness_v2.keras'

    # Allowed extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # Max upload size (10MB)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024