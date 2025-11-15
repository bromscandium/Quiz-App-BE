from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.membership import (
    MembershipSchema,
    MembershipCreate,
    MembershipUpdate,
    MembershipsList,
    UserMembership,
    UserMembershipsList,
    CompanyMembership,
    CompanyMembershipsList,
)


class MembershipSchemaFactory(ModelFactory[MembershipSchema]):
    __model__ = MembershipSchema
    __check_model__ = False


class MembershipCreateFactory(ModelFactory[MembershipCreate]):
    __model__ = MembershipCreate
    __check_model__ = False


class MembershipUpdateFactory(ModelFactory[MembershipUpdate]):
    __model__ = MembershipUpdate
    __check_model__ = False


class MembershipsListFactory(ModelFactory[MembershipsList]):
    __model__ = MembershipsList
    __check_model__ = False


class UserMembershipFactory(ModelFactory[UserMembership]):
    __model__ = UserMembership
    __check_model__ = False


class UserMembershipsListFactory(ModelFactory[UserMembershipsList]):
    __model__ = UserMembershipsList
    __check_model__ = False


class CompanyMembershipFactory(ModelFactory[CompanyMembership]):
    __model__ = CompanyMembership
    __check_model__ = False


class CompanyMembershipsListFactory(ModelFactory[CompanyMembershipsList]):
    __model__ = CompanyMembershipsList
    __check_model__ = False
