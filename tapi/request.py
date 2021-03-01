import json
from copy import deepcopy
from json import JSONDecodeError

import requests
import allure
from urllib.parse import urljoin
from typing import Text, Dict, Union, NoReturn, MutableMapping, IO
from config import BASE_URL, HEADERS


@allure.step('{1} {0}')
def request(url, method, headers, query, body) -> requests.Response:
    if not url.startswith('http'):
        url = urljoin(BASE_URL, url)
    current_headers = HEADERS
    if headers:
        current_headers = deepcopy(HEADERS)
        current_headers.update(headers)
    r = requests.request(method, url, headers=current_headers, params=query, json=body, verify=False)

    recode_headers(r.headers, f'响应头 {r.status_code}')
    try:
        allure.attach(json.dumps(r.json(), indent=4), '响应数据', allure.attachment_type.JSON)
    except JSONDecodeError:
        allure.attach(r.text, '响应数据', allure.attachment_type.TEXT)

    recode_headers(r.request.headers, '请求头', r.request.method, r.request.url)
    if r.request.body:
        allure.attach(json.dumps(json.loads(r.request.body), indent=4), '请求体', allure.attachment_type.JSON)
    else:
        allure.attach('', '请求体为空', allure.attachment_type.TEXT)

    return r


def recode_headers(headers: MutableMapping, name: Text, method: Text = '', url: Text = '') -> NoReturn:
    headers_list = []
    for k, v in headers.items():
        headers_list.append(f'{k}: {v}')
    headers_text = '\n'.join(headers_list)
    if method and url:
        headers_text = f'{method.upper()} {url}\n{headers_text}'
    allure.attach(headers_text, name, allure.attachment_type.TEXT)
