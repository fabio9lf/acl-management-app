import json
import pytest

def pytest_addoption(parser):
    parser.addoption("--rule", action="store", default="{}")
    parser.addoption("--type", action="store", default="{}")

@pytest.fixture
def rule(request):
    return json.loads(request.config.getoption("--rule"))

@pytest.fixture
def type(request):
    return json.loads(request.config.getoption("--type"))

def pytest_report_header(config):
    rule = json.loads(config.getoption("--rule"))
    type = json.loads(config.getoption("--type"))

    return f"Test della {type['nome']} della policy con {rule['target']} dei pacchetti da {rule['src_node']['nome']} ({rule['src_node']['ip']}) a {rule['dest_node']['nome']} ({rule['dest_node']['ip']})"