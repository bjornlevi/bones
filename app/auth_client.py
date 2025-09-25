import requests, time
from flask import current_app
from flask import request as flask_request
import logging

log = logging.getLogger("bones.auth_client")

def _mask(value):
    """Recursively mask sensitive fields in dicts/lists."""
    if isinstance(value, dict):
        masked = {}
        for k, v in value.items():
            if k.lower() in {"password", "token", "authorization"}:
                masked[k] = "****"
            else:
                masked[k] = _mask(v)
        return masked
    elif isinstance(value, list):
        return [_mask(v) for v in value]
    else:
        return value

def _request_id():
    # propagate inbound request id if present
    return (flask_request.headers.get("X-Request-ID") if flask_request else None) or None

def auth_service_request(endpoint, data):
    url = f"{current_app.config['AUTH_SERVICE_URL']}{endpoint}"
    headers = {"X-Api-Key": current_app.config["AUTH_SERVICE_API_KEY"]}
    rid = _request_id()

    try:
        res = requests.post(url, headers=headers, json=data, timeout=5)

        # Mask request data
        safe_req = _mask(data)

        # Mask response (JSON if possible; else truncate text)
        try:
            safe_body = _mask(res.json())
        except Exception:
            safe_body = res.text[:200]

        log.info(
            "outbound_request %s %s status=%s body=%s",
            url,
            safe_req,
            res.status_code,
            safe_body,
        )
    except requests.exceptions.RequestException as e:
        log.error("outbound_request_failed endpoint=%s error=%s", endpoint, str(e))
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
