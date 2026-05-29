from flask import Blueprint, request, jsonify
import os
import uuid

from utils.predict_species import predict_species
from utils.predict_freshness import predict_freshness
from utils.gatekeeper import (
    is_valid_extension,
    is_confident_species,
    is_known_species,
    is_confident_freshness
)
from config import Config

predict_bp = Blueprint('predict', __name__)

# ── ERROR HANDLER: file terlalu besar (413) ───────────────────────────────────
@predict_bp.app_errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'error': f'Ukuran file terlalu besar. Maksimal {Config.MAX_CONTENT_LENGTH // (1024*1024)} MB.'
    }), 413

@predict_bp.route('/predict', methods=['POST'])
def predict():

    # ── VALIDASI DASAR ──────────────────────────────────────────
    if 'image' not in request.files:
        return jsonify({'error': 'Tidak ada file gambar yang dikirim'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'File kosong, tidak ada yang dipilih'}), 400

    # Filter 0: cek ekstensi file
    if not is_valid_extension(file.filename):
        return jsonify({
            'error': 'Format file tidak didukung. Gunakan JPG atau PNG'
        }), 400

    # ── SIMPAN FILE SEMENTARA ────────────────────────────────────
    # Gunakan nama unik agar tidak bentrok jika ada request bersamaan
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
    file.save(filepath)

    try:
        # ── TAHAP 1: PREDIKSI SPESIES ────────────────────────────
        species, species_confidence = predict_species(filepath)

        print(f"[Stage 1] Spesies: {species} | Confidence: {species_confidence:.2%}")

        # Filter 1: confidence spesies terlalu rendah
        if not is_confident_species(species_confidence):
            return jsonify({
                'status': 'rejected',
                'reason': 'Gambar tidak dikenali dengan tingkat keyakinan yang tinggi sebagai salah satu dari 3 ikan utama '
                          '(Horse Mackerel, Red Sea Bream, Sea Bass). Kemungkinan ini adalah ikan jenis lain atau gambar kurang jelas.',
                'species_confidence': f'{species_confidence:.2%}'
            }), 200

        # Filter 2: spesies tidak termasuk yang didukung
        if not is_known_species(species):
            return jsonify({
                'status': 'rejected',
                'reason': f'Spesies "{species}" tidak termasuk dalam sistem. '
                          'Sistem hanya mendukung Horse Mackerel, Red Sea Bream, dan Sea Bass.',
                'species_confidence': f'{species_confidence:.2%}'
            }), 200

        # ── TAHAP 2: PREDIKSI KESEGARAN ──────────────────────────
        freshness, freshness_confidence = predict_freshness(filepath)

        print(f"[Stage 2] Kesegaran: {freshness} | Confidence: {freshness_confidence:.2%}")

        # Filter 3: confidence freshness terlalu rendah
        if not is_confident_freshness(freshness_confidence):
            return jsonify({
                'status': 'uncertain',
                'reason': 'Kondisi kesegaran ikan tidak dapat ditentukan dengan pasti. '
                          'Coba foto bagian mata atau insang ikan lebih jelas.',
                'species': species,
                'species_confidence': f'{species_confidence:.2%}',
                'freshness_confidence': f'{freshness_confidence:.2%}'
            }), 200

        # ── HASIL LENGKAP ─────────────────────────────────────────
        return jsonify({
            'status': 'success',
            'species': species,
            'species_confidence': f'{species_confidence:.2%}',
            'freshness': freshness,
            'freshness_confidence': f'{freshness_confidence:.2%}'
        }), 200

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({'error': 'Terjadi kesalahan saat memproses gambar'}), 500

    finally:
        # Selalu hapus file setelah diproses (berhasil atau gagal)
        # Di Windows, file mungkin masih terkunci oleh Pillow/OS,
        # sehingga perlu menangani PermissionError secara eksplisit.
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except PermissionError:
                import gc
                gc.collect()  # Paksa garbage collection untuk melepas file handle
                try:
                    os.remove(filepath)
                except Exception as cleanup_err:
                    print(f"[WARN] Gagal menghapus file sementara '{filepath}': {cleanup_err}")