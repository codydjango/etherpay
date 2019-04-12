from flask import Flask, jsonify, request

app = Flask(__name__)

# @app.before_request
# def before_request(*args, **kwargs):
#     request.headers['Access-Control-Allow-Origin'] = '*'

@app.route('/')
def hello_world():
    response = jsonify({
        "status": "Hello, World!",
        "payload": {}
    })

    response.headers['Access-Control-Allow-Origin'] = '*'

    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='8000')
