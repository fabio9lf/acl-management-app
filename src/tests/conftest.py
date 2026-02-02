import json
import pytest

def pytest_addoption(parser):
    parser.addoption("--rule-file", action="store", default=None, help="Percorso del file JSON contenente la regola")

@pytest.fixture
def rule(request):
    rule_file = request.config.getoption("--rule-file")
    if not rule_file:
        pytest.fail("Devi passare un file json!")
    with open(rule_file, "r") as file:
        rule_data = json.load(file)
    return rule_data


def pytest_report_header(config):
    rule_file = config.getoption("--rule-file")
    with open(rule_file) as file:
        rule = json.load(file)
    if rule["type"] == "policy":
        optional = [
            f"dei pacchetti di tipo {rule['rule']['protocollo']}" if rule["rule"]["protocollo"] != "" else f"dei pacchetti ip",
            f"da {rule['rule']['src_node']['nome']} ({rule['rule']['src_node']['ip']})" if rule["rule"]["src_node"] is not None else None,
            f"a {rule['rule']['dest_node']['nome']} ({rule['rule']['dest_node']['ip']})" if rule["rule"]["dest_node"] is not None else None
        ]
        

        return f"Test della {rule['type']} della policy con {rule['rule']['target']} " + " ".join(filter(None, optional))
    return f"Test della connettività tra l'host {rule['rule']['src_node']['nome']} ({rule['rule']['src_node']['ip']}) e l'host {rule['rule']['dest_node']['nome']} ({rule['rule']['dest_node']['ip']}) con pacchetto di tipo {rule['rule']['protocollo']}"