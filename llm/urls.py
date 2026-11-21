from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('login/', auth_views.LoginView.as_view(template_name='llm/login.html'), name='llm_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/llm/login/'), name='llm_logout'),
    path('api/chat/', views.chat_api, name='chat_api'),
]