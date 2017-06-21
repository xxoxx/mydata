from django.conf.urls import url
from . import views

app_name = 'manager'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pre/$', views.pre, name='pre_release'),
]