from uuid import uuid4

import pytest

from app.exceptions.user import UnauthorizedUserAction, UserAlreadyExists
from app.schemas.user import UserCreate, UserUpdate
from app.services.user import UserService

user_service = UserService()


@pytest.mark.asyncio
class TestUserService:
    @pytest.fixture
    def valid_user_data(self):
        return UserCreate(
            name="John",
            surname="Doe",
            nickname="johndoe",
            email="john.doe@example.com",
            password="SecurePass123!",
        )

    @pytest.fixture
    def another_user_data(self):
        return UserCreate(
            name="Jane",
            surname="Smith",
            nickname="janesmith",
            email="jane.smith@example.com",
            password="AnotherPass456!",
        )

    async def test_create_user_success(self, uow, valid_user_data):
        user = await user_service.create_user(uow, valid_user_data)
        assert user.email == valid_user_data.email
        assert user.name == valid_user_data.name
        assert user.surname == valid_user_data.surname
        assert user.nickname == valid_user_data.nickname
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.hashed_password != valid_user_data.password

    async def test_create_user_duplicate_email(self, uow, valid_user_data):
        await user_service.create_user(uow, valid_user_data)
        duplicate_data = UserCreate(
            name="Another",
            surname="User",
            nickname="anotheruser",
            email=valid_user_data.email,
            password="Password123!",
        )
        with pytest.raises(UserAlreadyExists):
            await user_service.create_user(uow, duplicate_data)

    async def test_get_user_by_id_success(self, uow, valid_user_data):
        created_user = await user_service.create_user(uow, valid_user_data)
        fetched_user = await user_service.read_user_by_id(uow, created_user.id)
        assert fetched_user.id == created_user.id
        assert fetched_user.email == valid_user_data.email
        assert fetched_user.name == valid_user_data.name

    async def test_get_user_by_id_not_found(self, uow):
        non_existent_id = uuid4()
        user = await user_service.read_user_by_id(uow, non_existent_id)

        assert user is None

    async def test_get_user_by_email_success(self, uow, valid_user_data):
        await user_service.create_user(uow, valid_user_data)
        fetched_user = await user_service.read_user_by_email(uow, valid_user_data.email)
        assert fetched_user is not None
        assert fetched_user.email == valid_user_data.email
        assert fetched_user.name == valid_user_data.name

    async def test_get_user_by_email_not_found(self, uow):
        result = await user_service.read_user_by_email(uow, "nonexistent@example.com")
        assert result is None

    async def test_read_all_users(self, uow, valid_user_data, another_user_data):
        await user_service.create_user(uow, valid_user_data)
        await user_service.create_user(uow, another_user_data)
        result = await user_service.read_all_users(uow, offset=0, limit=10)
        assert result.total == 2
        assert len(result.users) == 2
        emails = [user.email for user in result.users]
        assert valid_user_data.email in emails
        assert another_user_data.email in emails

    async def test_read_all_users_pagination(
        self, uow, valid_user_data, another_user_data
    ):
        await user_service.create_user(uow, valid_user_data)
        await user_service.create_user(uow, another_user_data)
        result_page1 = await user_service.read_all_users(uow, offset=0, limit=1)
        result_page2 = await user_service.read_all_users(uow, offset=1, limit=1)
        assert result_page1.total == 2
        assert len(result_page1.users) == 1
        assert result_page2.total == 2
        assert len(result_page2.users) == 1
        assert result_page1.users[0].id != result_page2.users[0].id

    async def test_update_user_success(self, uow, valid_user_data):
        created_user = await user_service.create_user(uow, valid_user_data)
        update_data = UserUpdate(name="UpdatedName", surname="UpdatedSurname")

        updated_user = await user_service.update_user(
            uow, created_user.id, update_data, created_user.id
        )

        assert updated_user.name == "UpdatedName"
        assert updated_user.surname == "UpdatedSurname"
        assert updated_user.email == valid_user_data.email
        assert updated_user.id == created_user.id

    async def test_update_user_password(self, uow, valid_user_data):
        created_user = await user_service.create_user(uow, valid_user_data)
        original_password_hash = created_user.hashed_password
        update_data = UserUpdate(password="NewSecurePass999!")

        updated_user = await user_service.update_user(
            uow, created_user.id, update_data, created_user.id
        )

        assert updated_user.hashed_password != original_password_hash
        assert updated_user.hashed_password != "NewSecurePass999!"

    async def test_delete_user_success(self, uow, valid_user_data):
        created_user = await user_service.create_user(uow, valid_user_data)

        await user_service.delete_user(uow, created_user.id, created_user.id)

        user = await user_service.read_user_by_id(uow, created_user.id)

        assert user is None

    async def test_update_user_unauthorized(self, uow, valid_user_data):
        created_user = await user_service.create_user(uow, valid_user_data)
        different_user_id = uuid4()
        update_data = UserUpdate(name="HackedName")

        with pytest.raises(UnauthorizedUserAction):
            await user_service.update_user(
                uow, created_user.id, update_data, different_user_id
            )

    async def test_delete_user_unauthorized(self, uow, valid_user_data):
        created_user = await user_service.create_user(uow, valid_user_data)
        different_user_id = uuid4()

        with pytest.raises(UnauthorizedUserAction):
            await user_service.delete_user(uow, created_user.id, different_user_id)

    async def test_update_user_multiple_fields(self, uow, valid_user_data):
        created_user = await user_service.create_user(uow, valid_user_data)
        update_data = UserUpdate(
            name="NewName", surname="NewSurname", nickname="newnick"
        )

        updated_user = await user_service.update_user(
            uow, created_user.id, update_data, created_user.id
        )

        assert updated_user.name == "NewName"
        assert updated_user.surname == "NewSurname"
        assert updated_user.nickname == "newnick"
        assert updated_user.email == valid_user_data.email
