from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("parent-profiles/", ProfileViewSet, basename="profile")
router.register("my-profile/", ProfileDetailViewSet, basename="profile-detail")

urlpatterns = router.urls