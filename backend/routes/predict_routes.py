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

@predict_bp.app_errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'error': f'Ukuran file terlalu besar. Maksimal {Config.MAX_CONTENT_LENGTH // (1024*1024)} MB.'
    }), 413

def save_temp_file(file):
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
    file.save(filepath)
    return filepath

def cleanup(filepath):
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except PermissionError:
            import gc
            gc.collect()
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"[WARN] Gagal hapus file: {e}")

# ── ENDPOINT 1: KLASIFIKASI SPESIES ──────────────────────────────
@predict_bp.route('/predict-species', methods=['POST'])
def predict_species_route():
    if 'image' not in request.files:
        return jsonify({'error': 'Tidak ada file gambar yang dikirim'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'File kosong, tidak ada yang dipilih'}), 400

    if not is_valid_extension(file.filename):
        return jsonify({'error': 'Format file tidak didukung. Gunakan JPG atau PNG'}), 400

    filepath = save_temp_file(file)

    try:
        species, confidence = predict_species(filepath)
        print(f"[Species] {species} | {confidence:.2%}")

        if not is_confident_species(confidence):
            return jsonify({
                'status': 'rejected',
                'reason': 'Gambar tidak dikenali sebagai salah satu dari 3 ikan yang didukung '
                          '(Horse Mackerel, Red Sea Bream, Sea Bass). '
                          'Kemungkinan ini ikan jenis lain atau foto kurang jelas.',
                'confidence': f'{confidence:.2%}'
            }), 200

        if not is_known_species(species):
            return jsonify({
                'status': 'rejected',
                'reason': f'Spesies "{species}" tidak didukung sistem. '
                          'Sistem hanya mengenali Horse Mackerel, Red Sea Bream, dan Sea Bass.',
                'confidence': f'{confidence:.2%}'
            }), 200

        return jsonify({
            'status': 'success',
            'species': species,
            'confidence': f'{confidence:.2%}'
        }), 200

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({'error': 'Terjadi kesalahan saat memproses gambar'}), 500

    finally:
        cleanup(filepath)


# ── ENDPOINT 2: CEK KESEGARAN ─────────────────────────────────────
@predict_bp.route('/predict-freshness', methods=['POST'])
def predict_freshness_route():
    if 'image' not in request.files:
        return jsonify({'error': 'Tidak ada file gambar yang dikirim'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'File kosong, tidak ada yang dipilih'}), 400

    if not is_valid_extension(file.filename):
        return jsonify({'error': 'Format file tidak didukung. Gunakan JPG atau PNG'}), 400

    filepath = save_temp_file(file)

    try:
        freshness, confidence, part = predict_freshness(filepath)
        print(f"[Freshness] {freshness} ({part}) | {confidence:.2%}")

        if not is_confident_freshness(confidence):
            return jsonify({
                'status': 'uncertain',
                'reason': 'Kondisi kesegaran tidak dapat ditentukan dengan pasti. '
                          'Coba foto bagian mata atau insang ikan lebih jelas.',
                'confidence': f'{confidence:.2%}'
            }), 200

        return jsonify({
            'status': 'success',
            'freshness': freshness,
            'confidence': f'{confidence:.2%}',
            'part': part
        }), 200

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({'error': 'Terjadi kesalahan saat memproses gambar'}), 500

    finally:
        cleanup(filepath)