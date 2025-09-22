import requests

token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
client_id = '5cd47024-d2ca-44df-bce2-2b7eecf13a71_78a0381c-9ae0-4e02-b3c0-640c7a6e13d5'
client_secret = 'QFwlMqVXc3xFBYCVCbfXt56n/rBTQjFoYu8CNmfN594='
scope = 'icdapi_access'
grant_type = 'client_credentials'


# get the OAUTH2 token

# set data to post
payload = {'client_id': client_id, 
	   	   'client_secret': client_secret, 
           'scope': scope, 
           'grant_type': grant_type}
           
# make request
r = requests.post(token_endpoint, data=payload, verify=False).json()
token = r['access_token']


# access ICD API

uri = 'https://id.who.int/icd/entity'

# HTTP header fields to set
headers = {'Authorization':  'Bearer '+token, 
           'Accept': 'application/json', 
           'Accept-Language': 'en',
	   'API-Version': 'v2'}
           
# make request           
r = requests.get(uri, headers=headers, verify=False)

# print the result
print (r.text)			
