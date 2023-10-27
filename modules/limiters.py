"""
    @Author: ImYrS Yang
    @Date: 2023/8/2
    @Copyright: @ImYrS
"""

from flask import request
from flask_limiter import Limiter

from modules.config import config
from modules.common import get_real_ip

redis = config['db'].get('redis')

if redis:
    limiter = Limiter(
        key_func=lambda: get_real_ip(request.headers),
        storage_uri=f'redis://{redis}',
        storage_options={'socket_connect_timeout': 30},
        strategy='fixed-window',
    )
else:
    limiter = Limiter(key_func=lambda: get_real_ip(request.headers))


def limits_to_chinese(text: str) -> str:
    """
    将限制提示翻译为中文

    :param text: 限制提示, 如: '1 per 1 second'
    """
    items = text.split(' ')
    if len(items) != 4:
        return text

    unit = items[3]
    if unit == 'second':
        unit = '秒'
    elif unit == 'minute':
        unit = '分钟'
    elif unit == 'hour':
        unit = '小时'
    elif unit == 'day':
        unit = '天'

    return f'每 {items[2]} {unit} {items[0]} 次'
