"""
    @Author: ImYrS Yang
    @Date: 2023/10/27
    @Copyright: ImYrS
    @Description: 
"""

import logging
import os
from typing import Optional

from flask import Flask, render_template

from modules.config import config
from modules import common, database
from modules.limiters import limiter
from routers.backend import bp as backend_bp

os.environ['NO_PROXY'] = '*'

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.register_blueprint(backend_bp, url_prefix='/api')

limiter.init_app(app)

debug_mode = config['dev'].as_bool('debug')
version = config['meta']['version']
commit = ''


def init_logger(debug: Optional[bool] = False):
    """初始化日志系统"""
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log_format = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if debug else logging.WARNING)
    ch.setFormatter(log_format)
    log.addHandler(ch)

    if not os.path.exists('./logs/'):
        os.mkdir(os.getcwd() + '/logs/')

    log_name = f'./logs/{common.formatted_time(secure_format=True)}.log'
    fh = logging.FileHandler(log_name, mode='a', encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(log_format)
    log.addHandler(fh)


def get_commit() -> Optional[str]:
    """获取当前 commit"""
    if not os.path.exists('.git'):
        return None

    try:
        with open('.git/refs/heads/main', 'r') as f:
            return f.read().strip()[0:7]
    except FileNotFoundError:
        pass

    return None


def init():
    """初始化"""
    init_logger(debug_mode)
    database.init_db()

    global commit
    commit = get_commit()


init()


@app.after_request
def after_request(response):
    """请求后执行"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    response.headers.add('Access-Control-Max-Age', '3600')
    response.headers.add('Access-Control-Allow-Headers', '*')

    return response


@app.teardown_request
def teardown_request(exception):
    """请求结束后执行"""
    if exception:
        logging.error(f'[Teardown] {exception}')


@app.route('/', methods=['GET'])
def index():
    """
    主页
    :return:
    """
    return render_template(
        'index.html',
        version=version,
        commit=commit,
        captcha_key=config['captcha']['key'],
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=debug_mode)
