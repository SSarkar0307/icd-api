import requests

token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
client_id = '5cd47024-d2ca-44df-bce2-2b7eecf13a71_78a0381c-9ae0-4e02-b3c0-640c7a6e13d5'
client_secret = 'QFwlMqVXc3xFBYCVCbfXt56n/rBTQjFoYu8CNmfN594='

payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'icdapi_access',
    'grant_type': 'client_credentials'
}
token = requests.post(token_endpoint, data=payload).json()['access_token']

# Correct search endpoint
query= "fever"
uri = (f"https://id.who.int/icd/release/11/2024-01/mms/search?q={query}")
# uri = (f"https://id.who.int/icd/release/11/2024-01/mms/search?q=kalliral&linearization=tm2")

headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json',
    'Accept-Language': 'en',
    'API-Version': 'v2'
}

r = requests.get(uri, headers=headers).json()

# 🔍 Debug
print("Full response:", r)

# Parse results if present
for item in r.get("destinationEntities", []):
    title = item.get("title", "").replace("<em class='found'>", "").replace("</em>", "")
    code = item.get("theCode", "")
    entity_id = item.get("id", "")
    print(f"{title} -> Code: {code}, ID: {entity_id}")

