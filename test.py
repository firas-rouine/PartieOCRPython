
"""
Ce script Flask implémente un service web d'OCR (Reconnaissance Optique de Caractères) qui convertit des images 
et des fichiers PDF en texte, puis en braille. Le service prend en charge plusieurs langues, notamment l'arabe et 
les langues basées sur l'alphabet latin.

Les principales fonctionnalités du script sont :
1. Conversion d'images en texte avec l'OCR.
2. Conversion de fichiers PDF en images pour en extraire le texte.
3. Traduction du texte extrait en braille, en fonction de la langue spécifiée.

Modules utilisés :
- Flask : pour créer une application web légère.
- Pytesseract : une interface pour Tesseract-OCR, utilisée pour extraire du texte à partir d'images.
- PIL (Python Imaging Library) : pour la manipulation d'images.
- pdf2image : pour convertir les pages PDF en images.
- os : pour interagir avec le système de fichiers.

Fonctionnalités détaillées :
- `text_to_braille`: Fonction qui prend du texte et une langue en entrée et convertit le texte en braille 
   en fonction de la table de correspondance définie pour la langue.
   
- `ocr_endpoint`: Route Flask qui gère les requêtes POST envoyées avec une image. 
   L'image est sauvegardée, puis analysée avec Tesseract pour extraire le texte dans les langues spécifiées. 
   Le texte extrait est ensuite converti en braille et retourné sous forme de JSON.
   
- `ocr_pdf_endpoint`: Route Flask qui gère les requêtes POST envoyées avec un fichier PDF. 
   Le PDF est converti en images, puis chaque page est analysée pour extraire le texte dans les langues spécifiées. 
   Le texte de chaque page est ensuite converti en braille et retourné sous forme de JSON.

- `BRAILLE_LATIN` et `BRAILLE_ARABIC`: Tables de conversion qui mappent les caractères des alphabets latin et arabe 
   vers leurs équivalents en braille.

- `if __name__ == '__main__'`: Démarre l'application Flask en mode debug pour permettre le développement local.
"""
from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import os
from flask_cors import CORS
#import fitz  # PyMuPDF
from pdf2image import convert_from_path
from pdf2image import convert_from_path
# Initialize the Flask application
app = Flask(__name__)
CORS(app)
output_folder = 'temp'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
# Table de conversion de texte en braille pour l'anglais et le français
BRAILLE_LATIN = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽',
    'z': '⠵',
    'é': '⠿', 'à': '⠷', 'ç': '⠯',
    '0': '⠴', '1': '⠂', '2': '⠆', '3': '⠒', '4': '⠲',
    '5': '⠢', '6': '⠖', '7': '⠶', '8': '⠦', '9': '⠔',
    ' ': ' ', '.': '⠲', ',': '⠠', '!': '⠖', '?': '⠦',
    '-': '⠤', '_': '⠸⠤', '*': '⠔',
    ':': '⠒', ';': '⠰', "'": '⠄', '"': '⠐',
    '(': '⠐', ')': '⠐', '@': '⠈⠤', '&': '⠮', '/': '⠤⠆'
}

# Table de conversion de texte en braille pour l'arabe
BRAILLE_ARABIC = {
    'ا': '⠁', 'ب': '⠃', 'ت': '⠞', 'ث': '⠹', 'ج': '⠚',
    'ح': '⠓', 'خ': '⠮', 'د': '⠙', 'ذ': '⠹', 'ر': '⠗',
    'ز': '⠵', 'س': '⠎', 'ش': '⠩', 'ص': '⠯', 'ض': '⠿',
    'ط': '⠾', 'ظ': '⠾', 'ع': '⠯', 'غ': '⠱', 'ف': '⠋',
    'ق': '⠟', 'ك': '⠅', 'ل': '⠇', 'م': '⠍', 'ن': '⠝',
    'ه': '⠓', 'و': '⠺', 'ي': '⠊', 'ى': '⠁', 'ء': '⠄',
    'ئ': '⠢', 'ؤ': '⠂', 'ة': '⠤', 'لا': '⠯', 'أ': '⠁',
    'إ': '⠊', 'آ': '⠜'
}
def text_to_braille(text, language):
    if language == 'ara':
        braille_alphabet = BRAILLE_ARABIC
    else:
        braille_alphabet = BRAILLE_LATIN
    
    braille_text = ''.join(braille_alphabet.get(char, char) for char in text)
    return braille_text

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    try:
        # Debugging: Check the request files and form data
        print("Received files:", request.files)
        print("Received form data:", request.form)
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        image = request.files['image']
        languages = request.form.getlist('language[]')

        image_path = os.path.join(output_folder, 'temp_image.png')
        image.save(image_path)
        
        results = {}

        for language in languages:
            text = pytesseract.image_to_string(Image.open(image_path), lang=language)
            print(f"Extracted text for language {language}: {text}")

            # braille_text = text_to_braille(text.lower(), language)
            # print(f"Braille text for language {language}: {braille_text}")
            
            results[language] = {
                'text': text,
                # 'braille': braille_text
            }

        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    

@app.route('/ocr_pdf', methods=['POST'])
def ocr_pdf_endpoint():
    try:
        pdf_file = request.files['pdf']
        languages = request.form.getlist('language[]')
        
        pdf_path = os.path.join(output_folder, 'temp_pdf.pdf')
        pdf_file.save(pdf_path)
        
        # Ensure correct Poppler path
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        poppler_path = r"C:/Users/Firas/Downloads/poppler-24.07.0/Library/bin"
        images = convert_from_path(pdf_path, dpi=300, output_folder=output_folder, poppler_path=poppler_path)
        
        results = {}
        for i, image in enumerate(images):
            image_path = os.path.join(output_folder, f'temp_image_{i}.png')
            image.save(image_path)
            
          
            for language in languages:
                text = pytesseract.image_to_string(image, lang=language)
                print(f"Extracted text for language {language}: {text}")
                # braille_text = text_to_braille(text.lower(), language)
               
                # print(f"Braille text for language {language}: {braille_text}")
                results[language] = {
                    'text': text,
                    # 'braille': braille_text
                }
            
           
        
        return jsonify(results)
    
    except Exception as e:
       
        return jsonify({'error': str(e)}), 500
@app.route('/transcribe_braille', methods=['POST'])
def transcribe_braille_endpoint():
    try:
        # Get the text and language from form-data
        text = request.form.get('text', '')  # Default to empty string if not provided
        language = request.form.get('language', 'eng')  # Default to English if not provided

        braille_text = text_to_braille(text.lower(), language)
        return braille_text  # Return plain text braille result

    except Exception as e:
        return str(e), 500  # Return error as plain text


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)