
import sqlite3
from flask import app, jsonify, request, session, Blueprint
from pydantic import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

class SignupModel(BaseModel):
    username: str
    email: str
    password: str

@auth.route('/prajitura/signup', methods=['POST'])
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

@auth.route('/prajitura/login', methods=['POST'])
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

@auth.route('/prajitura/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return jsonify({"message": "You have been logged out."}), 200