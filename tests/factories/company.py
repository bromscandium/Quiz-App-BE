from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.company import (
    CompanySchema,
    CompanyCreate,
    CompanyUpdate,
    CompaniesList,
)


class CompanySchemaFactory(ModelFactory[CompanySchema]):
    __model__ = CompanySchema
    __check_model__ = False


class CompanyCreateFactory(ModelFactory[CompanyCreate]):
    __model__ = CompanyCreate
    __check_model__ = False


class CompanyUpdateFactory(ModelFactory[CompanyUpdate]):
    __model__ = CompanyUpdate
    __check_model__ = False

    visibility: bool = True


class CompaniesListFactory(ModelFactory[CompaniesList]):
    __model__ = CompaniesList
    __check_model__ = False
