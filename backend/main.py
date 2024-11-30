import json
from typing import List
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from pydantic import BaseModel
import requests
from functional import seq
from bs4 import BeautifulSoup
# pt env variables
from dotenv import load_dotenv
import os

from typeguard import typechecked
from urllib.parse import urljoin


app = Flask(__name__)
load_dotenv()
AI_WEB_SERVICE_URL = os.getenv("AI_WEB_SERVICE_URL")

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

# REQ BODY: text/plain
@app.route('/prajitura/search', methods =["POST"])
def search():
    # data is byte arr
    user_query = request.get_data().decode()
    NUM_RESULTS = 10

    google_api_req_params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "q": user_query,
        "cx": os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
        "num": NUM_RESULTS
    }

    response = requests.get('https://www.googleapis.com/customsearch/v1', params=google_api_req_params)
    uris = seq(response.json()['items']).map(lambda item : item['link'])
    if response.status_code != 200:
        return jsonify({"msg:":"Error, Custom Search call failed"}),416

    # Extragem keyword-uri din ce cauta userul ca dupa sa putem filtra informatiile crawluite
    user_query_keywords = [user_query]
    
    resp = requests.post(f"{AI_WEB_SERVICE_URL}/extract_search_keywords",
                                        data=user_query,
                                        headers={
                                            'Content-Type':'text/plain'
                                            })
    if resp.status_code != 200:
        print(f"Error at extracting keywords from user query:{resp} ")
    else:
        user_query_keywords += resp.json()
    
    # print(user_query_keywords)

    crawled_site_data = []
    for uri in uris:
        crawled_site_data += get_spread_crawl_data(uri,user_query_keywords,3)

    for data in crawled_site_data:
        print(f"\nsite {data.site_uri}")
        for line in data.data:
            print(line)

    # TODO FA ENDPOINTU PT AI
    # payload = {
    #     "crawled_site_info": crawled_site_data
    # }
    # response = requests.post("https://ai_web_service/most_common_facts",data=payload)
    # if response.status_code != 200:
    #     return jsonify({"msg:":"Error, AI web service call failed"}),416


    # TODO RETURENAZA REZULTATELE IN LOC DE ASTA
    if response.status_code == 200:
        return response.json(),200
    else:
        return jsonify({"msg:":"Error, Custom Search Call Failed"}),403
    
class SiteCrawledData(BaseModel):
    data: List[str]
    site_uri: str

@typechecked
def get_spread_crawl_data(site_uri: str, query_keywords: List[str], nr_uris_to_crawl: int = 10) -> List[SiteCrawledData]:
    @typechecked
    def get_relevant_text(site_uri: str) -> SiteCrawledData:
        res = requests.get(site_uri)
        if res.status_code != 200:
            raise Exception(f"Get request to {site_uri} returned status code {res.status_code}")
        parser = BeautifulSoup(res.content,'html.parser')
        elements = parser.find_all('p') + parser.find_all('h1') + \
                parser.find_all('h2') + parser.find_all('h3') +\
                parser.find_all('h4') + parser.find_all('h5') + parser.find_all('h6')
        relevant_text = [element.get_text() for element in elements if any(q in element.get_text().lower() for q in query_keywords)]
        return SiteCrawledData(data=relevant_text,site_uri=site_uri)
    
    @typechecked
    def get_relevant_links(site_uri: str) -> List[str]:
        res = requests.get(site_uri)
        if res.status_code != 200:
            raise Exception(f"Get request to {site_uri} returned status code {res.status_code}")
        parser = BeautifulSoup(res.content,'html.parser')
        # sa nu inceapa linku cu # ca atunci e doar un element de pe aceasi pagina
        # relevante is daca au in ele un keyword. eventual putem schimba asta
        links = [a['href'] for a in parser.find_all('a',href = True) if a['href'][0] != '#']

        # poate linku e /cart/product in loc de https://emag.ro/cart/product, urljoin lipeste urlu de baza cu ala relativ daca e relativ
        relevant_links = [urljoin(site_uri,l) for l in links if any(keyword in l for keyword in query_keywords)]
        return relevant_links

    data = []
    uris_crawled = set()
    uris_to_crawl = [site_uri]
    while nr_uris_to_crawl > 0 and len(uris_to_crawl) > 0:
        current_site = uris_to_crawl.pop(0)
        uris_crawled.add(current_site)
        nr_uris_to_crawl -= 1
        # print(f'Crawling {current_site}')
        try:
            data.append(get_relevant_text(current_site))
            relevant_links = get_relevant_links(current_site)
            for link in relevant_links:
                if link not in uris_crawled:
                    uris_to_crawl.append(link)
        except Exception as e:
            print(e)

    return data

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
