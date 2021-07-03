import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'flaskdev.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffeeShop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    if 'Authorization' not in request.headers:
       abort(401)

    auth_header = request.headers['Authorization']
    header_pats = auth_header.split(' ')
    if len(header_pats) != 2:
        abort(401)
    elif header_pats[0].lower() != 'bearer':
        abort(401)

    return header_pats[1]

def check_permissions(payload, permission):
    if not 'permissions' in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)
    
    if not permission in payload['permissions']:
        abort(403)
    return True

def verify_decode_jwt(token):
    jsonurl = urlopen("https://{}/.well-known/jwks.json".format(AUTH0_DOMAIN))
    jwks = json.loads(jsonurl.read())

    unverified_token = jwt.get_unverified_header(token)

    if not 'kid' in unverified_token:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_token['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token, 
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload 
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token Expired.'
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Pleas, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse the authentication token.'
            }, 401)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find appropriate key.' 
    })

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            check_permissions(payload, permission)
            return f(payload, *args, **kwargs)
        return wrapper 
    return requires_auth_decorator