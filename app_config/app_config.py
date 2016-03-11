"""
Look up sensitive configuration items such as credentials and keys
so they don't need to be hardcoded as artifacts in the code repository.
This implementation finds it's resources in the DynamoDB table called 'config_provider'
"""

import boto
import boto.dynamodb
import json
import time
from collections import defaultdict


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2 - time1) * 1000.0)
        return ret

    return wrap


class ConfigProvider(object):
    _ENVIRONMENT_DEFAULT_NAME = 'default'
    _DYNAMO_DB_TABLE = 'app_config'

    def __init__(self, region, environment_name, table_name=_DYNAMO_DB_TABLE):

        # Front load all resources early to fail fast if there is a retrieval or parsing problem
        self._resources = defaultdict(dict)
        self._environment = environment_name
        self._conn = boto.dynamodb.connect_to_region(region_name=region)
        self._table = self._conn.get_table(table_name)

    @timing
    def __getitem__(self, resource_name):
        if not self._resources[resource_name]:
            self._load_resources_from_dynamo_db(resource_name, self._ENVIRONMENT_DEFAULT_NAME)
            self._load_resources_from_dynamo_db(resource_name, self._environment)

        return self._resources[resource_name]

    def _load_resources_from_dynamo_db(self, resource_name, environment):
        try:
            item = self._table.get_item(hash_key=resource_name, range_key=environment)
            if item:
                resource_dict = json.loads(item.get("config"))
                self._resources[resource_name].update(resource_dict)
        except Exception as e:
            #raise Exception('Problem decoding json in {0}. Reason: {1}'.format(resource_name, e.message))
            pass


c = ConfigProvider("us-east-1", "unit_test_env")
print c["workflows"]["username"]
print c["workflows"]["username"]