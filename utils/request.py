# -*- coding: utf-8 -*-
import asyncio
import http.cookies
from typing import *
import os
import aiohttp

# 不带这堆头部有时候也能成功请求，但是带上后成功的概率更高
BILIBILI_COMMON_HEADERS = {
    'Origin': 'https://www.bilibili.com',
    'Referer': 'https://www.bilibili.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/114.0.0.0 Safari/537.36'
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'
}

http_session: Optional[aiohttp.ClientSession] = None


# def init():
#     global http_session
#     http_session = aiohttp.ClientSession(
#         response_class=CustomClientResponse,
#         timeout=aiohttp.ClientTimeout(total=10),
#     )
def init(cookie_path: str):
    global http_session
    if cookie_path is not None and os.path.exists(cookie_path):
        with open(cookie_path, encoding='utf-8') as f:
            cookies = f.read()
            cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookies.split('; ')}
            c = http.cookies.SimpleCookie()
            c.update(cookies)
            # c['SESSDATA']['domain'] = 'bilibili.com'
            http_session = aiohttp.ClientSession(
                # cookies=c,
                response_class=CustomClientResponse,
                timeout=aiohttp.ClientTimeout(total=10)
            )
            http_session.cookie_jar.update_cookies(c)
    else:
        http_session = aiohttp.ClientSession(
            response_class=CustomClientResponse,
            timeout=aiohttp.ClientTimeout(total=10),
        )

async def shut_down():
    if http_session is not None:
        await http_session.close()


class CustomClientResponse(aiohttp.ClientResponse):
    # 因为aiohttp的BUG，当底层连接断开时，_wait_released可能会抛出CancelledError，导致上层协程结束。这里改个错误类型
    async def _wait_released(self):
        try:
            return await super()._wait_released()
        except asyncio.CancelledError as e:
            raise aiohttp.ClientConnectionError('Connection released') from e
