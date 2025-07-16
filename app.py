from flask import Flask, render_template, request, jsonify
import os
import re
from werkzeug.utils import secure_filename
from io import BytesIO

# For PDF parsing
import PyPDF2

# For DOCX parsing
import docx

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.config['UPLOAD_EXTENSIONS'] = ['.pdf', '.doc', '.docx']
app.config['UPLOAD_PATH'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.makedirs(app.config['UPLOAD_PATH'])

def extract_text_from_pdf(file_stream):
    reader = PyPDF2.PdfReader(file_stream)
    text = ''
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            # Clean up text: strip leading/trailing spaces, replace multiple newlines with single newline
            cleaned_text = re.sub(r'\n+', '\n', page_text.strip())
            text += cleaned_text + '\n'
    # Further clean up: remove excessive blank lines
    text = re.sub(r'(\n\s*){2,}', '\n\n', text)
    return text

def extract_text_from_docx(file_stream):
    doc = docx.Document(file_stream)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

def extract_text_from_doc(file_stream):
    # For .doc files, fallback to docx parser might not work.
    # Here, we just return empty or a message.
    return "Parsing .doc files is not supported in this demo."

def extract_contact_info(text):
    # Improved regex patterns for email and phone
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    # More precise phone number regex pattern
    phone_pattern = r'(\+?\d{1,3}[\s.-]?)?(\(?\d{3}\)?[\s.-]?)?[\d\s.-]{7,10}'

    emails = re.findall(email_pattern, text)
    phones_raw = re.findall(phone_pattern, text)

    # phones_raw is list of tuples due to groups, join groups to form full number
    phones = []
    for groups in phones_raw:
        phone = ''.join(groups)
        # Remove spaces, dots, dashes, parentheses for normalization
        phone_clean = re.sub(r'[\s\.\-\(\)]', '', phone)
        # Filter out too short or too long numbers
        if 7 <= len(phone_clean) <= 15:
            phones.append(phone_clean)

    return {
        'emails': list(set(emails)),
        'phones': list(set(phones))
    }

def extract_name(text):
    # Heuristic: Assume the name is in the first non-empty line and contains alphabets
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:5]:  # check first 5 lines for a name
        if re.match(r'^[A-Za-z ,.\'-]+$', line):
            return line
    return "Name not found"

def extract_sections(text):
    # Define possible section headings for each category
    sections = {
        'education': ['Education', 'Education and Training', 'Academic Background'],
        'experience': ['Experience', 'Work Experience', 'Professional Experience', 'Employment History'],
        'skills': ['Skills', 'Technical Skills', 'Skills & Abilities', 'Core Competencies']
    }

    extracted = {}

    for key, headings in sections.items():
        pattern = re.compile(
            r'(' + '|'.join([re.escape(h) for h in headings]) + r')\s*\n(.*?)(?=\n[A-Z][a-zA-Z &]+?\n|$)',
            re.DOTALL | re.IGNORECASE
        )
        match = pattern.search(text)
        if match:
            content = match.group(2).strip()
            content = re.sub(r'\n{2,}', '\n', content)
            extracted[key] = content
        else:
            extracted[key] = f"{key.capitalize()} details not found"

    return extracted

def extract_education(text):
    return extract_sections(text).get('education', 'Education details not found')

def extract_experience(text):
    return extract_sections(text).get('experience', 'Experience details not found')

def extract_skills(text):
    return extract_sections(text).get('skills', 'Skills details not found')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_resume():
    uploaded_file = request.files.get('pdf_doc')
    if not uploaded_file:
        return jsonify({'error': 'No file uploaded'}), 400

    filename = secure_filename(uploaded_file.filename)
    if filename == '':
        return jsonify({'error': 'Invalid file name'}), 400

    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
        return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

    file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
    uploaded_file.save(file_path)

    text = ''
    try:
        with open(file_path, 'rb') as f:
            if file_ext == '.pdf':
                text = extract_text_from_pdf(f)
            elif file_ext == '.docx':
                text = extract_text_from_docx(f)
            elif file_ext == '.doc':
                text = extract_text_from_doc(f)
    except Exception as e:
        return jsonify({'error': f'Failed to parse file: {str(e)}'}), 500

    contact_info = extract_contact_info(text)

    # Prepare data for rendering result page
    result = {
        'filename': filename,
        'text_length': len(text),
        'name': extract_name(text),
        'contact_info': contact_info,
        'education': extract_education(text),
        'experience': extract_experience(text),
        'skills': extract_skills(text)
    }

    return render_template('result.html', parsed_data=result)

if __name__ == '__main__':
    app.run(debug=True)
