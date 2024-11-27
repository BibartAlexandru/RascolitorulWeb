from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
app = Flask(__name__)
app.secret_key = 'your_secret_key'
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


# @app.route('/prajitura/index', methods=['GET'])
# def index():
#     return render_template('index.html')


@app.route('/prajitura/signup', methods=['POST'])
def signup():
    print(request.get_json())
    request_body = request.get_json()
    username = request_body['username']
    email = request_body['email']
    password = request_body['password']
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

    return jsonify({"msg": "Nice pass"}) ,200

@app.route('/prajitura/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('signup.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')

@app.route('/prajitura/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
