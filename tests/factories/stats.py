from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas.stats import (
    UserStats,
    UserQuizStats,
    UserStatsQuizzesList,
    UserLastAttempt,
    UserLastAttemptsList,
    CompanyUserStats,
    CompanyUserStatsList,
    CompanyUserQuizStats,
    CompanyUserQuizStatsList,
    CompanyUserLastAttempt,
    CompanyUserLastAttemptsList,
)


class UserStatsFactory(ModelFactory[UserStats]):
    __model__ = UserStats
    __check_model__ = False


class UserQuizStatsFactory(ModelFactory[UserQuizStats]):
    __model__ = UserQuizStats
    __check_model__ = False


class UserStatsQuizzesListFactory(ModelFactory[UserStatsQuizzesList]):
    __model__ = UserStatsQuizzesList
    __check_model__ = False


class UserLastAttemptFactory(ModelFactory[UserLastAttempt]):
    __model__ = UserLastAttempt
    __check_model__ = False


class UserLastAttemptsListFactory(ModelFactory[UserLastAttemptsList]):
    __model__ = UserLastAttemptsList
    __check_model__ = False


class CompanyUserStatsFactory(ModelFactory[CompanyUserStats]):
    __model__ = CompanyUserStats
    __check_model__ = False


class CompanyUserStatsListFactory(ModelFactory[CompanyUserStatsList]):
    __model__ = CompanyUserStatsList
    __check_model__ = False


class CompanyUserQuizStatsFactory(ModelFactory[CompanyUserQuizStats]):
    __model__ = CompanyUserQuizStats
    __check_model__ = False


class CompanyUserQuizStatsListFactory(ModelFactory[CompanyUserQuizStatsList]):
    __model__ = CompanyUserQuizStatsList
    __check_model__ = False


class CompanyUserLastAttemptFactory(ModelFactory[CompanyUserLastAttempt]):
    __model__ = CompanyUserLastAttempt
    __check_model__ = False


class CompanyUserLastAttemptsListFactory(ModelFactory[CompanyUserLastAttemptsList]):
    __model__ = CompanyUserLastAttemptsList
    __check_model__ = False
