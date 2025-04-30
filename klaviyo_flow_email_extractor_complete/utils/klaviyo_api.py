import requests

BASE_URL = "https://a.klaviyo.com/api"

def klaviyo_api_request(endpoint, api_key, params=None):
    """Generic Klaviyo API request helper."""
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=headers, params=params or {})
    response.raise_for_status()
    return response.json()

def get_flows(api_key, params={"page[size]": 50}):
    return klaviyo_api_request("v1/flows", api_key, params)

def get_flow_actions(flow_id, api_key, params={"page[size]": 50}):
    return klaviyo_api_request(f"v1/flows/{flow_id}/actions", api_key, params)

def get_email_content(action_id, api_key):
    return klaviyo_api_request(f"v1/content_actions/{action_id}/render", api_key)

def get_flow_metrics(flow_id, api_key, params=None):
    return klaviyo_api_request(f"v1/flows/{flow_id}/metrics", api_key, params)

def get_message_metrics(message_id, api_key, params=None):
    return klaviyo_api_request(f"v1/metrics/{message_id}", api_key, params)
