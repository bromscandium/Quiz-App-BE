from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.company_actions import (
    CompanyActionSchema,
    CompanyActionCreate,
    CompanyActionUpdate,
    CompanyActionsList,
)


class CompanyActionSchemaFactory(ModelFactory[CompanyActionSchema]):
    __model__ = CompanyActionSchema
    __check_model__ = False


class CompanyActionCreateFactory(ModelFactory[CompanyActionCreate]):
    __model__ = CompanyActionCreate
    __check_model__ = False


class CompanyActionUpdateFactory(ModelFactory[CompanyActionUpdate]):
    __model__ = CompanyActionUpdate
    __check_model__ = False


class CompanyActionsListFactory(ModelFactory[CompanyActionsList]):
    __model__ = CompanyActionsList
    __check_model__ = False
