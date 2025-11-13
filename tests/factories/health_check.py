from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.health_check import HealthCheckResponse


class HealthCheckResponseFactory(ModelFactory[HealthCheckResponse]):
    __model__ = HealthCheckResponse
    __check_model__ = False
