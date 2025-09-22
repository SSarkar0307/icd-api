import requests
import re
from requests.auth import HTTPBasicAuth

# --- Configuration ---
TOKEN_ENDPOINT = 'https://icdaccessmanagement.who.int/connect/token'
CLIENT_ID = '5cd47024-d2ca-44df-bce2-2b7eecf13a71_78a0381c-9ae0-4e02-b3c0-640c7a6e13d5'
CLIENT_SECRET = 'QFwlMqVXc3xFBYCVCbfXt56n/rBTQjFoYu8CNmfN594='
SCOPE = "icdapi_access"
GRANT_TYPE = "client_credentials"

def get_token():
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    payload = {"scope": SCOPE, "grant_type": GRANT_TYPE}
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
    
    if "destinationEntities" in response_data:
        results = response_data["destinationEntities"]
    else:
        results = []
    
    return results[:limit]

def clean_html(text):
    if not text:
        return "No title available"
    if isinstance(text, dict):
        text = text.get("@value", "No title available")
    return re.sub(r'<[^>]+>', '', str(text))

def get_entity_details(entity_id, token):
    if entity_id.startswith("http"):
        details_url = entity_id
    else:
        details_url = f"https://id.who.int/icd/release/11/2024-01/{entity_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2"
    }
    
    r = requests.get(details_url, headers=headers)
    r.raise_for_status()
    return r.json()

# --- Example usage ---
if __name__ == "__main__":
    try:
        token = get_token()
        query = "malabsorption"
        results = search_icd(query, token, limit=5)
        
        print(f"Found {len(results)} results for '{query}':")
        print("=" * 80)
        
        for i, item in enumerate(results, 1):
            print(f"Result {i}:")
            
            # Extract and clean title
            title = item.get("title", {})
            clean_title = clean_html(title)
            print(f"  Title: {clean_title}")
            
            # Extract ICD code, chapter, and score
            icd_code = item.get("theCode", "N/A")
            chapter = item.get("chapter", "N/A")
            score = item.get("score", "N/A")
            
            print(f"  ICD Code: {icd_code}")
            print(f"  Chapter: {chapter}")
            print(f"  Relevance Score: {score}")
            
            # Extract entity ID for details call
            entity_id = item.get("id")
            
            if not entity_id:
                print("  No entity ID found, skipping details")
                print("-" * 40)
                continue
            
            # Get detailed information
            try:
                details = get_entity_details(entity_id, token)
                
                # Extract definition
                definition = details.get("definition", {})
                if isinstance(definition, dict):
                    definition_text = definition.get("@value", "No definition available")
                elif isinstance(definition, list) and definition:
                    definition_text = definition[0].get("@value", "No definition available")
                else:
                    definition_text = str(definition)
                    
                print(f"  Definition: {definition_text}")
                
            except Exception as e:
                print(f"  Error fetching details: {str(e)}")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"An error occurred: {e}")