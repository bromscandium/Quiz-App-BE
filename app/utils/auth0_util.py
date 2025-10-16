import json
from urllib.request import urlopen

import jwt
from fastapi import HTTPException, status
from jwt.algorithms import RSAAlgorithm

from app.core.security import security_settings


class Auth0TokenUtil:
    def __init__(self):
        self.domain = security_settings.auth0.domain
        self.audience = security_settings.auth0.api_audience
        self.algorithms = security_settings.jwt.algorithm
        self.jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        self._jwks = None

    def _load_jwks(self):
        if self._jwks is None:
            with urlopen(self.jwks_url) as response:
                self._jwks = json.loads(response.read())
        return self._jwks

    def decode_token(self, token: str) -> dict:
        jwks = self._load_jwks()
        unverified_header = jwt.get_unverified_header(token)

        rsa_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = RSAAlgorithm.from_jwk(json.dumps(key))
                break

        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key",
            )

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=self.algorithms,
            audience=self.audience,
            issuer=f"https://{self.domain}/",
        )
        return payload
