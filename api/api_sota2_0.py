from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF para extraer texto del PDF
import re  # Biblioteca para limpieza de texto
import nltk  # Biblioteca para preprocesamiento de texto
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from openai import OpenAI
import time  # Para medir el tiempo de ejecución
from flask_cors import CORS

# Configuración inicial
api_key = ''
client = OpenAI(api_key=api_key)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas
app.config['UPLOAD_FOLDER'] = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
        print(f"Texto extraído del PDF {pdf_path}: {text[:500]}...")  # Muestra solo los primeros 500 caracteres
        return text
    except Exception as e:
        print(f"Error al extraer texto del PDF {pdf_path}: {e}")
        return ""

def clean_text(text):
    text = re.sub(r'\W+', ' ', text)  
    text = re.sub(r'\d+', '', text)   
    text = re.sub(r'\s+', ' ', text)  
    text = text.strip()               
    text = text.lower()               
    return text

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))  
    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(text.lower())
    words = [lemmatizer.lemmatize(word) for word in words if word.isalnum() and word not in stop_words]
    preprocessed_text = ' '.join(words)
    print(f"Texto preprocesado: {preprocessed_text[:500]}...")  # Muestra solo los primeros 500 caracteres
    return preprocessed_text

def obtener_estado_del_arte(textos, tema):
    mensajes = [
        {"role": "system", "content": "Eres un asistente experto en generar el estado del arte de investigaciones científicas."},
        {"role": "user", "content": f"El tema de investigación es: {tema}."},
        {"role": "user", "content": "Por favor, genera en un párrafo el estado del arte basado en los siguientes documentos y el tema de investigación:"}
    ]
    
    for i, texto in enumerate(textos):
        mensajes.append({"role": "user", "content": f"Documento {i+1}: {texto}"})

    try:
        start_time = time.time()  # Inicio del cronómetro
        respuesta = client.chat.completions.create(
            model="gpt-4o",
            messages=mensajes,
            max_tokens=1024
        )
        end_time = time.time()  # Fin del cronómetro
        elapsed_time = end_time - start_time  # Tiempo transcurrido en segundos
        print(f"Tiempo de ejecución de obtener_estado_del_arte: {elapsed_time} segundos")
        return respuesta.choices[0].message.content
    except Exception as e:
        print(f"Error al obtener estado del arte: {e}")
        return ""

@app.route("/")
def root():
    return "home"

@app.route('/process', methods=['POST'])
def process_request():
    # Obtener nombre del tema
    topic_name = request.form.get('topic_name')
    if not topic_name:
        return jsonify({"error": "No topic name provided"}), 400

    # Verificar que los archivos PDF estén presentes en la solicitud
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1.filename == '' or file2.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
        file1.save(filepath1)
        file2.save(filepath2)

        # Procesar los archivos y obtener el estado del arte
        textos = [preprocess_text(clean_text(extract_text_from_pdf(filepath))) for filepath in [filepath1, filepath2]]
        estado_del_arte = obtener_estado_del_arte(textos, topic_name)
        return jsonify({"estado_del_arte": estado_del_arte}), 200

    return jsonify({"error": "Invalid file type"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
