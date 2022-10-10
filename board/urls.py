from django.urls import path

from . import views

# borad应用的路由配置
urlpatterns = [
    path('message', views.message, name='message'),
    path('clearmessage', views.clear_message, name='clear_message'),
    path('messages_for_user', views.messages_for_user, name='messages_for_user')
]