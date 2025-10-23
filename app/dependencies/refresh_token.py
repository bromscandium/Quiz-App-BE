from app.services.refresh_token import RefreshTokenService


async def get_refresh_token_service() -> RefreshTokenService:
    return RefreshTokenService()
