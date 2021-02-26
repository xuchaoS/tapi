import os
from enum import Enum
from typing import Any
from typing import Dict, Text, Union, Callable
from typing import List

from pydantic import BaseModel, Field
import allure
from pydantic import HttpUrl


class MethodEnum(Text, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    FILE = 'FILE'


class TRequest(BaseModel):
    method: MethodEnum
    url: Text
    headers: Union[Text, Dict[Text, Text]] = {}
    body: Union[Text, Dict[Text, Any]] = None
    query: Union[Text, Dict[Text, Any]] = None


class TStep(BaseModel):
    pre_variables: List = []
    post_variables: List = []
    request: Union[TRequest, None] = None
    validators: List = []


class TCase(BaseModel):
    name: Text
    steps: List[TStep] = []
    run: bool
    tag: List[Text] = []
    level: allure.severity_level = allure.severity_level.NORMAL


class HookTypeEnum(str, Enum):
    SETUP = 'setup'
    SETUP_CLASS = 'setup_class'
    TEARDOWN = 'teardown'
    TEARDOWN_CLASS = 'teardown_class'


class THook(BaseModel):
    hook_type: HookTypeEnum
    run: bool
    steps: List[TStep] = []


class TSuite(BaseModel):
    name: Text
    cases: List[TCase] = []
    parent_suite_name: Text
    hooks: List[THook] = []
