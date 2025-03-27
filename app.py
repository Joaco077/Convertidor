import os
import zipfile
import pandas as pd
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

# Carpetas de trabajo
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

# Asegurar que las carpetas existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No se encontró el archivo", 400
    
    file = request.files['file']
    if file.filename == '':
        return "Nombre de archivo vacío", 400
    
    # Obtener valores del formulario
    rows = int(request.form.get('rows', 1))
    filename = request.form.get('filename', 'output')

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    print(f"Archivo recibido y guardado en: {filepath}")

    # Leer el archivo Excel ignorando la primera fila de datos (índice 1 en Pandas)
    df = pd.read_excel(filepath, skiprows=1)

    # Nombre del archivo ZIP
    zip_filename = os.path.join(OUTPUT_FOLDER, f"{filename}.zip")
    print(f"Creando ZIP en: {zip_filename}")

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for i in range(0, len(df), rows):
            txt_filename = f"{OUTPUT_FOLDER}/{filename}_{i//rows+1}.txt"
            df.iloc[i:i+rows].to_csv(txt_filename, index=False, sep='\t')
            zipf.write(txt_filename, os.path.basename(txt_filename))
            print(f"Archivo agregado al ZIP: {txt_filename}")

    if not os.path.exists(zip_filename):
        print("❌ ERROR: El archivo ZIP no se creó correctamente.")
        return "Error al generar el ZIP", 500

    print(f"✅ ZIP generado correctamente: {zip_filename}")
    return send_file(zip_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)