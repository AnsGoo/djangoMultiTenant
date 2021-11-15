from rest_framework import routers, urlpatterns
from .views import UserViewSet


from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register('user', UserViewSet)

urlpatterns = router.urls