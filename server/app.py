from flask import Flask
from flask_cors import *
from flask_jsonrpc import JSONRPC

app = Flask(__name__)
CORS(app, supports_credentials=True)
jsonrpc = JSONRPC(app, '/api')


@jsonrpc.method('App.index')
def index():
    return u'Welcome to Flask JSON-RPC'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
