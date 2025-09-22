import requests

# Authentication
token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
client_id = '5cd47024-d2ca-44df-bce2-2b7eecf13a71_78a0381c-9ae0-4e02-b3c0-640c7a6e13d5'
client_secret = 'QFwlMqVXc3xFBYCVCbfXt56n/rBTQjFoYu8CNmfN594='

payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'icdapi_access',
    'grant_type': 'client_credentials'
}

# Get access token
response = requests.post(token_endpoint, data=payload)
response.raise_for_status()
token = response.json()['access_token']

# Search for conditions
query = "malabsorption"
search_url = f"https://id.who.int/icd/release/11/2024-01/mms/search?q={query}"

headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json',
    'Accept-Language': 'en',
    'API-Version': 'v2'
}

# Get search results
search_response = requests.get(search_url, headers=headers)
search_response.raise_for_status()
search_data = search_response.json()

# Get top 5 results
top_results = search_data.get("destinationEntities", [])[:5]

print(f"Top {len(top_results)} results for '{query}':")
print("=" * 80)

# Process each result
for i, item in enumerate(top_results, 1):
    title = item.get("title", "").replace("<em class='found'>", "").replace("</em>", "")
    code = item.get("theCode", "N/A")
    entity_id = item.get("id", "")
    score = item.get("score", "N/A")
    chapter = item.get("chapter", "N/A")
    
    print(f"\n{i}. {title}")
    print(f"   ICD-11 Code: {code}")
    print(f"   Chapter: {chapter}")
    print(f"   Relevance Score: {score}")
    
    if entity_id:
        # Fetch detailed information for this entity
        try:
            detail_response = requests.get(entity_id, headers=headers)
            detail_response.raise_for_status()
            detail_data = detail_response.json()
            
            # Extract definition
            definition = detail_data.get("definition", {})
            if isinstance(definition, dict):
                definition_text = definition.get("@value", "No definition available")
            elif isinstance(definition, list) and definition:
                definition_text = definition[0].get("@value", "No definition available")
            else:
                definition_text = str(definition)
            
            print(f"   Definition: {definition_text}")
            
            # Extract additional details if available
            inclusion_terms = detail_data.get("inclusion", [])
            if inclusion_terms:
                print("   Inclusion Terms:")
                for term in inclusion_terms[:3]:  # Show first 3 terms
                    if isinstance(term, dict):
                        term_text = term.get("@value", "")
                        if term_text:
                            print(f"     - {term_text}")
            
            # Check for synonyms
            synonyms = detail_data.get("synonym", [])
            if synonyms:
                print("   Synonyms:")
                for synonym in synonyms[:3]:  # Show first 3 synonyms
                    if isinstance(synonym, dict):
                        synonym_text = synonym.get("@value", "")
                        if synonym_text:
                            print(f"     - {synonym_text}")
            
        except Exception as e:
            print(f"   Error fetching details: {str(e)}")
    else:
        print("   No entity ID available for detailed information")
    
    print("-" * 60)

print("\nSearch completed successfully!")