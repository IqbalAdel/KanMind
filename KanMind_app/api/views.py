from django.http import Http404
from rest_framework import generics
from KanMind_app.models import Board, Task, Comment
from .serializers import BoardSerializer, TaskSerializer, CommentSerializer, TaskDetailSerializer, BoardDetailSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import IsBoardMemberOrOwner, IsBoardMemberOrOwnerForComments , IsBoardMemberForTask    
from django.db.models import Q

class BoardsList(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(user=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        board = serializer.save(user=self.request.user)


class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated ,IsBoardMemberOrOwner]

class TasksList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            board__members=user
        ) | Task.objects.filter(
            board__user=user
        )
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class TasksDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]

class CommentsList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwnerForComments]

    def get_queryset(self):
        task_id = self.kwargs['pk']
        user = self.request.user
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Comment.objects.none()

        board = task.board
        if user == board.user or user in board.members.all():
            return Comment.objects.filter(task=task)
        return Comment.objects.none()

    def perform_create(self, serializer):
        task_id = self.kwargs['pk']
        serializer.save(author=self.request.user, task_id=task_id)

class CommentsDetail(generics.RetrieveDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated ,IsBoardMemberOrOwnerForComments]

    def get_object(self):
        task_id = self.kwargs['pk']
        comment_id = self.kwargs['comment_id']

        try:
            comment = Comment.objects.select_related("task__board").get(
                id=comment_id, task_id=task_id
            )
        except Comment.DoesNotExist:
            raise Http404

        self.check_object_permissions(self.request, comment)
        return comment

class AssignedTasksList(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [ IsAuthenticated]

    def get_queryset(self):
        user = self.request.user    
        return Task.objects.filter(assignee=user).select_related('board', 'assignee', 'reviewer')


class ReviewedTasksList(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [ IsAuthenticated]

    def get_queryset(self):
        user = self.request.user    
        return Task.objects.filter(reviewer=user).select_related('board', 'assignee', 'reviewer')
    