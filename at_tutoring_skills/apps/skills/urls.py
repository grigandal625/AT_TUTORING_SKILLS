# project/skills_data/ATskills/urls.py
from adrf.routers import DefaultRouter

from at_tutoring_skills.apps.skills.views import TaskUserViewSet, UsersViewSet
from at_tutoring_skills.apps.skills.views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"task_users", TaskUserViewSet, basename="task_users")
router.register(r"user", UsersViewSet, basename="user")

urlpatterns = router.urls
