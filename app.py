import os
import zipfile
import re
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear carpeta de subida si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image(img_path):
    try:
        img = Image.open(img_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return ""

def find_case_number(text):
    match = re.search(r'(?:Caso:|No Caso)[\s]*([A-Za-z0-9\-]+)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []

    if request.method == 'POST':
        # Asegúrate de limpiar la carpeta de uploads
        for f in os.listdir(UPLOAD_FOLDER):
            os.remove(os.path.join(UPLOAD_FOLDER, f))

        files = request.files.getlist('files')
        if len(files) == 1 and files[0].filename.endswith('.zip'):
            # Manejo de archivo ZIP
            zip_file = files[0]
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(zip_file.filename))
            zip_file.save(zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(UPLOAD_FOLDER)
            os.remove(zip_path)
        else:
            # Manejo de múltiples imágenes
            for file in files:
                if allowed_file(file.filename):
                    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
                    file.save(file_path)

        # Procesar imágenes en carpeta
        for root, _, filenames in os.walk(UPLOAD_FOLDER):
            for filename in filenames:
                if allowed_file(filename):
                    img_path = os.path.join(root, filename)
                    text = extract_text_from_image(img_path)
                    case_number = find_case_number(text)
                    results.append({
                        'filename': filename,
                        'case_number': case_number or "No detectado"
                    })

        # Limpiar uploads al final si se desea
        for f in os.listdir(UPLOAD_FOLDER):
            os.remove(os.path.join(UPLOAD_FOLDER, f))

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

