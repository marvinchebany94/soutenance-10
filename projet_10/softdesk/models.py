from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Create your models here.


class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, blank=False, unique=True)
    password = models.CharField(blank=True, max_length=254)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('password',)
    list_display = ('last_login', 'is_superuser', 'is_staff')

    def unique_email(self):
        try:
            User.objects.get(email=self.email)
            return "L'email est deja dans la base de données"
        except ObjectDoesNotExist:
            return "c'est bon"

    def correct_lentgh_passwd(self):
        passwd = self.password
        if len(str(passwd)) < 5:
            return "Mot de passe trop court, 5 caractères au minimum"
        else:
            return True


class Projects(models.Model):
    title = models.CharField(max_length=150, blank=False, unique=True)
    description = models.CharField(blank=False, max_length=8192)

    TYPES = [
            ('back-end', 'back-end'),
            ('front-end', 'front-end'),
            ('IOS', 'IOS'),
            ('Android', 'Android')
        ]
    types = models.CharField(choices=TYPES, blank=False, max_length=20)
    author_user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    time_created = models.DateTimeField(auto_now_add=True)

    def user_has_project(self):
        try:
            Projects.objects.filter(author_user_id=self.author_user_id)
            return True
        except ObjectDoesNotExist:
            return False


class Contributors(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE, blank=False)
    PERMISSION = [
        ('CRUD', 'crud'),
        ('RC', 'rc'),
    ]
    permission = models.CharField(choices=PERMISSION, blank=False, max_length=4)
    ROLES = [
        ('CONTRIBUTEUR', 'contributeur'),
        ('RESPONSABLE', 'responsable')
    ]
    role = models.CharField(choices=ROLES, blank=False, max_length=20)


class Issues(models.Model):
    title = models.CharField(max_length=150, blank=False)
    desc = models.CharField(blank=False, max_length=8192)
    TAG = [
        ('BUG', 'bug'),
        ('AMELIORATION', 'amélioration'),
        ('TÂCHE', 'tâche')
]
    tag = models.CharField(blank=False, choices=TAG, max_length=20)
    PRIORITY = [
        ('FAIBLE', 'faible'),
        ('MOYENNE', 'moyenne'),
        ('ÉLEVÉE', 'élevée')

    ]
    priority = models.CharField(choices=PRIORITY, blank=False, max_length=20)
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)
    STATUS = [
        ('À faire', 'à faire'),
        ('En cours', 'en cours'),
        ('Terminé', 'terminé')
    ]
    status = models.CharField(choices=STATUS, blank=False, max_length=20)
    auteur_user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    assignee_user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False,
                                         related_name="user_assigne")
    time_created = models.DateTimeField(auto_now_add=True)


class Comments(models.Model):
    description = models.CharField(blank=False, max_length=8192)
    author_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_id = models.ForeignKey(Issues, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)




