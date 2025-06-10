from flask import Flask, render_template, request, redirect, session, send_from_directory
import socket
import os
import hashlib
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.hash_utils import calculate_sha256

app = Flask(__name__)
app.secret_key = 'your-secret-key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
users_db = {}  # simple in-memory user database

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users_db and users_db[username] == password:
            session['user'] = username
            return redirect('/upload')
        else:
            message = 'Invalid credentials'
    return render_template('login.html', message=message)

@app.route('/register', methods=['POST'])
def register():
    new_user = request.form['new_username']
    new_pass = request.form['new_password']
    if new_user in users_db:
        return render_template('login.html', message='Username already exists!')
    users_db[new_user] = new_pass
    return render_template('login.html', message='Account created successfully. You can now log in.')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user' not in session:
        return redirect('/login')

    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'upload':
            file = request.files['file']
            if not file:
                message = 'No file selected'
            else:
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)

                file_hash = calculate_sha256(filepath)

                # Send to server
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(('127.0.0.1', 9090))
                    s.sendall(file.filename.encode() + b'||' + file_hash.encode())
                    with open(filepath, 'rb') as f:
                        while chunk := f.read(1024):
                            s.sendall(chunk)

                message = f"File '{file.filename}' uploaded with SHA-256: {file_hash}"

        elif action == 'download':
            filename = request.form.get('filename')
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', 9091))  # listening on another port for receiving
                s.sendall(filename.encode())

                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    while True:
                        data = s.recv(1024)
                        if not data:
                            break
                        f.write(data)

            message = f"File '{filename}' received from server and saved."

    return render_template('upload.html', message=message)



    return '''
        <h2>Upload File</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file"><br><br>
            <input type="submit" value="Upload">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
