import requests

# --- Step 1: Authenticate ---
token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
client_id = '5cd47024-d2ca-44df-bce2-2b7eecf13a71_78a0381c-9ae0-4e02-b3c0-640c7a6e13d5'
client_secret = 'QFwlMqVXc3xFBYCVCbfXt56n/rBTQjFoYu8CNmfN594='

payload = {
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "icdapi_access",
    "grant_type": "client_credentials",
}
token = requests.post(token_endpoint, data=payload).json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "Accept-Language": "en",
    "API-Version": "v2",
}

# --- Step 2: Search directly in MMS linearization ---
query = "diabetes"
search_uri = (
    f"https://id.who.int/icd/release/11/2024-01/mms/search"
    f"?q={query}&flatResults=true&includeKeywordResult=false&highlight=false"
)

search_response = requests.get(search_uri, headers=headers).json()

print("\n🔎 Direct MMS search results:")
for item in search_response.get("destinationEntities", []):
    title = item.get("title", "").replace("<em class='found'>", "").replace("</em>", "")
    code = item.get("theCode", "")
    entity_id = item.get("id", "")
    print(f"{title} -> Code: {code}, ID: {entity_id}")

# --- Step 3: Map TM2/Foundation ID (SM36) into MMS linearization ---
sm36_foundation_uri = "http://id.who.int/icd/release/11/2024-01/foundation/SM36"
lookup_uri = (
    "https://id.who.int/icd/release/11/2024-01/mms/linearization"
    f"?foundationUri={sm36_foundation_uri}"
)

lookup_response = requests.get(lookup_uri, headers=headers).json()

print("\n📌 Mapping SM36 (TM2) into MMS:")
for entity in lookup_response.get("destinationEntities", []):
    title = entity.get("title", "")
    code = entity.get("theCode", "")
    entity_id = entity.get("id", "")
    print(f"{title} -> Code: {code}, ID: {entity_id}")
