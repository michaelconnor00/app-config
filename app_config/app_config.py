"""
Application configuration provider with AWS DynamoDB persistance.
"""

import boto
import boto.dynamodb
import json
import logging
from boto.exception import BotoClientError
from collections import Mapping

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AppConfigException(Exception):
    pass


class ImmutableDict(Mapping):
    def __init__(self, data):
        assert(isinstance(data, dict))
        self.data = data

    def __getitem__(self, resource_name):
        return self.data[resource_name]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


class AppConfig(Mapping):
    _ENVIRONMENT_DEFAULT_NAME = 'default'
    _DYNAMO_DB_TABLE = 'app_config'

    def __init__(self, region, environment_name, table_name=_DYNAMO_DB_TABLE):
        self._environment = environment_name
        self._config_sections = {}

        self._table = boto.dynamodb.connect_to_region(region_name=region).get_table(table_name)

    def __getitem__(self, resource_name):
        if not self._config_sections.get(resource_name):
            self._load_config_section(resource_name, self._environment)

        return self._config_sections[resource_name]

    def __iter__(self):
        return iter(self._config_sections)

    def __len__(self):
        return len(self._config_sections)

    def _load_config_section(self, section_name, environment):
        tmp_dict = self._load_raw_dict(section_name, self._ENVIRONMENT_DEFAULT_NAME)
        tmp_dict.update(self._load_raw_dict(section_name, environment))

        self._config_sections[section_name] = ImmutableDict(tmp_dict)

    def _load_raw_dict(self, section_name, environment):
        return_dict = {}
        try:
            item = self._table.get_item(hash_key=section_name, range_key=environment)
            if item:
                dict_ = json.loads(item.get("config", "{}"))
                assert(isinstance(dict_, dict))
                return_dict = dict_
        except BotoClientError as e:
            if e.reason == "Key does not exist.":
                logger.warning(e.message)
            else:
                raise
        except Exception as e:
            raise AppConfigException('Error occurred getting config, Reason: {0}'.format(e.message))

        return return_dict
