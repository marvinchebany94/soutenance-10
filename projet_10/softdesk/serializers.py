from rest_framework.serializers import ModelSerializer
from .models import User, Projects, Contributors, Issues, Comments


class UsersSerializers(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name']


class ProjectsSerializers(ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'title', 'description', 'types', 'time_created']
        read_only_fields = ['id', 'time_created']


class ContributorsSerializers(ModelSerializer):
    class Meta:
        model = Contributors
        fields = ['user_id', 'project_id', 'permission', 'role']


class IssuesSerializers(ModelSerializer):
    class Meta:
        model = Issues
        fields = ['title', 'desc', 'tag', 'priority', 'status']


class CommentsSerializers(ModelSerializer):
    class Meta:
        model = Comments
        fields = ['description']


class SignUpSerializers(ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']


class LoginSerializers(ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']



