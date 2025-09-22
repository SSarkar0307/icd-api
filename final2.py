import requests
from requests.auth import HTTPBasicAuth

# --- Configuration ---
TOKEN_ENDPOINT = 'https://icdaccessmanagement.who.int/connect/token'
CLIENT_ID = '5cd47024-d2ca-44df-bce2-2b7eecf13a71_78a0381c-9ae0-4e02-b3c0-640c7a6e13d5'
CLIENT_SECRET = 'QFwlMqVXc3xFBYCVCbfXt56n/rBTQjFoYu8CNmfN594='
SCOPE = "icdapi_access"
GRANT_TYPE = "client_credentials"

def get_token():
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    payload = {
        "scope": SCOPE,
        "grant_type": GRANT_TYPE
    }
    r = requests.post(TOKEN_ENDPOINT, auth=auth, data=payload)
    r.raise_for_status()
    return r.json()["access_token"]

def search_icd(query, token, limit=5):
    search_url = "https://id.who.int/icd/release/11/2024-01/mms/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2"
    }
    params = {
        "q": query,
        "flatResults": "false",
        "useFlexisearch": "false",
        "highlightingEnabled": "false"
    }
    r = requests.get(search_url, headers=headers, params=params)
    r.raise_for_status()
    response_data = r.json()
    results = response_data.get("destinationEntities", [])
    return results[:limit]

def get_entity_details(entity_id, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2"
    }
    r = requests.get(entity_id, headers=headers)
    r.raise_for_status()
    return r.json()

def extract_definition(details):
    definition = details.get("definition", {})
    if isinstance(definition, dict):
        return definition.get("@value", "No definition available")
    elif isinstance(definition, list) and definition:
        first_def = definition[0]
        if isinstance(first_def, dict):
            return first_def.get("@value", "No definition available")
        else:
            return str(first_def)
    else:
        return str(definition)

if __name__ == "__main__":
    token = get_token()
    query = "diabetes"
    results = search_icd(query, token, limit=5)
    
    print(f"Found {len(results)} results for '{query}':")
    print("=" * 80)
    
    for i, item in enumerate(results, 1):
        print(f"Result {i}:")
        
        # Extract title
        title = item.get("title", "No title available")
        if isinstance(title, dict):
            title = title.get("@value", "No title available")
        print(f"  Title: {title}")
        
        # Extract entity ID
        entity_id = item.get("id")
        if not entity_id:
            print("  No entity ID found, skipping details")
            print("-" * 40)
            continue
        
        print(f"  Entity ID: {entity_id}")
        
        try:
            details = get_entity_details(entity_id, token)
            definition = extract_definition(details)
            print(f"  Definition: {definition}")
        except Exception as e:
            print(f"  Error fetching details: {str(e)}")
        
        print("-" * 40)