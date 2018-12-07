import os
import xmlrunner
from tests.app_config_tests import setup_dynamo_mock
from tests import app_config_tests
from moto import mock_dynamodb


@mock_dynamodb
def run_tests():
    output = 'test-reports/unit/app_config'

    suites = [
        app_config_tests
    ]

    # configure mocks for dynamoDb
    setup_dynamo_mock()

    for suite in suites:
        xmlrunner.XMLTestRunner(output=output).run(suite.get_suite())
        os.system('cls' if os.name == 'nt' else 'clear')
