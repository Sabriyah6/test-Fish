from PIL import Image
import numpy as np

def preprocess_image(img_path):
    """
    Mempersiapkan gambar untuk dimasukkan ke model CNN.
    - Resize ke 224x224 piksel (sesuai input MobileNetV2)
    - Normalisasi nilai piksel ke rentang [0, 1]
    - Tambah dimensi batch agar sesuai format model

    Menggunakan 'with' statement saat membuka gambar agar file handle
    ditutup segera setelah array dibuat. Ini mencegah file lock di Windows
    yang dapat menyebabkan PermissionError saat file dihapus di blok finally.
    """
    with Image.open(img_path) as img:
        img = img.convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img, dtype='float32')

    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array