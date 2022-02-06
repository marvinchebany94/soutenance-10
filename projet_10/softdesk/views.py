from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from .serializers import UsersSerializers, SignUpSerializers, LoginSerializers
from .models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView,\
    TokenVerifyView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
# Create your views here.


class SignUp(ModelViewSet):
    serializer_class = SignUpSerializers


class ConnexionAPIView(ModelViewSet):
    serializer_class = UsersSerializers

    def get_queryset(self):
        query_set = User.objects.all()
        email = self.request.POST.get('email')
        return query_set.filter(email=email)


@api_view(['POST'])
def sign_up(request):
    serializer = SignUpSerializers(data=request.data)
    if serializer.is_valid():
        email = serializer.data['email']
        password = serializer.data['password']
        first_name = serializer.data['first_name']
        last_name = serializer.data['last_name']
        new_user = User(first_name=serializer.data['first_name'])
        print(serializer.data)
        return Response('formulaire bien rempli')
    else:
        email = serializer.data['email']
        password = serializer.data['password']
        first_name = serializer.data['first_name']
        last_name = serializer.data['last_name']
        new_user = User(first_name=first_name, last_name=last_name,
                         email=email, password=password)
        print(new_user.unique_email())
        return Response("le form n'est pas valide")


class LoginApiView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = LoginSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
