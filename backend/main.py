from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/prajitura', methods=['GET'])
def say_hi():
    return jsonify({"message":"HI!"}),200

@app.route('/prajitura/index')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)