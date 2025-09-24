import requests, time
from flask import current_app
from flask import request as flask_request
import logging

log = logging.getLogger("bones.auth_client")

def _mask(d: dict) -> dict:
    if not isinstance(d, dict):
        return d
    m = {}
    for k, v in d.items():
        if k.lower() in {"password", "token", "authorization"}:
            m[k] = "****"
        else:
            m[k] = v
    return m

def _request_id():
    # propagate inbound request id if present
    return (flask_request.headers.get("X-Request-ID") if flask_request else None) or None

def auth_service_request(endpoint, data):
    url = f"{current_app.config['AUTH_SERVICE_URL']}{endpoint}"
    headers = {"X-Api-Key": current_app.config["AUTH_SERVICE_API_KEY"]}
    rid = _request_id()

    try:
        res = requests.post(url, headers=headers, json=data, timeout=5)
        safe_data = dict(data)
        if "password" in safe_data:
            safe_data["password"] = "***"
        log.info(
            "outbound_request %s %s status=%s body=%s",
            url,
            data,
            res.status_code,
            res.text[:200],
        )
    except requests.exceptions.RequestException as e:
        log.error("outbound_request_failed", extra={"error": str(e), "endpoint": endpoint})
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
