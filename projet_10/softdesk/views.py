from itertools import chain

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import ModelViewSet
from .serializers import UsersSerializers, SignUpSerializers, LoginSerializers, ProjectsSerializers, \
    ContributorsSerializers, IssuesSerializers
from .models import User, Projects, Contributors, Issues
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
        if self.kwargs.get('pk'):
            try:
                pk = self.kwargs.get('pk')
                project = Projects.objects.all()
                return project.filter(id=pk, author_user_id=self.request.user)
            except ObjectDoesNotExist:
                return Response("Le project n'existe pas.")
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

                    contributor = Contributors(permission='crud', role='responsable',
                                               user_id=author_user, project_id=project)
                    contributor.save()
                    return Response('le project a bien été enregistré')
                except IntegrityError:
                    return Response("Le projet n'a pas été enregistré à cause d'une erreur dans la table\
     contributor.")
            except IntegrityError:
                return Response("le projet n'a pas été enregistré")
        else:
            return Response("Erreur pendant le remplissage du formulaire.")

    @action(methods=['get'], permission_classes=[IsAuthenticated],
            authentication_classes=[JWTAuthentication], detail=True)
    def get_project(self, request, pk):
        #project = get_object_or_404(Projects, id=pk, author_user_id=request.user)
        project = Projects.objects.all()
        print('ça bug ici')
        return project.filter(id=pk, author_user_id_id=request.user.id)

    def partial_update(self, request, *args, **kwargs):
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
            try:
                int(pk)
            except ValueError:
                return Response('Tu dois entrer un chiffre.')
        project = get_object_or_404(Projects, id=str(pk), author_user_id=request.user)
        form = ProjectsSerializers(project, data=request.data, partial=True)
        if form.is_valid():
            form.save()
            return Response(form.data)
        else:
            return Response('formulaire mal rempli')

    def destroy(self, request, *args, **kwargs):
        if not self.kwargs.get('pk'):
            return Response("Tu n'as pas entré l'id du projet.")
        else:
            try:
                pk = self.kwargs.get('pk')
                int(pk)
            except ValueError:
                return Response('la valeur n est pas un chiffre')
        project = get_object_or_404(Projects, id=pk, author_user_id=request.user)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], permission_classes=[IsAuthenticated],
            authentication_classes=[JWTAuthentication], detail=True, url_path='users')
    def add_users_to_project(self, request, *args, **kwargs):
        if not self.kwargs.get('pk'):
            return Response("Tu n'as pas entré l'id du projet.")
        else:
            queryset = Projects.objects.all()
            pk = self.kwargs.get('pk')
            try:
                int(pk)
            except ValueError:
                return Response('Tu dois entrer un chiffre.')
            user = get_object_or_404(User, id=request.user.id)
            try:
                project = Projects.objects.get(id=pk, author_user_id=request.user.id)
            except ObjectDoesNotExist:
                return Response("le projet n'est pas à toi.")
            get_object_or_404(Contributors, project_id=project, user_id=user, role="responsable")
            if request.POST.get('email'):
                email = request.POST.get('email')
                user_to_add = get_object_or_404(User, email=email)
                try:
                    Contributors.objects.get(project_id=project, user_id=user_to_add, role='contributeur')
                    return Response("Cette personne est déjà associé à ce projet.")
                except ObjectDoesNotExist:
                    pass
                try:
                    contributor = Contributors(role='contributeur', permission='rc',
                                               user_id=user_to_add, project_id=project)
                    contributor.save()
                except IntegrityError:
                    return Response("Erreur pendant la sauvegarde.")
                return Response("L'utilisateur a bien été ajouté en tant que contributeur\
 au projet")
            else:
                return Response("Tu as oublié d'entrer la variable email et de lui assigner\
 une valeur")

    @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated],
            authentication_classes=[JWTAuthentication], url_path='users')
    def get(self, request, *args, **kwargs):
        if not self.kwargs.get('pk'):
            return Response("Tu n'as pas entré l'id du projet.")
        else:
            pk = self.kwargs.get('pk')
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
                contributors_id.append(user.user_id_id)
            queryset = users.filter(id__in=contributors_id).values('id', 'email',
                                                                   'first_name', 'last_name')

            return Response(queryset)

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
            print(pk_users)
        except ValueError:
            return Response("Il faut entrer des chiffres.")
        try:
            project = Projects.objects.get(id=pk, author_user_id=request.user)
        except ObjectDoesNotExist:
            return Response('Le project n existe pas.')
        try:
            user_to_delete = User.objects.get(id=pk_users)
        except ObjectDoesNotExist:
            return Response("La personne recherchée n'existe pas.")
        try:
            contributor = Contributors.objects.get(project_id=project, user_id=user_to_delete)
        except ObjectDoesNotExist:
            return Response('La personne ne figure pas dans la liste des contributeurs.')
        if contributor.role == 'contributeur':
            contributor.delete()
            return Response("La personne a bien été supprimée.")
        else:
            return Response('Tu ne peux pas te supprimer de ton propre project.')

    @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated],
            authentication_classes=[JWTAuthentication], url_path='issues')
    def get_issues_from_project(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            pk = self.kwargs.get('pk')
            try:
                int(pk)
                try:
                    project = Projects.objects.get(id=pk)
                except ObjectDoesNotExist:
                    return Response("Le project n'existe pas")
                issues = Issues.objects.all()
                return Response(issues.filter(project_id=project).values())
            except ValueError:
                return Response("Il faut entrer un chiffre")
        else:
            return Response("Tu dois entrer l'id du projet")

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated],
            authentication_classes=[JWTAuthentication], url_path='issues')
    def create_issues(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            pk = self.kwargs.get('pk')
            try:
                int(pk)
                try:
                    project = Projects.objects.get(id=pk)
                    contributor = Contributors.objects.get(project_id=pk, user_id=request.user)
                except ObjectDoesNotExist:
                    return Response("project inexistant et/ou tu n'es pas associé à celui-ci.")
            except ValueError:
                return Response("Tu dois entrer un chiffre.")
            form = IssuesSerializers(data=request.data)
            if form.is_valid():
                print(form)
                print(request.POST.get('assignee_user_id'))
                title = form.data['title']
                desc = form.data['desc']
                tag = form.data['tag']
                priority = form.data['priority']
                status = form.data['status']
                if request.POST.get('assignee_user_id') is None or request.POST.get('assignee_user_id') == "":
                    assignee_user_id = request.user
                else:
                    assignee_user_id = request.POST.get('assignee_user_id')
                    try:
                        int(assignee_user_id)
                        user = User.objects.get(id=assignee_user_id)
                        contributor = Contributors.objects.get(project_id=project, user_id=user)
                        if contributor.role == 'contributeur':
                            pass
                        else:
                            return Response("La personne n'est pas associée à ce project.")
                    except ValueError:
                        return Response('Tu dois entrer un chiffre.')
                    except ObjectDoesNotExist:
                        return Response("Aucune personne ayant cet id est associée à ce project.")
                try:
                    issue = Issues(title=title, desc=desc, tag=tag,
                                   priority=priority, project_id=project, status=status,
                                   auteur_user_id=request.user, assignee_user_id=assignee_user_id)
                    issue.save()
                    return Response(form.data)
                except IntegrityError:
                    return Response("L'issue n'a pas été enregistrée.")
            else:
                return Response(form.errors)

        else:
            return Response("Tu dois entrer l'id du project auquel tu veux ajouter une issue.")


class IssuesView(ModelViewSet):
    queryset = Issues.objects.all()
    serializer_class = IssuesSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]



    def partial_update(self, request, *args, **kwargs):
        pk_issue = self.kwargs.get('pk_issue')
        print("tu es bien ici")
        return Response("tu vas update")


