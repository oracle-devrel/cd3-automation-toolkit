from django.urls import path

from . import views

app_name = 'register'

urlpatterns = [
    path('', views.Cd3welcome.as_view(), name='welcome'),
    path('cd3login/', views.Cd3login.as_view(), name='cd3login'),
    path('callback/', views.Callback.as_view(), name='callback'),
    path('cd3logout/', views.Cd3logout.as_view(), name='cd3logout'),
    path('cd3home/', views.Cd3home.as_view(), name='cd3home'),
]