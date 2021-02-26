import os
from typing import List, Union

from pandas import read_excel, ExcelFile
from numpy import isnan
import json
from loguru import logger
from .models import TSuite, TCase, TStep, TRequest, THook

COL_CASE_NAME = '用例名称'
COL_RUN = 'run'
COL_TAGS = '标签'
COL_LEVEL = '用例级别'
COL_URL = '请求地址'
COL_METHOD = "method"
COL_HEADERS = 'headers'
COL_QUERY = 'query'
COL_BODY = 'body'
COL_EXPECT = '预期结果'
COL_PRE_VARIABLE = '变量引入'
COL_POST_VARIABLE = '变量导出'
LEVEL_DICT = {
    'smoke': 'blocker',
    'high': 'critical',
    'low': 'minor',
    'not important': 'trivial',
    '冒烟': 'blocker',
    '高': 'critical',
    '中': 'normal',
    '低': 'minor',
    '不重要': 'trivial',
}
HOOK_DICT = {
    'setup': 'setup',
    'teardown': 'teardown',
    'setup_class': 'setup_class',
    'teardown_class': 'teardown_class',
    'setup_method': 'setup',
    'teardown_method': 'teardown',
    'setup method': 'setup',
    'teardown method': 'teardown',
    'setup class': 'setup_class',
    'teardown class': 'teardown_class',
    'setup case': 'setup',
    'teardown case': 'teardown',
    'setup suite': 'setup_class',
    'teardown suite': 'teardown_class',
    'setup_case': 'setup',
    'teardown_case': 'teardown',
    'setup_suite': 'setup_class',
    'teardown_suite': 'teardown_class',
}

TEST_CASE_PATH = 'test_cases'


def parse_step(line) -> Union[TStep]:
    url = get_value(line, COL_URL)
    if not url:
        request = None
    else:
        method = get_value(line, COL_METHOD, True).upper()
        query = get_value(line, COL_QUERY, False)
        try:
            query = json.loads(query) if query else {}
        except json.decoder.JSONDecodeError:
            pass
        body = get_value(line, COL_BODY, False)
        try:
            body = json.loads(body) if body else {}
        except json.decoder.JSONDecodeError:
            pass
        headers = get_value(line, COL_HEADERS, False)
        try:
            headers = json.loads(headers) if headers else {}
        except json.decoder.JSONDecodeError:
            pass
        request = TRequest(
            url=url,
            method=method,
            headers=headers,
            body=body,
            query=query
        )
    expect = [i.strip() for i in get_value(line, COL_EXPECT).split('\n')] if get_value(line, COL_EXPECT) else []
    if get_value(line, COL_PRE_VARIABLE):
        pre_variables = [i.strip() for i in str(get_value(line, COL_PRE_VARIABLE)).split('\n')]
    else:
        pre_variables = []

    if get_value(line, COL_POST_VARIABLE):
        post_variables = [i.strip() for i in str(get_value(line, COL_POST_VARIABLE)).split('\n')]
    else:
        post_variables = []
    return TStep(
        request=request,
        pre_variables=pre_variables,
        post_variables=post_variables,
        validators=expect
    )


def parse_cases(test_case_file_name, sheet=0) -> List[TCase]:
    logger.info(f'读取文件：{test_case_file_name}，sheet页：{sheet}')
    df = read_excel(test_case_file_name, sheet)
    data: list = df.to_dict(orient='records')
    cases: list = []
    run: bool = False
    write = False
    for i, line in enumerate(data):
        case_name = get_value(line, COL_CASE_NAME)
        if case_name:
            if case_name in HOOK_DICT:
                write = False
                continue
            write = True
            run = True if str(get_value(line, COL_RUN, True))[0].upper() == 'Y' else False
            level = get_value(line, COL_LEVEL, True).lower().strip()
            if level in LEVEL_DICT:
                level = LEVEL_DICT[level]
            if get_value(line, COL_TAGS):
                tag = [i.strip() for i in str(get_value(line, COL_TAGS)).split('\n')]
            else:
                tag = []
            cases.append(TCase(name=case_name, run=run, steps=[parse_step(line)], tag=tag, level=level))
        else:
            if write:
                cases[-1].steps.append(parse_step(line))
    return cases


def parse_hooks(test_case_file_name, sheet=0) -> List[THook]:
    df = read_excel(test_case_file_name, sheet)
    data: list = df.to_dict(orient='records')
    hooks: list = []
    run: bool = False
    write = False
    for i, line in enumerate(data):
        case_name = get_value(line, COL_CASE_NAME)
        if case_name:
            if case_name not in HOOK_DICT:
                write = False
                continue
            write = True
            run = True if str(get_value(line, COL_RUN, True))[0].upper() == 'Y' else False
            hooks.append(THook(hook_type=HOOK_DICT[case_name], run=run, steps=[parse_step(line)]))
        else:
            if write:
                hooks[-1].steps.append(parse_step(line))
    return hooks


