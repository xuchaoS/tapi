import os

import urllib3

from .runner import run_all_test_cases, open_test_report
from .parse import get_all_test_case
from .make import generate_test_case_scripts
from loguru import logger


def main(open_report=False):
    urllib3.disable_warnings()
    logger.add(os.path.join(os.curdir, 'outputs', f'run_test.log'),
               level='TRACE',
               encoding='utf-8')
    logger.trace('主程序开始执行')
    data = get_all_test_case()
    generate_test_case_scripts(data)
    run_all_test_cases()
    if open_report:
        open_test_report()
    logger.trace('主程序执行完毕')

if __name__ == '__main__':
    main()
