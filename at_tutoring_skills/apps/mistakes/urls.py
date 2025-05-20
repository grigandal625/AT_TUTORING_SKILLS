# project/skills_data/ATskills/urls.py
from adrf.routers import DefaultRouter

from at_tutoring_skills.apps.mistakes.views import MistakeViewSet

router = DefaultRouter()
router.register(r"mistakes", MistakeViewSet, basename="mistakes")

urlpatterns = router.urls
