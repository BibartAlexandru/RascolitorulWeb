from flask import Blueprint, jsonify, session
import sqlite3

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
