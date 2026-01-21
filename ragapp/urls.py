from django.urls import path
from ragapp.views import ask_view

urlpatterns = [
    path('ask/', ask_view, name='ask'),
]
