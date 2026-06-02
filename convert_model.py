import tensorflow as tf
print("TF version:", tf.__version__)

# Load dan simpan ulang model spesies
model_spesies = tf.keras.models.load_model(
    'backend/models/model_spesies_terbaik_final.h5', 
    compile=False
)
model_spesies.save('backend/models/model_spesies_v2.h5', save_format='h5')
print("Model spesies selesai!")

# Load dan simpan ulang model freshness
model_freshness = tf.keras.models.load_model(
    'backend/models/best_freshness_model.h5', 
    compile=False
)
model_freshness.save('backend/models/freshness_v2.h5', save_format='h5')
print("Model freshness selesai!")