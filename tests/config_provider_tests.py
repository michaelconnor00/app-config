__author__ = 'bcullen'

import unittest
import boto
from app_config.app_config import AppConfig
from moto import mock_dynamodb


class TestConfigProvider(unittest.TestCase):
    """
    Test ability to get config JSON from DynamoDB
    """

    # Test lookup code without integration to persistent storage
    @mock_dynamodb
    def test_set_item_fails(self):
        setup_dynamo_mock()
        self.app_config_cls = AppConfig('us-east-1', 'unit_test')
        try:
            self.app_config_cls['unit_test_comp'] = "test"
        except TypeError as e:
            self.assertEqual(e.message, "'AppConfig' object does not support item assignment")

        try:
            self.app_config_cls['unit_test_comp']['foo'] = "test"
        except TypeError as e:
            self.assertEqual(e.message, "'AppConfig' object does not support item assignment")

    @mock_dynamodb
    def test_env_doesnt_exist(self):
        setup_dynamo_mock()
        app_config = AppConfig('us-east-1', 'foo-env-doesnt-exist')
        username = app_config['unit_test_comp']['username']
        self.assertEqual(username, 'testuser')
        password = app_config['unit_test_comp']['password']
        self.assertEqual(password, 'testpass')

    @mock_dynamodb
    def test_env_override(self):
        setup_dynamo_mock()
        self.app_config_cls = AppConfig('us-east-1', 'unit_test')
        username = self.app_config_cls['unit_test_comp']['username']
        self.assertEqual(username, 'testuser')
        password = self.app_config_cls['unit_test_comp']['password']
        self.assertEqual(password, 'envtestpass')

    @mock_dynamodb
    def helper_test_resource_not_found(self):
        setup_dynamo_mock()
        self.app_config_cls = AppConfig('us-east-1', 'unit_test')
        return self.app_config_cls['foo-doesnt-exist']['username']

    def test_resource_not_found(self):
        self.assertRaises(KeyError, self.helper_test_resource_not_found)

    @mock_dynamodb
    def helper_test_attribute_not_found(self):
        setup_dynamo_mock()
        self.app_config_cls = AppConfig('us-east-1', 'unit_test')
        return self.app_config_cls['unit_test_comp']['bar-doesnt-exist']

    def test_attribute_not_found(self):
        self.assertRaises(KeyError, self.helper_test_attribute_not_found)

    @mock_dynamodb
    def test_creation_with_bad_env_name(self):
        setup_dynamo_mock()
        app_config = AppConfig('us-east-1', "foo_barrr")
        self.assertEqual(app_config["unit_test_comp"]["password"], "testpass")

    @mock_dynamodb
    def test_creation_with_good_env_name(self):
        setup_dynamo_mock()
        app_config = AppConfig('us-east-1', "unit_test")
        self.assertEqual(app_config["unit_test_comp"]["password"], "envtestpass")

    @mock_dynamodb
    def test_app_config_with_custom_table(self):
        table_name = "test_table_new"
        setup_dynamo_mock(table_name=table_name)
        app_config = AppConfig('us-east-1', 'unit_test', table_name=table_name)
        self.assertEqual(app_config["unit_test_comp"]["password"], "envtestpass")

    @mock_dynamodb
    def test_non_default_config_values_get_loaded(self):
        setup_dynamo_mock()
        self.app_config_cls = AppConfig('us-east-1', 'unit_test')
        # 'test_env' key was not present in default config
        self.assertEqual(self.app_config_cls['unit_test_comp']['test_new_env_var'], 'test_val')

    def tearDown(self):
        pass


@mock_dynamodb
def setup_dynamo_mock(table_name="app_config"):
    conn = boto.connect_dynamodb()

    message_table_schema = conn.create_schema(
        hash_key_name='component',
        hash_key_proto_value=str,
        range_key_name='environment',
        range_key_proto_value=str
    )

    conn.create_table(
        name=table_name,
        schema=message_table_schema,
        read_units=10,
        write_units=10
    )

    table = conn.get_table(table_name)

    item_data1 = {
        'config': "{ \"username\": \"testuser\", \"password\": \"testpass\" }"
    }

    item1 = table.new_item(
        hash_key='unit_test_comp',
        range_key='default',
        attrs=item_data1
    )

    item_data2 = {
        'config': "{ \"password\": \"envtestpass\", \"test_new_env_var\": \"test_val\" }"
    }

    item2 = table.new_item(
        hash_key='unit_test_comp',
        range_key='unit_test',
        attrs=item_data2
    )

    for item in [item1, item2]:
        item.put()


def get_suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestConfigProvider)
