from requests_oauthlib import OAuth1 as OAuth
import requests, json

client_key='xxxxxxx'
client_secret='xxxxxxxx'
resource_owner_key='xxxxxxxx'
resource_owner_secret='xxxxxxxx'

MAGENTO_HOST = 'http://0.0.0.0:8000'
MAGENTO_API_BASE = '%s/index.php/rest/V1/' % MAGENTO_HOST

consumer_key = 'xxxxx'
consumer_secret = 'xxxxx'
access_token = 'xxxxx'
access_token_secret = 'xxxx'