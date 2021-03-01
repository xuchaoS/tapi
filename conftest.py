import pprint

import pytest
from faker import Faker
from loguru import logger


class DotDict(dict):
    def __setattr__(self, key, value):
        self.__setitem__(key, value)
        logger.debug(f'全局变量设置: var.{key} = {repr(value)}')

    def __getattr__(self, key):
        logger.debug(f'全局变量读取: var.{key} = {repr(self.__getitem__(key))}')
        return self.__getitem__(key)


_var = DotDict()
_var.faker = Faker()


# @pytest.fixture(scope='session')
@pytest.fixture
def var():
    global _var
    logger.debug(f'用例开始全局变量:{pprint.pformat(_var)}')
    yield _var
    logger.debug(f'用例结束全局变量:{pprint.pformat(_var)}')


@pytest.fixture(autouse=True)
def log(request):
    logger.debug(f'测试用例开始执行: {request.module.__file__}::{request.cls.__name__}::{request.node.name}')
    yield
    logger.debug('测试用例结束执行')