def get_all_test_case() -> List[TSuite]:
    abs_test_case_path = os.path.abspath(os.path.join(os.path.curdir, TEST_CASE_PATH))
    test_case_file_names = os.listdir(abs_test_case_path)
    suites = []
    for test_case_file_name in test_case_file_names:
        if test_case_file_name.startswith('test_') and (
                test_case_file_name.endswith('.xlsx') or test_case_file_name.endswith('.xls')):
            logger.info(f'发现测试用例文件{test_case_file_name}, 正在解析')
            test_case_file = os.path.join(abs_test_case_path, test_case_file_name)
            test_case_file_obj = ExcelFile(test_case_file)
            sheets = test_case_file_obj.sheet_names
            test_case_file_obj.close()
            if test_case_file_name.endswith('.xlsx'):
                suite_name = test_case_file_name[5: -5]
            else:
                suite_name = test_case_file_name[5: -4]

            if len(sheets) == 1:
                cases = parse_cases(test_case_file)
                hooks = parse_hooks(test_case_file)
                suites.append(TSuite(name=suite_name, cases=cases, parent_suite_name=suite_name, hooks=hooks))
            else:
                for sheet in sheets:
                    if sheet.startswith('t_'):
                        cases = parse_cases(test_case_file, sheet)
                        hooks = parse_hooks(test_case_file, sheet)
                        sub_suite_name = sheet[2:]
                        suites.append(
                            TSuite(name=sub_suite_name, cases=cases, parent_suite_name=suite_name, hooks=hooks))
    return suites


def is_empty(cell):
    return True if isinstance(cell, float) and isnan(cell) else False


def get_value(line: dict, key: str, is_necessary: bool = False):
    value = line[key]
    if is_empty(value):
        if is_necessary:
            raise Exception(f'{key}不能为空')
        return None
    else:
        if isinstance(value, str):
            tmp = value.strip() or None
            if is_necessary and not tmp:
                raise Exception(f'{key}不能为空')
            return tmp
        else:
            return value


# @logger.catch(reraise=True)
# def get_variables(datafile: str, sheet=0):
#     logger.info(f'读取文件：{datafile}，sheet页：{sheet}')
#     df = read_excel(datafile, sheet)
#     data: list = df.to_dict(orient='records')
#     result: list = []
#     run: bool = False
#     for i, line in enumerate(data):
#         try:
#             case_name = get_value(line, COL_CASE_NAME)
#             if case_name:
#                 run = True if str(get_value(line, COL_RUN, True)).upper() == 'Y' else False
#                 if run:
#                     create_test_case(str(case_name), line, result)
#             else:
#                 if run:
#                     result[-1]['steps'].append(gen_step(line))
#         except Exception as e:
#             # logger.error(f'文件{datafile}第{i + 2}行读取错误：\n{e}')
#             root = Tk()
#             root.withdraw()
#             showerror('用例文件解析失败', f'文件{datafile}第{i + 2}行读取错误：\n{format_exc()}')
#             raise e
#     # variables = {'data': result}
#     return result
#
#
# def create_test_case(case_name: str, line: dict, result: list):
#     tags = [i.strip() for i in get_value(line, COL_TAGS).split('\n')] if get_value(line, COL_TAGS) else []
#     # if AUTO_ASSERT_KEYWORD not in case_name:
#     result.append({'case_name': case_name, 'tags': tags, 'steps': [gen_step(line)]})
#     logger.info(f'读取测试用例：{case_name}')
#
#
# def gen_step(line: dict):
#     url = get_value(line, COL_URL, True)
#     method = get_value(line, COL_METHOD, True).upper()
#     body = get_value(line, COL_DATA, False)
#     body = json.loads(get_value(line, COL_DATA, False)) if body else body
#     expect = [i.strip() for i in get_value(line, COL_EXPECT).split('\n')] if get_value(line, COL_EXPECT) else []
#     if get_value(line, COL_PRE_VARIABLE):
#         _variables = (i.strip() for i in str(get_value(line, COL_PRE_VARIABLE)).split('\n'))
#     else:
#         _variables = []
#     pre_variables = {}
#     for v in _variables:
#         index = v.index('=')
#         pre_variables[v[: index].strip()] = v[index + 1:].strip()
#
#     if get_value(line, COL_POST_VARIABLE):
#         _variables = (i.strip() for i in str(get_value(line, COL_POST_VARIABLE)).split('\n'))
#     else:
#         _variables = []
#     post_variables = {}
#     for v in _variables:
#         index = v.index('=')
#         post_variables[v[: index].strip()] = v[index + 1:].strip()
#     return {
#         'url': url,
#         'method': method,
#         'data': body,
#         'asserts': expect,
#         'pre variables': pre_variables,
#         'post variables': post_variables,
#     }


if __name__ == '__main__':
    import pprint

    pprint.pprint(get_all_test_case())
