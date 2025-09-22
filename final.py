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
    # Use Basic Authentication instead of sending credentials in the body
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    
    # The token endpoint expects these parameters in the body
    payload = {
        "scope": SCOPE,
        "grant_type": GRANT_TYPE
    }
    
    # Make the request with Basic Auth and form data
    r = requests.post(TOKEN_ENDPOINT, auth=auth, data=payload)
    
    # Check for errors and provide more detailed information
    try:
        r.raise_for_status()
        return r.json()["access_token"]
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {r.text}")
        raise
    except KeyError:
        print(f"Unexpected response format: {r.json()}")
        raise

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
        "flatResults": "false",  # Changed to false to get hierarchical results
        "useFlexisearch": "false",
        "highlightingEnabled": "false"  # Disable highlighting to avoid HTML tags
    }
    
    try:
        r = requests.get(search_url, headers=headers, params=params)
        r.raise_for_status()
        response_data = r.json()
        
        # Debug: print the full response to understand its structure
        print("Search API response:", response_data)
        
        # The structure might have changed, let's check for different possible keys
        if "destinationEntities" in response_data:
            results = response_data["destinationEntities"]
        elif "entity" in response_data:
            results = [response_data["entity"]]
        elif "entities" in response_data:
            results = response_data["entities"]
        else:
            print("Unexpected response structure. Available keys:", response_data.keys())
            results = []
        
        return results[:limit]
    
    except requests.exceptions.HTTPError as e:
        print(f"Search API Error: {e}")
        print(f"Response: {r.text}")
        return []

def clean_html(text):
    """Remove HTML tags from text"""
    if not text:
        return "No title available"
    if isinstance(text, dict):
        text = text.get("@value", "No title available")
    return re.sub(r'<[^>]+>', '', str(text))

def get_entity_details(entity_id, token):
    # The entity_id might be a full URL or just an ID
    if entity_id.startswith("http"):
        # It's a full URL, use it directly
        details_url = entity_id
    else:
        # It's just an ID, construct the URL
        details_url = f"https://id.who.int/icd/release/11/2024-01/{entity_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2"
    }
    
    try:
        r = requests.get(details_url, headers=headers)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        print(f"Entity details Error: {e}")
        print(f"Response: {r.text}")
        return {}

# --- Example usage ---
if __name__ == "__main__":
    try:
        token = get_token()
        print("Successfully obtained token")
        
        query = "malabsorption"
        results = search_icd(query, token, limit=5)
        
        print(f"Found {len(results)} results for '{query}':")
        print("=" * 80)
        
        for i, item in enumerate(results, 1):
            print(f"Result {i}:")
            
            # Extract title with HTML cleaning
            title = item.get("title", {})
            clean_title = clean_html(title)
            print(f"  Title: {clean_title}")
            
            # Try different possible ID fields
            entity_id = item.get("@id") or item.get("id") or item.get("entityId")
            
            if not entity_id:
                print("  No entity ID found, skipping details")
                print("-" * 40)
                continue
            
            print(f"  Entity ID: {entity_id}")
            
            details = get_entity_details(entity_id, token)
            
            # Extract definition safely
            definition = details.get("definition", {})
            if isinstance(definition, dict):
                definition_text = definition.get("@value", "No definition available")
            elif isinstance(definition, list) and definition:
                definition_text = definition[0].get("@value", "No definition available")
            else:
                definition_text = str(definition)
                
            print(f"  Definition: {definition_text}")
            print("-" * 40)
            
    except Exception as e:
        print(f"An error occurred: {e}")