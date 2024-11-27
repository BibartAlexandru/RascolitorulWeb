from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from pydantic import BaseModel
app = Flask(__name__)

# app.secret_key = 'your_secret_key'
# pentru toate rutele cu /prajitura/ceva -> poate din uri u ala sa-l acceseze. musai rutele cu /prajitura
CORS(app, resources={r"/prajitura/*": {"origins": "http://localhost:5173"}})


def init_db():
    conn = sqlite3.connect('signup.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()


#o sa o implementez mai tarziu, content tre sa fie string
def upload(searched_url, content):
    pass

@app.route('/prajitura', methods=['GET'])
def say_hi():
    return jsonify({"message": "HI!"}), 200

class SignupModel(BaseModel):
    username: str
    email: str
    password: str

@app.route('/prajitura/signup', methods=['POST'])
def signup():

    try:
        # **ia key-value pairurile din dict si le paseaza ca key=val functiei SignupModel
        request_body = SignupModel(**request.get_json())
    except Exception as e:
        return jsonify(e),400
    
    #acum request body are garantat fieldurile
    username = request_body.username
    email = request_body.email
    password = request_body.password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    conn = sqlite3.connect('signup.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
    user = cursor.fetchone()

    if user:
        return jsonify({"msg": "Error. Username or Email already exists"}), 406

    cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, hashed_password))
    conn.commit()
    conn.close()

    return jsonify({"msg": "User registered successfully"}) ,200

class LoginModel(BaseModel):
    username:str
    password:str

@app.route('/prajitura/login', methods=['POST'])
def login():
    try:
        request_body = LoginModel(**request.get_json())
    except Exception as e:
        return jsonify(e),400

    username = request_body.username
    password = request_body.password

    conn = sqlite3.connect('signup.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user[3], password):
        return jsonify({"message": "Logged in successfully!"}), 200
    else:
        return jsonify({"message": "Invalid username or password!"}), 401

@app.route('/prajitura/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return jsonify({"message": "You have been logged out."}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
