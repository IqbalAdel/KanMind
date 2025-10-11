from django.urls import path
from .views import BoardsList, BoardDetail

urlpatterns = [
    path('', BoardsList.as_view(), name='board-list'),
    path('<int:pk>/', BoardDetail.as_view(), name='board-detail'),
    
]