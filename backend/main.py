from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/prajitura', methods=['GET'])
def say_hi():
    return jsonify({"message":"HI!"}),200

if __name__ == '__main__':
    app.run(debug=True, port=5000)