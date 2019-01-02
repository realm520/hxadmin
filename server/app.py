from flask import Flask
from libs.scheduler import scheduler
from flask_cors import *
from flask_jsonrpc import JSONRPC
from hx_util import get_account_balances, get_account_info, get_asset_info



def job_1():
    get_asset_info()
    get_account_info()

class Config(object):
    JOBS = [
        {
            'id': 'job2',
            'func': job_1,
            'trigger': 'interval',
            'seconds': 5,
        }
    ]

app = Flask(__name__)
app.config.from_object(Config())
CORS(app, supports_credentials=True)
jsonrpc = JSONRPC(app, '/api')

@jsonrpc.method('hx.asset.summary')
def index():
    return u'Welcome to Flask JSON-RPC'


if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()

    app.run(host='0.0.0.0', debug=True) #use_reloader=False, prevent scheduler run twice
