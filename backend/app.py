from flask import Flask, send_from_directory
from flask_cors import CORS
import os

from routes.predict_routes import predict_bp
from config import Config

# Setup Flask to serve the frontend folder as static files
frontend_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
app = Flask(__name__, static_folder=frontend_folder, static_url_path='')
CORS(app)

# Konfigurasi dari Config class
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Pastikan folder uploads ada
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Register Blueprint
app.register_blueprint(predict_bp)

@app.route('/')
def home():
    # Serve index.html or cek.html as default
    if os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return app.send_static_file('index.html')
    return app.send_static_file('cek.html')

@app.route('/<path:path>')
def serve_frontend(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    return app.send_static_file('cek.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)