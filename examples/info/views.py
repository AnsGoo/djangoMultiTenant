

from info.models import User
from .serilizer import UserSerializer

from rest_framework.viewsets import ModelViewSet

class  UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class  = UserSerializer
