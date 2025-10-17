from app.services.refresh_token_service import RefreshTokenService


async def get_refresh_token_service() -> RefreshTokenService:
    return RefreshTokenService()
