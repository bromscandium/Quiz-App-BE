from uuid import uuid4
from app.exceptions import UnauthorizedUserAction, UserAlreadyExists, UserNotFound
from tests.factories.user import UserUpdateFactory
from tests.fixtures import *


@pytest.mark.asyncio
async def test_create_user_success(uow, user_service, user_1_create):
    user = await user_service.create_user(uow, user_1_create)
    assert user.id is not None
    assert user.email == user_1_create.email
    assert user.nickname == user_1_create.nickname


@pytest.mark.asyncio
async def test_create_user_already_exists(uow, user_service, user_1_create, user_1):
    with pytest.raises(UserAlreadyExists):
        await user_service.create_user(uow, user_1_create)


@pytest.mark.asyncio
async def test_read_user_by_id_success(uow, user_service, user_1):
    user = await user_service.read_user_by_id(uow, user_1.id)
    assert user.id == user_1.id
    assert user.email == user_1.email


@pytest.mark.asyncio
async def test_read_user_by_id_not_found(uow, user_service):
    user = await user_service.read_user_by_id(uow, uuid4())
    assert user is None


@pytest.mark.asyncio
async def test_read_user_by_email_success(uow, user_service, user_1):
    user = await user_service.read_user_by_email(uow, user_1.email)
    assert user.id == user_1.id
    assert user.email == user_1.email


@pytest.mark.asyncio
async def test_read_user_by_email_not_found(uow, user_service):
    user = await user_service.read_user_by_email(uow, "nonexistent@example.com")
    assert user is None


@pytest.mark.asyncio
async def test_read_user_by_nickname_success(uow, user_service, user_1):
    user = await user_service.read_user_by_nickname(uow, user_1.nickname)
    assert user.id == user_1.id
    assert user.nickname == user_1.nickname


@pytest.mark.asyncio
async def test_read_user_by_nickname_not_found(uow, user_service):
    user = await user_service.read_user_by_nickname(uow, "nonexistent_nickname")
    assert user is None


@pytest.mark.asyncio
async def test_read_all_users(uow, user_service, user_1, user_2):
    result = await user_service.read_all_users(uow, offset=0, limit=20)
    assert result.total >= 2
    assert len(result.users) >= 2


@pytest.mark.asyncio
async def test_read_user_companies(
    uow, user_service, company_service, user_1, company_1_create
):
    await company_service.create_company(uow, user_1.id, company_1_create)
    result = await user_service.read_user_companies(
        uow, offset=0, limit=20, value=user_1.id
    )
    assert result.total >= 1
    assert len(result.companies) >= 1


@pytest.mark.asyncio
async def test_update_user_success(uow, user_service, user_1):
    update_data = UserUpdateFactory.build(
        name="test", surname="test", nickname="new_nickname", password="test"
    )
    updated_user = await user_service.update_user(
        uow, user_1.id, update_data, current_user_id=user_1.id
    )
    assert updated_user.id == user_1.id
    assert updated_user.nickname == "new_nickname"


@pytest.mark.asyncio
async def test_update_user_unauthorized(uow, user_service, user_1, user_2):
    update_data = UserUpdateFactory.build(nickname="new_nickname")
    with pytest.raises(UnauthorizedUserAction):
        await user_service.update_user(
            uow, user_1.id, update_data, current_user_id=user_2.id
        )


@pytest.mark.asyncio
async def test_update_user_not_found(uow, user_service, user_1):
    update_data = UserUpdateFactory.build(nickname="new_nickname")
    nonexistent_id = uuid4()
    with pytest.raises(UserNotFound):
        await user_service.update_user(
            uow, nonexistent_id, update_data, current_user_id=nonexistent_id
        )


@pytest.mark.asyncio
async def test_delete_user_success(uow, user_service, user_1):
    await user_service.delete_user(uow, user_1.id, current_user_id=user_1.id)
    deleted_user = await user_service.read_user_by_id(uow, user_1.id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_delete_user_unauthorized(uow, user_service, user_1, user_2):
    with pytest.raises(UnauthorizedUserAction):
        await user_service.delete_user(uow, user_1.id, current_user_id=user_2.id)


@pytest.mark.asyncio
async def test_delete_user_not_found(uow, user_service, user_1):
    nonexistent_id = uuid4()
    with pytest.raises(UserNotFound):
        await user_service.delete_user(
            uow, nonexistent_id, current_user_id=nonexistent_id
        )
