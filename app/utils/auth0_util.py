import json
from urllib.request import urlopen

import jwt
from jwt.algorithms import RSAAlgorithm

from app.core.security import security_settings
from app.exceptions.auth_exceptions import InvalidTokenHeader


class Auth0TokenUtil:
    def __init__(self):
        self.domain = security_settings.auth0.domain
        self.audience = security_settings.auth0.api_audience
        self.algorithms: list[str] = [security_settings.jwt.algorithm]
        self.jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        self._jwks: dict | None = None

    def _load_jwks(self) -> dict:
        if self._jwks is None:
            with urlopen(self.jwks_url) as response:
                self._jwks = json.loads(response.read())
        return self._jwks

    def decode_token(self, token: str) -> dict:
        jwks = self._load_jwks()
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.PyJWTError:
            raise InvalidTokenHeader

        rsa_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == unverified_header.get("kid"):
                rsa_key = RSAAlgorithm.from_jwk(json.dumps(key))
                break

        if rsa_key is None:
            return None

        return jwt.decode(
            token,
            rsa_key,
            algorithms=self.algorithms,
            audience=self.audience,
            issuer=f"https://{self.domain}/",
        )
