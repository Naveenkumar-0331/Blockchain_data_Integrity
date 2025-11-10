from flask import Flask, render_template, request, redirect, url_for, Response
from blockchain import Blockchain, hash_student_record
import os
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
edu_chain = Blockchain()
edu_chain.load_chain()

# Folder to store uploaded certificates
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allow only specific file types
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if file has a valid extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_record():
    name = request.form['name']
    roll = request.form['roll']
    gpa = request.form['gpa']
    record_hash = hash_student_record(name, roll, gpa)
    edu_chain.add_block(record_hash)
    edu_chain.save_chain()
    return redirect(url_for('view_chain'))

@app.route('/view')
def view_chain():
    chain_data = []
    for block in edu_chain.chain:
        chain_data.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'data': block.data,
            'prev_hash': block.previous_hash,
            'hash': block.hash
        })
    return render_template('view.html', chain=chain_data)

@app.route('/verify', methods=['GET', 'POST'])
def verify_record():
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        gpa = request.form['gpa']
        verified = edu_chain.verify_student_record(name, roll, gpa)
        return render_template('verify.html', verified=verified)
    return render_template('verify.html', verified=None)

# --------------------------
# 📎 CERTIFICATE UPLOAD FEATURE
# --------------------------

@app.route('/upload', methods=['GET', 'POST'])
def upload_certificate():
    if request.method == 'POST':
        # Optional admin password check (can remove if not needed)
        key = request.form.get('key')
        correct_key_hash = hashlib.sha256(b"admin123").hexdigest()
        if hashlib.sha256(key.encode()).hexdigest() != correct_key_hash:
            return "Unauthorized Access", 403

        # Check file validity
        if 'file' not in request.files:
            return "No file uploaded", 400
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Generate SHA-256 hash for the file
            with open(filepath, 'rb') as f:
                file_bytes = f.read()
                file_hash = hashlib.sha256(file_bytes).hexdigest()

            # Add this hash to the blockchain
            edu_chain.add_block(f"Certificate Hash: {file_hash}")
            edu_chain.save_chain()

            return render_template('upload.html', uploaded=True, file_hash=file_hash)

    # GET request → load upload page
    return render_template('upload.html', uploaded=False)
@app.route('/verify_certificate', methods=['GET', 'POST'])
def verify_certificate():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded", 400
        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400

        # Save temporarily for hashing
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Compute hash of uploaded file
        with open(filepath, 'rb') as f:
            file_bytes = f.read()
            uploaded_hash = hashlib.sha256(file_bytes).hexdigest()

        # Check if hash exists in blockchain
        found = False
        for block in edu_chain.chain:
            if uploaded_hash in block.data:
                found = True
                break

        return render_template('verify_certificate.html', checked=True, found=found, uploaded_hash=uploaded_hash)

    # GET request (when user opens the page)
    return render_template('verify_certificate.html', checked=False)

@app.route('/sha_steps')
def sha_steps():
    return render_template('sha_steps.html')


if __name__ == '__main__':
    app.run(debug=True)
