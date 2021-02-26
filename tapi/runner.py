import os

from .make import TEST_SCRIPT_DIR
import pytest


def run_all_test_cases():
    pytest.main(['--alluredir', r'.\outputs\allure', '-vs', '--clean-alluredir', TEST_SCRIPT_DIR])


def open_test_report():
    os.system(r'allure serve outputs\allure')
