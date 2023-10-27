"""
    @Author: ImYrS Yang
    @Date: 2023/4/20
    @Copyright: @ImYrS
"""

from functools import wraps
from typing import Optional
import logging

from flask import request, g
import requests

from modules.config import config
from modules.errors import Error


def captcha_required() -> callable:
    """
    验证码校验装饰器

    :return:
    """

    def decorated(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            captcha = request.headers.get('X-Captcha-Token')
            if not verify_captcha(captcha, g.ip):
                return Error().captcha_error().create()

            return func(*args, **kwargs)

        return wrapper

    return decorated


def verify_captcha(token: str, ip: Optional[str] = None) -> bool:
    """
    验证 Cloudflare turnstile v0

    :param token: token
    :param ip: ip
    :return: bool
    """
    secret = config['captcha']['secret']
    if not secret:
        return True

    if not token:
        return False

    payload = {
        'secret': secret,
        'response': token,
    }
    if ip:
        payload['remoteip'] = ip

    try:
        r = requests.post(
            url='https://challenges.cloudflare.com/turnstile/v0/siteverify',
            json=payload,
            timeout=5,
        ).json()
    except Exception as e:
        logging.error(f'Cloudflare captcha error: {e}')
        return False

    return r.get('success', False)
