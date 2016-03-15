import os
import xmlrunner
from tests.config_provider_tests import setup_dynamo_mock
from tests import config_provider_tests
from moto import mock_dynamodb


@mock_dynamodb
def run_tests():
    output = 'test-reports/unit/app_config'

    suites = [
        config_provider_tests
    ]

    # configure mocks for dynamoDb
    setup_dynamo_mock()

    for suite in suites:
        xmlrunner.XMLTestRunner(output=output).run(suite.get_suite())
        os.system('cls' if os.name == 'nt' else 'clear')
