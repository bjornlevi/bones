# Basic setup for app to auth

## 1) Browser → Traefik → Flask (with path prefix)

[Browser]
  GET http://HOST/auth-service/ui/login  
      |  
      v  
[Traefik :80, entrypoint=web]  
  Router rule: PathPrefix(`/auth-service`)  
  Middlewares:  
    1) StripPrefix(`/auth-service`)        # remove external base path  
    2) Add headers:  
         X-Forwarded-Prefix: /auth-service  
         X-Script-Name:     /auth-service  
      |  
      v  
[auth-service container]  
  Gunicorn on 0.0.0.0:5000  
  Flask WSGI stack:  
    ScriptNameFromForwardedPrefix -> sets SCRIPT_NAME from headers  
    ProxyFix(x_for=1, x_proto=1, x_host=1, x_prefix=1)  
      |  
      v  
  Flask routes see: /ui/login, /api/health (no /auth-service)  
  BUT url_for(...) builds URLs prefixed with /auth-service (thanks to SCRIPT_NAME)  
      |  
      v  
[Response to Browser]  
  Redirects/links/forms point to /auth-service/... (prefix preserved)  

## 2) Service → Service (inside Docker, no Traefik, no prefix)  

[app container]  ---- Docker DNS + bridge network ---->  [auth-service container]  
  POST http://auth-service:5000/api/login                    Flask @ 0.0.0.0:5000  
    Headers:  
      X-Api-Key: <service key>                          (require_api_key checks DB)  
    Body:  
      {"username":"admin","password":"adminpass"}       (User table via SQLAlchemy)  
         |  
         v  
      {"token":"<jwt>"}                                 (PyJWT with SECRET_KEY)  

  ### Verification  
  POST http://auth-service:5000/api/verify  
    Headers: X-Api-Key: <service key>  
    Body: {"token":"<jwt>"}  
    -> {"user_id":..., "username":"..."}  

## 3) Startup / bootstrap flow  

[Container start]  
  Gunicorn binds :5000  
  Flask create_app():  
    - db.create_all()  
    - ensure DEFAULT_ADMIN (admin/adminpass) exists  
    - ensure one ServiceApiKey exists (or use UI to mint more)  
  Healthcheck -> /health -> container becomes (healthy)  
  Traefik sees healthy container + labels -> creates router/service/middlewares  

## 4) Minimal label + code checklist (copyable)  

### docker-compose.yml requirements  
    labels:  
      - traefik.enable=true  
      - traefik.docker.network=web  
      - traefik.http.routers.<name>.rule=PathPrefix(`/auth-service`)  
      - traefik.http.routers.<name>.entrypoints=web  
      - traefik.http.routers.<name>.service=<name>  
      - traefik.http.services.<name>.loadbalancer.server.port=5000  
      - traefik.http.middlewares.<name>-strip.stripprefix.prefixes=/auth-service  
      - traefik.http.middlewares.<name>-prefix.headers.customrequestheaders.X-Forwarded-Prefix=/auth-service  
      - traefik.http.middlewares.<name>-prefix.headers.customrequestheaders.X-Script-Name=/auth-service  
      - traefik.http.routers.<name>.middlewares=<name>-strip,<name>-prefix  

### __init__.py (or where create_app is run)  

create_app():  
from werkzeug.middleware.proxy_fix import ProxyFix  

class ScriptNameFromForwardedPrefix:  
    def __init__(self, app): self.app = app  
    def __call__(self, environ, start_response):  
        p = environ.get("HTTP_X_FORWARDED_PREFIX") or environ.get("HTTP_X_SCRIPT_NAME")  
        if p: environ["SCRIPT_NAME"] = p.rstrip("/")  
        return self.app(environ, start_response)  

app = Flask(__name__)  
app.wsgi_app = ScriptNameFromForwardedPrefix(app.wsgi_app)  
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)  

### Dockerfile

With other settings  

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \  
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2).getcode()==200 else 1)"  

## 5) Quick test commands

curl -si http://HOST/auth-service/api/health  
Expected: 200 OK  

curl -si http://HOST/auth-service/ | grep -i '^location'  
expected: Location: /auth-service/ui/login  

docker compose exec app \  
  curl -si -X POST http://auth-service:5000/api/login \  
    -H 'X-Api-Key: <key>' -H 'Content-Type: application/json' \  
    --data '{"username":"admin","password":"adminpass"}'  
