from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload', methods = ['POST'])
def upload():
    return 'working...'

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response
app.after_request(add_cors_headers)

if __name__ == '__main__':
    app.run()