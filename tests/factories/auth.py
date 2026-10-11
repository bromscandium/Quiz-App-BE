from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.auth import LoginRequest, TokenRequest, TokenResponse


class LoginRequestFactory(ModelFactory[LoginRequest]):
    __model__ = LoginRequest
    __check_model__ = False


class TokenRequestFactory(ModelFactory[TokenRequest]):
    __model__ = TokenRequest
    __check_model__ = False


class TokenResponseFactory(ModelFactory[TokenResponse]):
    __model__ = TokenResponse
    __check_model__ = False
