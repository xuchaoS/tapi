import dis
import os
import time
from typing import NoReturn, List

import autopep8
import jinja2

from .models import TSuite

TEST_SCRIPT_DIR = os.path.join(os.curdir, f'test_scripts_{time.strftime("%Y%m%d_%H%M%S")}')
TEMPLATE = jinja2.Template('''import allure
import json

from tapi.request import request


class TestSuit(object): 
    {% for hook in suite.hooks %}
    {% if hook.run %}
    {% if hook.hook_type.value == 'setup' %}
    def setup_method(self):
    {% endif %}
    {% if hook.hook_type.value == 'teardown' %}
    def teardown_method(self):
    {% endif %}
    {% if hook.hook_type.value == 'setup_class' %}
    @classmethod
    def setup_class(self):
    {% endif %}
    {% if hook.hook_type.value == 'teardown_class' %}
    @classmethod
    def teardown_class(self):
    {% endif %}
        {% for step in hook.steps %}
        {% for pre_variable in step.pre_variables %}
        {{ pre_variable }}
        {% endfor %}
        {% if step.request %}
        url = f'{{ step.request.url }}'
        method = '{{ step.request.method.value }}'
        headers = {{ step.request.headers }}
        query = {{ step.request.query }}
        body = {{ step.request.body }}
        r = request(url, method, headers, query, body)
        {% endif %}
        {% for post_variable in step.post_variables %}
        {{ post_variable }}
        {% endfor %}
        {% for validator in step.validators %}
        assert {{ validator }}
        {% endfor %}
        {% endfor %}
    {% endif %}
    {% endfor%}

    {% for case in suite.cases %}
    {% if not case.run %}@pytest.mark.skip{% endif %}
    {% if case.tag %}@allure.tag('{{ "', '".join(case.tag) }}'){% endif %}
    @allure.parent_suite('{{ suite.parent_suite_name }}')
    @allure.suite('{{ suite.parent_suite_name }}')
    @allure.sub_suite('{{ suite.name }}')
    @allure.title('{{ case.name }}')
    @allure.severity('{{ case.level.value }}')
    def test_case_{{ loop.index }}(self, var): 
        {% for step in case.steps %}with allure.step('step {{ loop.index }}'):
            {% for pre_variable in step.pre_variables %}{{ pre_variable }}
            {% endfor %}
            url = f'{{ step.request.url }}'
            method = '{{ step.request.method.value }}'
            headers = {{ step.request.headers }}
            query = {{ step.request.query }}
            body = {{ step.request.body }}
            r = request(url, method, headers, query, body)
            {% for post_variable in step.post_variables %}{{ post_variable }}
            {% endfor %}
            allure.attach(json.dumps(var, indent=4), '全局变量：var', allure.attachment_type.JSON)
            {% for validator in step.validators %}assert {{ validator }}
            {% endfor %}
        {% endfor %}
    {% endfor %}
''')


def generate_test_case_scripts(suites: List[TSuite]) -> NoReturn:
    for suite in suites:
        content = TEMPLATE.render(suite=suite)
        content = autopep8.fix_code(content)
        if not os.path.isdir(TEST_SCRIPT_DIR):
            os.mkdir(TEST_SCRIPT_DIR)
        filename = f'test_{suite.parent_suite_name}_{suite.name}.py' if suite.parent_suite_name != suite.name else f'test_{suite.name}.py'
        test_case_script_name = os.path.join(TEST_SCRIPT_DIR, filename)
        with open(test_case_script_name, 'w', encoding='utf-8') as f:
            f.write(content)
