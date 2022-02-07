from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import ModelViewSet
from .serializers import UsersSerializers, SignUpSerializers, LoginSerializers, ProjectsSerializers
from .models import User, Projects
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView,\
    TokenVerifyView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.db import IntegrityError
from django.contrib.auth import logout
# Create your views here.


class SignUp(ModelViewSet):
    serializer_class = SignUpSerializers
    queryset = User


class ConnexionAPIView(ModelViewSet):
    serializer_class = UsersSerializers
    permission_classes = (IsAuthenticated,)

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
        new_user = User(first_name=first_name, last_name=last_name,
                        email=email, password=password)
        try:
            new_user.set_password(password)
            new_user.save()
            print(new_user)
        except IntegrityError:
            print("Erreur dans la création du user")

        return Response('formulaire bien rempli')
    else:
        try:
            email = serializer.data['email']
            new_user = User(email=email)
            print(new_user.unique_email())
        except KeyError:
            return Response("Pas d'email rentré")

        try:
            password = serializer.data['password']
            new_user = User(password=password)
            print(new_user.correct_lentgh_passwd())
        except KeyError:
            return Response("Pas de mot de passe rentré")
        """
        first_name = serializer.data['first_name']
        last_name = serializer.data['last_name']
        new_user = User(first_name=first_name, last_name=last_name,
                        email=email, password=password)"""
        return Response("le form n'est pas valide")


class LoginApiView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = LoginSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class TestView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @api_view(['GET'])
    def list(self, request):
        print(request.GET)
        return Response(request.GET)


@api_view(['GET'])
def get_projects(request):

    if request.user.is_authenticated:
        projects = Projects(author_user_id=request.user)
        if not projects.user_has_project():
            return Response("Tu n'as pas de projects.")
        else:
            projets = Projects.objects.filter(author_user_id=request.user)
            serializers = ProjectsSerializers(projets, many=True)
            return Response(serializers.data)
    else:
        return Response("tu n'est pas connecté")