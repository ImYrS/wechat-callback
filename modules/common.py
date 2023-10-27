"""
    @Author: ImYrS Yang
    @Date: 2023/10/27
    @Copyright: ImYrS
    @Description: 
"""

import re
import time
from typing import Optional, Iterable, Any


def formatted_time(
        time_stamp: Optional[int] = int(time.time()),
        secure_format: Optional[bool] = False,
) -> str:
    """
    时间戳转换为格式化时间

    :param time_stamp: 需要格式化的 Unix 时间戳
    :param secure_format: 是否需要安全的字符格式
    :return: 格式化后的时间
    """
    return (
        time.strftime("%Y%m%d_%H%M%S", time.localtime(time_stamp))
        if secure_format
        else time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamp))
    )


def timestamp(ms: Optional[bool] = True) -> int:
    """
    获取当前时间戳

    :param ms: 是否以毫秒为单位
    :return: 时间戳
    """
    return int(time.time()) if not ms else int(time.time() * 1000)


def now() -> int:
    """获取毫秒单位时间戳的别名"""
    return timestamp()


def str_process(var):
    """字符串处理, 支持列表和字典"""
    if type(var) in [int, float, bool, None]:
        return var
    elif type(var) is str:
        return clean_str(var)
    elif type(var) in [list, tuple]:
        return [str_process(i) for i in var]
    elif type(var) is dict:
        return {str_process(k): str_process(v) for k, v in var.items()}
    else:
        return var


def clean_str(text: str) -> str:
    """去除异常字符"""
    text = eval(re.sub(r"\\u.{4}", "", repr(text)))  # 去除 unicode 编码
    text = eval(re.sub(r"\\x.{2}", "", repr(text)))  # 去除 hex 编码
    text = eval(re.sub(r"\\", "", repr(text)))  # 去除转义字符
    text = eval(re.sub(r"\"", "", repr(text)))  # 去除双引号
    text = eval(re.sub(r"\n", "", repr(text)))  # 去除换行符
    text = eval(re.sub(r"\r", "", repr(text)))  # 去除回车符
    text = eval(re.sub(r"\t", "", repr(text)))  # 去除制表符
    text = eval(re.sub(r"\s", "", repr(text)))  # 去除空格

    # 全角转半角
    new_string = ""
    for char in text:
        inside_code = ord(char)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xFEE0

        # 不是半角字符返回原来的字符
        new_string += (
            char if inside_code < 0x0020 or inside_code > 0x7E else chr(inside_code)
        )

    return new_string


def get_real_ip(headers: Iterable[Any]) -> str:
    """
    在使用了反向代理或 CDN 等情况下, 获取请求真实 IP

    :param headers: 可迭代的请求头
    :return: IP 或 127.0.0.1
    """
    probable_headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Forwarded',
        'Forwarded-For',
        'Forwarded',
        'True-Client-IP',
        'Client-IP',
        'Ali-CDN-Real-Ip',
        'Cdn-Src-Ip',
        'Cdn-Real-Ip',
        'Cf-Connecting-Ip',
        'X-Cluster-Client-Ip',
        'Wl-Proxy-Client-Ip',
        'Proxy-Client-IP',
        'True-Client-Ip',
    ]

    existed_headers = {}
    for k, v in headers:
        existed_headers[k.upper()] = v

    for header in probable_headers:
        if header.upper() in existed_headers:
            ip = existed_headers[header.upper()]

            # 可能存在多个 IP, 取第一个
            return (
                ip
                if ',' not in ip
                else ip.split(',')[0]
            )

    return '127.0.0.1'
