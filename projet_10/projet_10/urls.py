"""projet_10 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from softdesk.views import ConnexionAPIView, sign_up, LoginApiView
from rest_framework_simplejwt.views import TokenObtainPairView,\
    TokenRefreshView,\
    TokenVerifyView
from softdesk.views import ProjectsView, UsersView, IssuesView, CommentsView

router = routers.SimpleRouter()
router.register('login', LoginApiView, basename="login")
router.register(r'projects', ProjectsView, basename="projects")
router.register('users', UsersView, basename='users')
router.register('issues', IssuesView, basename="issues")
router.register('comments', CommentsView, basename='comments')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api_auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name="gettoken"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name="refreshtoken"),
    path('verifytoken/', TokenVerifyView.as_view(), name="verifytoken"),
    path('api/signup/', sign_up),
    path('api/projects/<pk>/users/', UsersView.as_view({
        'get': 'get',
        'post': 'create',
    })),
    path('api/projects/<pk>/users/<pk_users>/', UsersView.as_view({
        'delete': 'destroy'})),
    path('api/projects/<pk>/issues/', IssuesView.as_view({
        'get': 'get',
        'post': 'create'
    })),
    path('api/projects/<pk>/issues/<pk_issue>/', IssuesView.as_view({
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
    path('api/projects/<pk>/issues/<pk_issue>/comments/', CommentsView.as_view({
        'get': 'get',
        'post': 'create'
    })),
    path('api/projects/<pk>/issues/<pk_issue>/comments/<pk_comment>/',
         CommentsView.as_view({
             'patch': 'partial_update',
             'delete': 'destroy'
         })),
]
