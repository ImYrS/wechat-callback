"""
    @Author: ImYrS Yang
    @Date: 2023/2/12
    @Copyright: ImYrS Yang
    @Description: 
"""

from flask import Blueprint, request, g

from modules import common
from modules.limiters import limits_to_chinese
from modules.errors import Error
from modules.address import bp as address_bp
from modules.callback import bp as callback_bp

bp = Blueprint('backend', __name__)


@bp.before_request
def before_request():
    ip = common.get_real_ip(request.headers)
    g.ip = ip


@bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def not_found(path):
    return Error(
        code=404,
        http_code=404,
        message='Path not found or method not allowed',
        message_human_readable='请求的路径不存在或方法不被允许',
    ).create()


@bp.errorhandler(429)
def ratelimit_handler(e):
    return Error(
        code=429,
        http_code=429,
        message='Too many requests: ' + str(e.description),
        message_human_readable='请求过于频繁, 请稍后再试. 速率限制:' + limits_to_chinese(e.description),
    ).create()


@bp.route('/<path:path>', methods=['OPTIONS'])
def options(path):
    return path, 200


bp.register_blueprint(address_bp, url_prefix='/addresses')
bp.register_blueprint(callback_bp, url_prefix='/callback')
