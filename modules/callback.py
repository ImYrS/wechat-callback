import logging
import re
import base64

from flask import request, Blueprint
import peewee
from Crypto.Cipher import AES

from modules.config import config
from modules import common
from modules.database import Address
from modules.types import AddressState
from modules.errors import ParameterError, Error

bp = Blueprint('callback', __name__)


@bp.route('', methods=['GET'])
def callback():
    """微信 URL 回调验证"""
    try:
        sign = request.args['msg_signature']
        timestamp = request.args['timestamp']
        nonce = request.args['nonce']
        echo_str = request.args['echostr']

        host = request.headers.get('Host', '')
        uuid = re.match(r'(.*)\.' + config['core']['domain'], host).group(1)
        if not uuid:
            raise ValueError('host')
    except ParameterError as e:
        return Error().parameters_invalid(e).create()

    try:
        address = (
            Address.select()
            .where(
                Address.state == AddressState.Active,
                Address.uuid == uuid,
                Address.expired_at > common.now(),
            )
            .get()
        )
    except peewee.DoesNotExist:
        return Error().permission_denied().create()

    try:
        decrypted = decrypt_msg(echo_str, address.aes_key)
    except Exception as e:
        logging.error(f'解密回调地址失败: {e}')
        return Error().internal_server_error().create()

    address.state = AddressState.Finished
    address.save()

    return decrypted, 200


def decrypt_msg(msg: str, aes_key: str) -> str:
    """
    解密微信消息

    :param msg:
    :param aes_key:
    :return:
    """
    aes_key = base64.b64decode(aes_key + '=')
    cipher = AES.new(aes_key, AES.MODE_CBC, aes_key[0:16])
    decrypted = cipher.decrypt(base64.b64decode(msg + '='))
    msg_len = int.from_bytes(decrypted[16:20], byteorder='big')
    decrypted = decrypted[20:20 + msg_len].decode('utf-8')

    return decrypted
