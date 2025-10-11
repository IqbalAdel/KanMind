from django.urls import path
from .views import ReviewedTasksList, AssignedTasksList, TasksList, TasksDetail, CommentsList, CommentsDetail

urlpatterns = [
    path('', TasksList.as_view(), name='tasks-list'),
    path('<int:pk>/', TasksDetail.as_view(), name='tasks-detail'),
    path('<int:pk>/comments/', CommentsList.as_view(), name='comments-list'),
    path('<int:pk>/comments/<int:comment_id>/', CommentsDetail.as_view(), name='comments-detail'),
    path('assigned-to-me/', AssignedTasksList.as_view(), name='tasks-assigned'),
    path('reviewing/', ReviewedTasksList.as_view(), name='tasks-review')
    
]