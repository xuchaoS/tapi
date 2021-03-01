import json
import os
import pprint

import furl

from pandas import DataFrame
from .parse import (COL_LEVEL,
                    COL_RUN,
                    COL_CASE_NAME,
                    COL_TAGS,
                    COL_BODY,
                    COL_HEADERS,
                    COL_URL,
                    COL_EXPECT,
                    COL_METHOD,
                    COL_POST_VARIABLE,
                    COL_QUERY,
                    COL_PRE_VARIABLE, parse_har)


def har2xlsx(filename):
    records = []
    for i, call in enumerate(parse_har(filename)):
        record = {
            COL_CASE_NAME: f'测试用例_{i + 1}',
            COL_RUN: 'Y',
            COL_LEVEL: 'normal',
            COL_TAGS: '自动生成',
            COL_URL: call.request.url,
            COL_METHOD: call.request.method.value,
            COL_PRE_VARIABLE: '',
            COL_HEADERS: call.request.headers,
            COL_QUERY: pprint.pformat(call.request.query) if call.request.query else '',
            COL_BODY: pprint.pformat(call.request.body) if call.request.body else call.request.body,
            COL_EXPECT: [f'r.status_code == {call.response.status_code}']
        }
        r = call.response.body
        if isinstance(r, dict):
            for k, v in r.items():
                if isinstance(v, bool):
                    record[COL_EXPECT].append(f'r.json()["{k}"] is {repr(v)}')
                elif isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
                    record[COL_EXPECT].append(f'r.json()["{k}"] == {repr(v)}')
                elif isinstance(v, list):
                    record[COL_EXPECT].append(f'isinstance(r.json()["{k}"], list)')
                    record[COL_EXPECT].append(f'len(r.json()["{k}"]) == {len(v)}')
                elif isinstance(v, dict):
                    record[COL_EXPECT].append(f'isinstance(r.json()["{k}"], dict)')
                    record[COL_EXPECT].append(f'len(r.json()["{k}"]) == {len(v)}')
                elif v is None:
                    record[COL_EXPECT].append(f'r.json()["{k}"] is None')
        elif isinstance(r, list):
            record[COL_EXPECT].append(f'isinstance(r.json(), list)')
            record[COL_EXPECT].append(f'len(r.json()) == {len(r)}')
        elif isinstance(r, str):
            record[COL_EXPECT].append(f'r.text == {repr(r)}')

        record[COL_EXPECT] = '\n'.join(record[COL_EXPECT])
        record[COL_POST_VARIABLE] = ''
        records.append(record)
    base_url = records[0][COL_URL]
    global_headers = records[0][COL_HEADERS].copy()
    for record in records:
        while not record[COL_URL].startswith(base_url):
            base_url = base_url[:base_url.rindex('/')]
        for k, v in global_headers.copy().items():
            if k not in record[COL_HEADERS] or record[COL_HEADERS][k] != v:
                global_headers.pop(k)
    with open('config_自动生成.py', 'w') as f:
        f.write(f"BASE_URL = '{base_url}'\n")
        f.write('HEADERS = {\n')
        for k, v in global_headers.items():
            f.write(f"    '{k}': '{v}',\n")
        f.write('}\n')
    base_url_len = len(base_url)
    for record in records:
        if base_url_len > 10:
            record[COL_URL] = record[COL_URL][base_url_len:]
        for k in global_headers:
            record[COL_HEADERS].pop(k)
        record[COL_HEADERS] = pprint.pformat(record[COL_HEADERS]) if record[COL_HEADERS] else ''

    df = DataFrame(records)
    df.to_excel(f'test_自动生成_{os.path.basename(filename)[:-4]}.xlsx',
                columns=[COL_CASE_NAME, COL_RUN, COL_LEVEL, COL_TAGS, COL_PRE_VARIABLE, COL_URL, COL_METHOD,
                         COL_HEADERS, COL_QUERY, COL_BODY, COL_EXPECT, COL_POST_VARIABLE])


def har2api(filename):
    with open(filename, "rb") as f:
        data = json.load(f)
    apis = {}
    for i, interface in enumerate(data['log']['entries']):
        url = furl.furl(interface['request']['url'])
        url.set(query=None)
        url = url.url
        method = interface['request']['method']
        headers = {header['name']: header['value'] for header in interface['request']['headers'] if
                   header['name'] not in ('Host', 'Connection', 'Content-Length')}
        query = {query['name']: query['value'] for query in interface["request"]["queryString"]} if \
            interface["request"]["queryString"] else {}
        body = interface['request']['postData']['text']
        body = json.loads(body) if body else body
        if url not in apis:
            apis[url] = {'method': method, 'headers': headers, 'data': [{'query': query, 'body': body}]}
        else:
            apis[url]['data'].append({'query': query, 'body': body})
    with open('apis.json', 'w') as f:
        json.dump(apis, f, indent=4)
