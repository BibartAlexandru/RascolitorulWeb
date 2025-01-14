
# WEB
from flask import Flask, request, jsonify, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import requests

# DB / TYPES
import sqlite3
from pydantic import BaseModel
import json

# HELPFUL
from typeguard import typechecked
from typing import List
from functional import seq
from dotenv import load_dotenv
import os

# OTHER FILES
from crawling import SubPageData,SiteData,SiteDataArray,get_site_data
from routes.authentication import auth

load_dotenv()
AI_WEB_SERVICE_URL = os.getenv("AI_WEB_SERVICE_URL")
app = Flask(__name__)
app.register_blueprint(auth)

# pentru toate rutele cu /prajitura/ceva -> poate din uri u ala sa-l acceseze. musai rutele cu /prajitura
CORS(app, resources={r"/prajitura/*": {"origins": "http://localhost:5173"}})

@app.route('/prajitura', methods=['GET'])
def say_hi():
    return jsonify({"message": "HI!"}), 200

# REQ BODY: text/plain
@app.post('/prajitura/google_search_websites')
def search_results():
    """
    Takes text/plain as input.
    Returns a List of Tuples(str,str).
    The result is of the form (sub_page_uri, site_uri) where sub_page_uri is among the results
    from searching the input string on the internet.
    Ex: (https://en.wikipedia.org/wiki/Sleep, https://en.wikipedia.org)
    """
    # data is byte arr
    user_query = request.get_data().decode()
    NUM_RESULTS = 5 # TODO: CHANGE

    google_api_req_params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "q": user_query,
        "cx": os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
        "num": NUM_RESULTS
    }

    response = requests.get('https://www.googleapis.com/customsearch/v1', params=google_api_req_params)
    uris = seq(response.json()['items']).map(lambda item : (item['link'],item['displayLink']))
    if response.status_code != 200:
        return jsonify({"msg:":"Error, Custom Search call failed"}),416  
    return jsonify(uris.to_list())

@app.post('/prajitura/crawl')
def crawl_sub_page():
    """
    Req body:
    {
        site_uri: str,
        sub_page_uri: str,
        query_keywords: List[str]
    }

    Response: 
    {
        sub_pages_data: List[SubPageData]
        site_uri: str,
    }
    where:
        SubPageData{
            text_lines: List[str]
            sub_page_uri: str
        }

    Returns paragraphs, h1-h6s of text from 10 neighbouring websites starting from sub_page_uri.
    Only returns paragraphs,.. that contained 1 ore more keywords.
    Neighbouring means a link to them was present on a uri visited prior.
    Websites are traversed in a BFS manner.
    """

    req_body = request.get_json()
    site_uri = req_body['site_uri']
    sub_page_uri = req_body['sub_page_uri']
    query_keywords = req_body['query_keywords']
    res = get_site_data(sub_page_uri, site_uri, query_keywords,1)
    return res.model_dump_json(),200

# REQ BODY: text/plain
@app.post('/prajitura/search')
def search():
    # data is byte arr
    user_query = request.get_data().decode()
    NUM_RESULTS = 5 # max 10 TODO: modifica, baga param

    google_api_req_params = {
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "q": user_query,
        "cx": os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
        "num": NUM_RESULTS
    }

    response = requests.get('https://www.googleapis.com/customsearch/v1', params=google_api_req_params)
    uris = seq(response.json()['items']).map(lambda item : (item['link'],item['displayLink']))
    if response.status_code != 200:
        return jsonify({"msg:":"Error, Custom Search call failed"}),416

    # Extragem keyword-uri din ce cauta userul ca dupa sa putem filtra informatiile crawluite
    user_query_keywords = [user_query]
    
    try:
        resp = requests.post(f"{AI_WEB_SERVICE_URL}/extract_search_keywords",
                                            data=user_query,
                                            headers={
                                                'Content-Type':'text/plain'
                                                })
        if resp.status_code != 200:
            print(f"Error at extracting keywords from user query:{resp} ")
        else:
            user_query_keywords += resp.json()
    except Exception as e:
        print(f"Error at extracting keywords from user query:{e} ")
    
    print(user_query_keywords)
    site_data: List[SiteData] = []
    for uri in uris:
        site_data.append(get_site_data(uri[0],uri[1],user_query_keywords,3))

    site_data_array = SiteDataArray(array=site_data)

    response = requests.post(f"{AI_WEB_SERVICE_URL}/most_common_facts",data=site_data_array.model_dump_json(),headers={'Content-Type':'application/json'})
    print(response.text)
    if response.status_code != 200:
        return jsonify({"msg:":"Error, AI web service call failed"}),416

    return jsonify(response.json()),200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
