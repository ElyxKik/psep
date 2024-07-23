"""
URL configuration for cisep project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static

from theapp.views import *
from compte.views import user_login, signup, logout_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',team_home, name='team_home' ),
    path('new-organisation', new_organisation, name='new_organisation'),
    path('search', search, name='search'),
    path('institutions', institutions, name='institutions'),
    path('institution/<int:id>',institution_detail, name='institution_detail' ),
    path('progressions', progression_institutions, name='progression_institutions'),
    path('new-projet/<int:id>', new_projet, name='new_projet'),
    path('membres', membres, name='membres'),
    path('projet/<int:id>', projet_detail, name='projet_detail'),
    path('projet/all', projets_list, name='projets_list'),
    path('new-jalon/<int:id>', new_jalon, name='new_jalon'),
    path('jalon-fini/<int:id>', jalon_fini, name='jalon_fini'),
    path('affectation/<int:id>',affectation, name='affectation'),
    path('profil/<int:id>', profil, name='profil'),
    path('login', user_login, name='login'),
    path('logout', logout_user, name='logout'),
    path('signup', signup, name='signup'),
    path("__reload__/", include("django_browser_reload.urls")),
    path('api/projets/', ProjetListCreate.as_view(), name='projet-list-create'),
    path('api/jalons/', JalonsListCreate.as_view(), name='jalons-list-create'),
    path('api/jalons/<int:pk>/', JalonsDetail.as_view(), name='jalons-detail'),
    path('api/taches/', TacheListCreate.as_view(), name='tache-list-create'),
    path('api/taches/<int:pk>/', TacheDetail.as_view(), name='tache-detail'),
    path('api/projets/<int:id>', api_projet_detail, name='api_projet_detail'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
