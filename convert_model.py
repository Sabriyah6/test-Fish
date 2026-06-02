import tensorflow as tf
print("TF version:", tf.__version__)

model_spesies = tf.keras.models.load_model(
    'backend/models/model_spesies_terbaik_final.h5', 
    compile=False
)
model_spesies.save('backend/models/model_spesies_v2.keras')
print("Model spesies selesai!")

model_freshness = tf.keras.models.load_model(
    'backend/models/best_freshness_model.h5', 
    compile=False
)
model_freshness.save('backend/models/freshness_v2.keras')
print("Model freshness selesai!")