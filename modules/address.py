import logging
from uuid import uuid4

from flask import request, Blueprint
import peewee

from modules.decorator import captcha_required
from modules.config import config
from modules import common
from modules.limiters import limiter
from modules.database import Address
from modules.types import AddressState
from modules.errors import ParameterError, Error

bp = Blueprint('address', __name__)


def address_to_dict(address: Address) -> dict:
    """
    将 Address 对象转换为 dict

    :param address:
    :return:
    """
    return {
        'id': address.uuid,
        'url': address.url,
        'state': address.state,
        'created_at': address.created_at,
        'expired_at': address.expired_at,
    }


@bp.route('', methods=['POST'])
@captcha_required()
@limiter.limit('10/minute; 30/hour; 50/3hour; 200/day')
def create() -> tuple[dict, int]:
    """
    创建回调地址

    :return:
    """
    try:
        aes_key = request.json['aes_key'].strip()
        if not aes_key:
            raise ValueError('aes_key')
    except ParameterError as e:
        return Error().parameters_invalid(e).create()

    uuid = uuid4()

    try:
        address = Address.create(
            uuid=uuid4(),
            url=f'{config["core"]["proto"]}://{uuid}.{config["core"]["domain"]}/api/callback',
            aes_key=aes_key,
            state=AddressState.Active,
            created_at=common.now(),
            expired_at=common.now() + 15 * 60 * 1000,  # 15 分钟后过期
        )
    except peewee.PeeweeException as e:
        logging.error(f'创建回调地址失败: {e}')
        return Error().db_error().create()

    return {'code': 200, 'data': address_to_dict(address)}, 200


@bp.route('/<uuid:address_id>', methods=['GET'])
def get(address_id: str) -> tuple[dict, int]:
    """
    获取回调地址信息

    :param address_id:
    :return:
    """
    try:
        address = Address.get(
            Address.uuid == address_id,
            Address.created_at >= common.now() - 24 * 60 * 60 * 1000,  # 24 小时内创建的地址
        )
    except peewee.DoesNotExist:
        return Error().not_found().create()

    return {'code': 200, 'data': address_to_dict(address)}, 200
