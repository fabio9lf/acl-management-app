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

    optional = [
        f"dei pacchetti di tipo {rule['protocollo']}" if rule["protocollo"] is not None else None,
        f"da {rule['src_node']['nome']} ({rule['src_node']['ip']})" if rule["src_node"] is not None else None,
        f"a {rule['dest_node']['nome']} ({rule['dest_node']['ip']})" if rule["dest_node"] is not None else None
    ]
    

    return f"Test della {type['nome']} della policy con {rule['target']} " + " ".join(filter(None, optional))