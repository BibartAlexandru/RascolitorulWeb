from flask import Blueprint, jsonify, request, session
import sqlite3

from database_functions import get_db

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/prajitura/profile/search-history', methods=['GET'])
def get_search_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"msg": "User not authenticated"}), 401

    conn = sqlite3.connect('signup.db')
    cursor = conn.cursor()
    cursor.execute("SELECT search_text, timestamp FROM searches WHERE user_id = ?", (user_id,))
    search_history = cursor.fetchall()
    conn.close()

    return jsonify(search_history), 200

@profile_bp.route('/profile/block-site', methods=['POST'])
def block_site():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"msg": "User not authenticated"}), 401

    site_url = request.json.get('site_url')
    if not site_url:
        return jsonify({"msg": "No site URL provided"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO blocked_sites (user_id, site_url) VALUES (?, ?)", (user_id, site_url))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Site blocked successfully"}), 201

@profile_bp.route('/prajitura/profile', methods=['GET'])
def profile():

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"msg": "User not authenticated"}), 401

    conn = sqlite3.connect('signup.db')
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    cursor.execute("SELECT search_text, timestamp FROM searches WHERE user_id = ?", (user_id,))
    searches = cursor.fetchall()

    conn.close()

    return jsonify({"msg":"Ok"}),200