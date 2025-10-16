from uuid import uuid4
from app.models import User
from app.schemas.user_schema import (
    SignUpRequest,
    UserUpdateRequest,
    UserDetailResponse,
)


def make_user(
    id=None,
    name="Bob",
    surname="Smith",
    nickname="ns123",
    email="bob@example.com",
    hashed_password="hashed_pass",
):
    return User(
        id=id if id else uuid4(),
        name=name,
        surname=surname,
        nickname=nickname,
        email=email,
        hashed_password=hashed_password,
    )


def make_signup_request(
    name="Bob",
    surname="Smith",
    nickname="ns123",
    email="bob@example.com",
    password="1234qwer",
):
    return SignUpRequest(
        name=name, surname=surname, nickname=nickname, email=email, password=password
    )


def make_update_request(
    name="Bob",
    surname="Smith",
    nickname="robert123",
    email="bob@example.com",
    password="newpass123",
):
    return UserUpdateRequest(
        name=name, surname=surname, nickname=nickname, email=email, password=password
    )


def make_user_detail_response(user=None):
    if user is None:
        user = make_user()
    return UserDetailResponse(
        id=user.id,
        name=user.name,
        surname=user.surname,
        nickname=user.nickname,
        email=user.email,
        hashed_password=user.hashed_password,
        created_at=None,
        updated_at=None,
    )
