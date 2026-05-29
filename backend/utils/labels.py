SPECIES_LABELS = [
    "Horse Mackerel",
    "Red Sea Bream",
    "Sea Bass"
]

# Untuk referensi, freshness ditangani langsung di predict_freshness.py
# karena menggunakan sigmoid (binary), bukan softmax (multi-class)
FRESHNESS_LABELS = [
    "Non-Fresh",  # index 0 / sigmoid mendekati 0.0
    "Fresh"       # index 1 / sigmoid mendekati 1.0
]