"""
Look up sensitive configuration items such as credentials and keys
so they don't need to be hardcoded as artifacts in the code repository.
This implementation finds it's resources in the DynamoDB table called 'app_config'
"""

import boto
import boto.dynamodb
import json
from boto.exception import BotoClientError
from collections import defaultdict, Mapping


class AppConfig(Mapping):
    _ENVIRONMENT_DEFAULT_NAME = 'default'
    _DYNAMO_DB_TABLE = 'app_config'

    def __init__(self, region, environment_name, table_name=_DYNAMO_DB_TABLE):

        # Front load all resources early to fail fast if there is a retrieval or parsing problem
        self._config_sections = defaultdict(dict)
        self._environment = environment_name

        _conn = boto.dynamodb.connect_to_region(region_name=region)
        self._table = _conn.get_table(table_name)

    def __getitem__(self, resource_name):
        if not self._config_sections[resource_name]:
            self._load_config_section(resource_name, self._ENVIRONMENT_DEFAULT_NAME)
            self._load_config_section(resource_name, self._environment)

        return self._config_sections[resource_name]

    def __iter__(self):
        return iter(self._config_sections)

    def __len__(self):
        return len(self._config_sections)

    def __contains__(self, item):
        return item in self._config_sections

    def _load_config_section(self, resource_name, environment):
        try:
            item = self._table.get_item(hash_key=resource_name, range_key=environment)
            if item:
                resource_dict = json.loads(item.get("config"))
                self._config_sections[resource_name].update(resource_dict)
        except BotoClientError as e:
            if e.reason == "Key does not exist.":
                print(e.message)
            else:
                raise
        except Exception as e:
            raise Exception('Error occured getting config, Reason: {0}'.format(e.message))
