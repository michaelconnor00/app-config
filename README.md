# GBDX App-Config

How to Use
----------


```bash
$ pip install app-config
```

```python
from app_config.app_config import AppConfig

app_config = AppConfig(<aws region>, <config environment>, <dynamoDb Table name>)

print(app_config['workflows']['username'])
'my_username'
```




