from itertools import chain

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import ModelViewSet
from .serializers import UsersSerializers, SignUpSerializers, LoginSerializers, ProjectsSerializers, \
    ContributorsSerializers
from .models import User, Projects, Contributors
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
        return Response("le form n'est pas valide")


class LoginApiView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = LoginSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class ProjectsView(ModelViewSet):
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        liste_projects = []
        user = User.objects.get(id=self.request.user.id)
        queryset = Projects.objects.all()
        queryset = queryset.filter(author_user_id=self.request.user)
        liste_id_project = Contributors.objects.filter(user_id=user, role='contributeur')
        for project in liste_id_project:
            q = Projects.objects.get(id=project.project_id.id)
            liste_projects.append(q)
        result_list = list(chain(queryset, liste_projects))
        return result_list

    def create(self, request):
        form = ProjectsSerializers(data=request.data)
        if form.is_valid():
            title = form.data['title']
            description = form.data['description']
            types = form.data['types']
            try:
                author_user = User.objects.get(id=request.user.id)
                project = Projects(title=title, description=description, types=types,
                                   author_user_id=author_user)
                project.save()
                project = Projects.objects.get(author_user_id=author_user, title=title)
                try:
                    contributor = Contributors(user_id=author_user, project_id=project,
                                               permission='crud', role='responsable')
                    contributor.save()
                    return Response('le project a bien été enregistré')
                except IntegrityError:
                    return Response("Le projet n'a pas été enregistré à cause d'une erreur dans la table\
     contributor.")
            except IntegrityError:
                return Response("le projet n'a pas été enregistré")
        else:
            return Response("Erreur pendant le remplissage du formulaire.")

    def get(self, request, pk):
        projects = Projects.objects.all()
        if not pk:
            return projects.filter(author_user_id=request.user)
        else:
            project = get_object_or_404(projects, id=pk, author_user_id=request.user)
            return project

    def patch(self, request, *args, **kwargs):
        """
        Pensez à retirer l'erreur si uen url ne se finit pas par un /
        APPEND_SLASH¶

Valeur par défaut : True

Si défini à True et que l’URL de la requête ne correspond à aucun des motifs de l’URLconf et que l’URL ne se
termine pas par une barre oblique (slash), Django effectue une redirection HTTP vers la même URL additionnée d’une barre
 oblique finale. Notez que la redirection peut causer la perte d’éventuelles données envoyées avec une requête POST.

Le réglage APPEND_SLASH n’est utilisé que si CommonMiddleware est installé (voir Intergiciels (« Middleware »)).
Voir aussi PREPEND_WWW.
        """
        if not self.kwargs.get('pk'):
            return Response("Tu n'as pas entré l'id du projet.")
        else:
            pk = self.kwargs.get('pk')
        project = Projects.objects.get(pk=pk, author_user_id=request.user)
        print(project.title)
        form = ProjectsSerializers(Projects, data=request.data, partial=True)
        if form.is_valid():
            if form.data['title']:
                title = form.data['title']
                project.title = title
            if form.data['description']:
                description = form.data['description']
                project.description = description
            if form.data['types']:
                types = form.data['types']
                project.types = types
            try:
                project.save()
                return Response(project)
            except IntegrityError:
                return Response("Erreur pendant la mise à jour du projet")
        else:
            return Response('Formulaire mal rempli')

    def delete(self, request, *kwarg, **kwargs):
        if not self.kwargs.get('pk'):
            return Response("Tu n'as pas entré l'id du projet.")
        else:
            pk = self.kwargs.get('pk')

        project = get_object_or_404(Projects, pk=pk, author_user_id=request.user)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], permission_classes=[IsAuthenticated],
            authentication_classes=[JWTAuthentication], detail=True)
    def users(self, request, *args, **kwargs):
        if not self.kwargs.get('pk'):
            return Response("Tu n'as pas entré l'id du projet.")
        else:
            queryset = Projects.objects.all()
            pk = self.kwargs.get('pk')
            if type(pk) != 'int':
                return Response('Tu dois entrer un chiffre.')
            user = get_object_or_404(User, id=request.user.id)
            try:
                Projects.objects.get(id=pk, author_user_id=request.user.id)
            except ObjectDoesNotExist:
                return Response("le projet n'est pas à toi.")
            if Contributors.objects.get(project_id_id=pk, user_id_id=user.id, role="responsable"):
                if request.POST.get('email'):
                    email = request.POST.get('email')
                    user_to_add = get_object_or_404(User, email=email)
                    if Contributors.objects.get(project_id_id=pk, user_id=user_to_add, role='contributeur'):
                        return Response("Cette personne est déjà associé à ce projet.")
                    try:
                        contributor = Contributors(user_id=user_to_add, role='contributeur',
                                                   project_id_id=pk, permission='rc')
                        contributor.save()
                    except IntegrityError:
                        return Response("Erreur pendant la sauvegarde.")
                    return Response("L'utilisateur a bien été ajouté en tant que contributeur\
 au projet")
                else:
                    return Response("Tu as oublié d'entrer la variable email et de lui assigner\
 une valeur")
            else:
                return Response('il n y a pas de projet')

    @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated],
            authentication_classes=[JWTAuthentication])
    def users(self, request, *args, **kwargs):
        print(self.kwargs.get('pk'))
        if not self.kwargs.get('pk'):
            return Response("Tu n'as pas entré l'id du projet.")
        else:
            pk = self.kwargs.get('pk')
            pk = int(pk)
            try:
                int(pk)
            except ValueError:
                return Response('Tu dois entrer un chiffre.')
            projects = Projects.objects.all()
            users = User.objects.all()
            project = get_object_or_404(projects, id=pk)
            contributors_id = []
            contributors = Contributors.objects.filter(project_id=project)
            for user in contributors:
                contributors_id.append(user.user_id.id)
            users_associated = users.filter(id__in=contributors_id).values('id', 'email',
                                                                           'first_name', 'last_name')
            return Response(users_associated)

    @action(methods=['delete'], detail=True, permission_classes=[IsAuthenticated],
            authentication_classes=[JWTAuthentication], url_path=r'users/(?P<pk_users>[^/.]+)')
    def users(self, request, *args, **kwargs):
        try:
            pk = self.kwargs.get('pk')
            pk_users = self.kwargs.get('pk_users')
        except ValueError:
            return Response("Il faut entrer l'id du project et l'id de la personne que tu veux enlever")
        try:
            int(pk)
            int(pk_users)
        except ValueError:
            return Response("Il faut entrer des chiffres.")
        return Response('Tout est bon')


class ContributorsView(ModelViewSet):
    queryset = Contributors.objects.all()
    serializer_class = ContributorsSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(methods=['delete'], detail=True, permission_classes=[IsAuthenticated],
            authentication_classes=[JWTAuthentication])
    def delete(self, request, *args, **kwargs):
        print(self.kwargs.get('pk'))
        print(self.kwargs.get('user_id'))

@action(methods=['delete'], detail=True, permission_classes=[IsAuthenticated],
            authentication_classes=[JWTAuthentication])
def delete_user_from_project(request, pk, user_id):
    print(pk, user_id)