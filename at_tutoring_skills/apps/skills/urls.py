# project/skills_data/ATskills/urls.py
from adrf.routers import DefaultRouter

from at_tutoring_skills.apps.skills.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = router.urls
