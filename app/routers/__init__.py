from .health_check import router as health_router
from .user import router as user_router
from .auth import router as auth_router
from .company import router as company_router
from .membership import router as membership_router
from .company_actions import router as company_actions_router
from .quiz import router as quiz_router
from .quiz_attempt import router as quiz_attempt_router

routers = [
    health_router,
    user_router,
    auth_router,
    company_router,
    membership_router,
    company_actions_router,
    quiz_router,
    quiz_attempt_router,
]
