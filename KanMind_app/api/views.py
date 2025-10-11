from rest_framework import generics
from KanMind_app.models import Board, Task, Comment
from .serializers import BoardSerializer, TaskSerializer, CommentSerializer, TaskDetailSerializer, BoardDetailSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
#from .permissions import IsStaffOrReadOnly, IsAdminForDeleteOrPatchAndReadOnly, IsOwnerOrAdmin     # später hinzufügen!

class BoardsList(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def perform_create(self, serializer):
        board = serializer.save(user=self.request.user)


class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer

class TasksList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TasksDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer

class CommentsList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs['pk']
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs['pk']
        serializer.save(author=self.request.user, task_id=task_id)

class CommentsDetail(generics.RetrieveDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class AssignedTasksList(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user    
        return Task.objects.filter(assignee=user).select_related('board', 'assignee', 'reviewer')


class ReviewedTasksList(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user    
        return Task.objects.filter(reviewer=user).select_related('board', 'assignee', 'reviewer')
    