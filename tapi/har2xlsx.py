import json
import os
from json import JSONDecodeError

import autopep8
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
                    COL_PRE_VARIABLE)


def har2xlsx(filename):
    with open(filename, "rb") as f:
        data = json.load(f)
    records = []
    for i, interface in enumerate(data['log']['entries']):
        record = {COL_CASE_NAME: f'测试用例_{i + 1}', COL_RUN: 'Y', COL_LEVEL: 'normal', COL_TAGS: '自动生成'}
        url = furl.furl(interface['request']['url'])
        url.set(query=None)
        record[COL_URL] = url.url
        record[COL_METHOD] = interface['request']['method']
        record[COL_PRE_VARIABLE] = ''
        record[COL_HEADERS] = {header['name']: header['value'] for header in interface['request']['headers'] if
                               header['name'] not in ('Host', 'Connection', 'Content-Length')}
        record[COL_QUERY] = json.dumps({query['name']: query['value'] for query in interface["request"]["queryString"]},
                                       indent=4) if interface["request"]["queryString"] else ''
        body = interface['request']['postData']['text']
        record[COL_BODY] = json.dumps(json.loads(body), indent=4) if body else body
        record[COL_EXPECT] = [f'r.status_code == {interface["response"]["status"]}']
        try:
            r = json.loads(interface["response"]['content']['text'])
        except JSONDecodeError:
            pass
        else:
            if isinstance(r, dict):
                for k, v in r.items():
                    if isinstance(v, bool):
                        record[COL_EXPECT].append(f'r.json()["{k}"] is {repr(v)}')
                    elif isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
                        # if 'date' in k.lower() or 'time' in k.lower():
                        #     continue
                        record[COL_EXPECT].append(f'r.json()["{k}"] == {repr(v)}')
                    elif isinstance(v, list):
                        record[COL_EXPECT].append(f'isinstance(r.json()["{k}"], list)')
                        record[COL_EXPECT].append(f'len(r.json()["{k}"]) == {len(v)}')
                    elif isinstance(v, dict):
                        record[COL_EXPECT].append(f'isinstance(r.json()["{k}"], dict)')
                        record[COL_EXPECT].append(f'len(r.json()["{k}"]) == {len(v)}')
            elif isinstance(r, list):
                record[COL_EXPECT].append(f'isinstance(r.json(), list)')
                record[COL_EXPECT].append(f'len(r.json()) == {len(r)}')

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
    # print(base_url)
    # print(len(global_headers), global_headers)
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
        record[COL_HEADERS] = json.dumps(record[COL_HEADERS], indent=4)

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
    # import pprint
    # pprint.pprint(apis)
    with open('apis.json', 'w') as f:
        json.dump(apis, f, indent=4)
