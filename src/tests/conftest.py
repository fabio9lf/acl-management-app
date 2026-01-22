import json
import pytest

def pytest_addoption(parser):
    parser.addoption("--rule", action="store", default="{}")

@pytest.fixture
def rule(request):
    return json.loads(request.config.getoption("--rule"))


def pytest_report_header(config):
    rule = json.loads(config.getoption("--rule"))
    if rule["type"] == "policy":
        optional = [
            f"dei pacchetti di tipo {rule['rule']['protocollo']}" if rule["rule"]["protocollo"] != "" else f"dei pacchetti ip",
            f"da {rule['rule']['src_node']['nome']} ({rule['rule']['src_node']['ip']})" if rule["rule"]["src_node"] is not None else None,
            f"a {rule['rule']['dest_node']['nome']} ({rule['rule']['dest_node']['ip']})" if rule["rule"]["dest_node"] is not None else None
        ]
        

        return f"Test della {rule['type']} della policy con {rule['rule']['target']} " + " ".join(filter(None, optional))
    return f"Test della connettività tra l'host {rule['rule']['src_node']['nome']} ({rule['rule']['src_node']['ip']}) e l'host {rule['rule']['dest_node']['nome']} ({rule['rule']['dest_node']['ip']}) con pacchetto di tipo {rule['rule']['protocollo']}"