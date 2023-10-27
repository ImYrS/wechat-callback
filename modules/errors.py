"""
    @Author: ImYrS Yang
    @Date: 2023/2/14
    @Copyright: ImYrS Yang
    @Description: 
"""

from typing import Optional

from flask import request
from werkzeug.exceptions import BadRequest

ParameterError = (TypeError, KeyError, ValueError, AssertionError, BadRequest)


class Error:

    def __init__(
            self,
            code: Optional[int] = None,
            http_code: Optional[int] = 400,
            message: Optional[str] = None,
            message_human_readable: Optional[str] = None,
            data: Optional[dict] = None,
    ):
        """
        错误类

        :param code: 错误码
        :param http_code: HTTP 状态码
        :param message: 错误信息, 英文的广义描述
        :param message_human_readable: 错误信息, 中文可读的狭义描述
        :param data: 可返回的数据
        """
        self.code = code
        self.http_code = http_code or 400
        self.message = message
        self.message_human_readable = message_human_readable
        self.data = data or {
            'path': request.path,
            'method': request.method,
            'headers': dict(request.headers),
        }

        try:
            del self.data['headers']['Authorization']
        except KeyError:
            pass

    def create(self) -> tuple[dict, int]:
        """创建 HTTP 响应数据"""
        return {
            'code': self.code,
            'message': self.message,
            'message_human_readable': self.message_human_readable,
            'data': self.data,
        }, self.http_code

    def parameters_invalid(self, var: Optional[str] = None) -> 'Error':
        """请求参数缺失或不可用"""
        self.code = self.http_code = 400
        self.message = 'Parameters invalid'
        self.message_human_readable = '请求参数缺失或不可用'
        if var:
            self.message += f': {var}'
            self.message_human_readable += f': {var}'

        return self

    def db_error(self) -> 'Error':
        """数据库错误"""
        self.code = self.http_code = 500
        self.message = 'Database error'
        self.message_human_readable = '数据库错误'

        return self

    def permission_denied(self) -> 'Error':
        """权限不足"""
        self.code = self.http_code = 403
        self.message = 'Permission denied'
        self.message_human_readable = '权限不足'

        return self

    def not_found(self) -> 'Error':
        """未找到"""
        self.code = self.http_code = 404
        self.message = 'Object or resource not found'
        self.message_human_readable = '指定的对象或资源不存在'

        return self

    def internal_server_error(self) -> 'Error':
        """服务器内部错误"""
        self.code = self.http_code = 500
        self.message = 'Internal server error'
        self.message_human_readable = '服务器内部错误'

        return self

    def captcha_error(self) -> 'Error':
        """验证码错误"""
        self.code = self.http_code = 400
        self.message = 'Captcha error'
        self.message_human_readable = '请求验证失败, 请重试'

        return self


class ErrorCodes:
    pass
