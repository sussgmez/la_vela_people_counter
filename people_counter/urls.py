from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", login_required(views.HomeView.as_view()), name="home"),
    path(
        "entrance/",
        login_required(views.EntranceView.as_view()),
        name="entrance",
    ),
    path(
        "entrances/",
        login_required(views.EntrancesView.as_view()),
        name="entrances",
    ),
    path("upload-file/", login_required(views.upload_file), name="upload-file"),
]
