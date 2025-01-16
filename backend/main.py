
# WEB
from flask import Flask, request, jsonify, session, Blueprint, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from crawling import SubPageData,SiteData,SiteDataArray,get_site_data
from flask_cors import CORS
import requests

# DB / TYPES
import sqlite3
from pydantic import BaseModel
import json
from database_functions import get_db, init_db

# HELPFUL
from typeguard import typechecked
from typing import List
from functional import seq
from dotenv import load_dotenv
import os

# OTHER FILES
from routes.authentication import auth
from routes.profile import profile_bp
# profile_bp = Blueprint('profile_bp', __name__)

load_dotenv()
AI_WEB_SERVICE_URL = os.getenv("AI_WEB_SERVICE_URL")
app = Flask(__name__)
app.register_blueprint(auth)
app.register_blueprint(profile_bp)

# pentru toate rutele cu /prajitura/ceva -> poate din uri u ala sa-l acceseze. musai rutele cu /prajitura
CORS(app, resources={r"/prajitura/*": {"origins": "http://localhost:5173"}})

def home():
    return render_template('index.html')    #nush daca mai trebe

@app.route('/prajitura', methods=['GET'])
def say_hi():
    return jsonify({"message": "HI!"}), 200

# REQ BODY: text/plain
@app.post('/prajitura/google_search_websites/<int:nr_results>')
def search_results(nr_results):
    """
    Takes text/plain as input. nr_results is how many websites the google API should return(max 10, min 1)
    Returns a List of Tuples(str,str).
    The result is of the form (sub_page_uri, site_uri) where sub_page_uri is among the results
    from searching the input string on the internet.
    Ex: (https://en.wikipedia.org/wiki/Sleep, https://en.wikipedia.org)
    """
    # data is byte arr
    user_query = request.get_data().decode()

    google_api_req_params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "q": user_query,
        "cx": os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
        "num": nr_results
    }

    response = requests.get('https://www.googleapis.com/customsearch/v1', params=google_api_req_params)
    uris = seq(response.json()['items']).map(lambda item : (item['link'],item['displayLink']))
    if response.status_code != 200:
        return jsonify({"msg:":"Error, Custom Search call failed"}),416  
    return jsonify(uris.to_list())

@app.post('/prajitura/crawl/<int:nr_total_crawled>')
def crawl_sub_page(nr_total_crawled):
    """
    Req body:
    {
        site_uri: str,
        sub_page_uri: str,
        query_keywords: List[str]
    }

    Response: List[SiteData]

    SiteData
    {
        sub_pages_data: List[SubPageData]
        site_uri: str,
    }

    SubPageData{
        text_lines: List[str]
        sub_page_uri: str
    }

    text_lines is paragraphs, h1-h6s of text from neighbouring websites starting from sub_page_uri.
    Only returns paragraphs,.. that contained 1 ore more keywords.
    Neighbouring means a link to them was present on a uri visited prior.
    Websites are traversed in a BFS manner.
    """

    req_body = request.get_json()
    site_uri = req_body['site_uri']
    sub_page_uri = req_body['sub_page_uri']
    query_keywords = req_body['query_keywords']
    res = get_site_data(sub_page_uri, site_uri, query_keywords,nr_total_crawled)
    json_res = '['
    for site_data in res:
        json_res += site_data.model_dump_json()
    json_res += ']'
    return json_res,200

# OBSOLETE ENDPOINT
# # REQ BODY: text/plain
# @app.post('/prajitura/search')
# def search():
#     # data is byte arr
#     user_id = session.get('user_id') #hehe
#     if not user_id:
#         return jsonify({"msg": "User not authenticated"}), 401

#     user_query = request.get_data().decode()
#     NUM_RESULTS = 5 # max 10 TODO: modifica, baga param

#     google_api_req_params = {
#         "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
#         "q": user_query,
#         "cx": os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
#         "num": NUM_RESULTS
#     }

#     response = requests.get('https://www.googleapis.com/customsearch/v1', params=google_api_req_params)
#     uris = seq(response.json()['items']).map(lambda item : (item['link'],item['displayLink']))
#     if response.status_code != 200:
#         return jsonify({"msg:":"Error, Custom Search call failed"}),416

#     # Extragem keyword-uri din ce cauta userul ca dupa sa putem filtra informatiile crawluite
#     user_query_keywords = [user_query]
    
#     try:
#         resp = requests.post(f"{AI_WEB_SERVICE_URL}/extract_search_keywords",
#                                             data=user_query,
#                                             headers={
#                                                 'Content-Type':'text/plain'
#                                                 })
#         if resp.status_code != 200:
#             print(f"Error at extracting keywords from user query:{resp} ")
#         else:
#             user_query_keywords += resp.json()
#     except Exception as e:
#         print(f"Error at extracting keywords from user query:{e} ")
    
#     print(user_query_keywords)

#     conn = sqlite3.connect('signup.db') #hehe
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO searches (user_id, search_text) VALUES (?, ?)", (user_id, user_query))  # <-- New line: Insert search query into DB
#     conn.commit()
#     conn.close()

#     site_data: List[SiteData] = []
#     for uri in uris:
#         site_data.append(get_site_data(uri[0],uri[1],user_query_keywords,3))

#     site_data_array = SiteDataArray(array=site_data)

#     response = requests.post(f"{AI_WEB_SERVICE_URL}/most_common_facts",data=site_data_array.model_dump_json(),headers={'Content-Type':'application/json'})
#     print(response.text)
#     if response.status_code != 200:
#         return jsonify({"msg:":"Error, AI web service call failed"}),416

#     return jsonify(response.json()),200

def get_blocked_sites():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"msg": "User not authenticated"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT site_url FROM blocked_sites WHERE user_id = ?", (user_id,))
    blocked_sites = cursor.fetchall()
    conn.close()

    return jsonify([{'site_url': site[0]} for site in blocked_sites])



# if __name__ == '__main__':
#     init_db()
#     app.run(debug=True, port=5000)
