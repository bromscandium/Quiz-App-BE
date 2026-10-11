from .auth import router as auth_router
from .company import router as company_router
from .company_actions import router as company_actions_router
from .health_check import router as health_router
from .membership import router as membership_router
from .quiz import router as quiz_router
from .quiz_attempt import router as quiz_attempt_router
from .user import router as user_router
from .stats import router as stats_router
from .export import router as export_router
from .notification import router as notification_router

routers = [
    health_router,
    user_router,
    auth_router,
    company_router,
    membership_router,
    company_actions_router,
    quiz_router,
    quiz_attempt_router,
    stats_router,
    export_router,
    notification_router,
]
