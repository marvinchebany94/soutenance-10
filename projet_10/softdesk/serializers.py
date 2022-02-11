from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import User, Projects, Contributors, Issues, Comments


class UsersSerializers(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name']


class ProjectsSerializers(ModelSerializer):
    class Meta:
        model = Projects
        fields = ['title', 'description', 'types']


class ContributorsSerializers(ModelSerializer):
    class Meta:
        model = Contributors
        fields = ['user_id', 'project_id', 'permission', 'role']


class IssuesSerializers(ModelSerializer):
    class Meta:
        model = Issues
        fields = ['title', 'desc', 'tag', 'priority', 'project_id', 'status', 'auteur_user_id', 'time_created']


class CommentsSerializers(ModelSerializer):
    class Meta:
        model = Comments
        fields = ['description', 'author_user_id', 'issue_id', 'time_created']


class SignUpSerializers(ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']


class LoginSerializers(ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']



