# GBDX App-Config

In a Nutshell
-------------
App-Config is a utility to retrieve configuration data from a DynamoDb Table and access it easily.

Setup
-----
##### 1)  Create DynamoDb Table with HashKey and RangeKey of your choosing. 
  Example: TableName: app_config, HashKey: component, RangeKey: environment
##### 2)  Create attribute called 'config', and store JSON encoded string of key/value pairs
  Example: 
  ```json
  "{ \"username\": \"testuser\", \"password\": \"testpass\" }"
  ```
##### 3) Your DynamoDb schema should appear like so:

  | component | environment | config |  
  ____________________________________

How to Use
----------


```bash
$ pip install app-config
```

```python
from app_config.app_config import AppConfig

app_config = AppConfig(<aws region>, <config environment>, <dynamoDb Table name>)

print(app_config['workflows']['username'])
'testuser'
```




