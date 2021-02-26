import json

import allure
import pytest


class DotDict(dict):
    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        self[key] = value

    def __getattr__(self, key):
        try:
            super().__getattribute__(key)
        except AttributeError:
            return self[key]


@pytest.fixture(scope='session')
def var():
    return DotDict()
