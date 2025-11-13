from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.user import (
    UserSchema,
    UserCreate,
    UserUpdate,
    UsersList,
    UserOwnedCompany,
    UserOwnedCompaniesList,
)


class UserSchemaFactory(ModelFactory[UserSchema]):
    __model__ = UserSchema
    __check_model__ = False


class UserCreateFactory(ModelFactory[UserCreate]):
    __model__ = UserCreate
    __check_model__ = False


class UserUpdateFactory(ModelFactory[UserUpdate]):
    __model__ = UserUpdate
    __check_model__ = False


class UserOwnedCompanyFactory(ModelFactory[UserOwnedCompany]):
    __model__ = UserOwnedCompany
    __check_model__ = False


class UsersListFactory(ModelFactory[UsersList]):
    __model__ = UsersList
    __check_model__ = False


class UserOwnedCompaniesListFactory(ModelFactory[UserOwnedCompaniesList]):
    __model__ = UserOwnedCompaniesList
    __check_model__ = False
