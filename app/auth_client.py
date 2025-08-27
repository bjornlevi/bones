import requests
from flask import current_app

def auth_service_request(endpoint, data):
    url = f"{current_app.config['AUTH_SERVICE_URL']}{endpoint}"
    headers = {"x-api-key": current_app.config["AUTH_SERVICE_API_KEY"]}
    try:
        res = requests.post(url, headers=headers, json=data, timeout=5)
        print(f"[AUTH_CLIENT] POST {url} {res.status_code} {res.text}")  # 👈 debug
    except requests.exceptions.RequestException as e:
        print(f"[AUTH_CLIENT] Request failed: {e}")
        return {"error": str(e)}, 500

    if res.status_code not in (200, 201):
        return None, res.status_code
    return res.json(), res.status_code

def login(username, password):
    """Authenticate a user against the auth service."""
    return auth_service_request("/login", {"username": username, "password": password})

def verify_token(token):
    """Verify a JWT token via the auth service."""
    return auth_service_request("/verify", {"token": token})

def userinfo(token):
    """Fetch user info via the auth service."""
    return auth_service_request("/userinfo", {"token": token})
