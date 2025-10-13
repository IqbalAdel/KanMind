from django.http import Http404
from rest_framework import generics
from KanMind_app.models import Board, Task, Comment
from .serializers import BoardSerializer, TaskSerializer, CommentSerializer, TaskDetailSerializer,BoardUpdateSerializer, BoardDetailSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import IsBoardMemberOrOwner, IsBoardMemberOrOwnerForComments , IsBoardMemberForTask    
from django.db.models import Q
from rest_framework.exceptions import NotFound, PermissionDenied

class BoardsList(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filters boards for only allowed boards

        Returns:
            object: all boards where the user is a member or owner
        """        
        user = self.request.user
        return Board.objects.filter(Q(user=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        """saves user who sent POST request as board owner

        """        

        board = serializer.save(user=self.request.user)


class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated ,IsBoardMemberOrOwner]

    def get_serializer_class(self):
        """returns specific serializers if its an update-reuqest or anything else

        Returns:
           serializer: returns a serializer to be used, depending on request method
        """        
        if self.request.method in ['PATCH', 'PUT']:
            return BoardUpdateSerializer
        return BoardDetailSerializer

class TasksList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]

    def get_queryset(self):
        """Filters for tasks where user is board-member or board-owner only

        Returns:
            object: all tasks where the user is a board-member or board-owner from
        """        

        user = self.request.user
        return Task.objects.filter(
            board__members=user
        ) | Task.objects.filter(
            board__user=user
        )
    
    def perform_create(self, serializer):
        """saves user as creator at POST request, necessary when checking for deletion of tasks

        """        
        board_id = self.request.data.get('board')
        user = self.request.user

        try: 
            board = Board.objects.get(id = board_id)
        except Board.DoesNotExist:
            raise NotFound('Board not found.')
        
        if user != board.user and user not in board.members.all():
            raise PermissionDenied("You are not a member of the board.")
        
        serializer.save(creator=self.request.user, board=board)

class TasksDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]

class CommentsList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwnerForComments]

    def get_queryset(self):
        """Filters view for comments where user is a board-member or board-owner, through the task_id which is connected to the board object

        Returns:
            object: Comments where user is board-member or board-owner from
        """        
        task_id = self.kwargs['pk']
        user = self.request.user
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        board = task.board
        if user != board.user and user not in board.members.all():
            raise PermissionDenied("You are not a member of the board.")
        return Comment.objects.filter(task=task).order_by("created_at")

    def perform_create(self, serializer):
        """Saves user as author when creating a comment for a specific task
        """        
        task_id = self.kwargs['pk']
        user = self.request.user

        try:  
            task = Task.objects.select_related('board').get(pk=task_id)
        except Task.DoesNotExist:
            raise NotFound('Task not found')

        board = task.board
        if user != board.user and user not in board.members.all():
            raise PermissionDenied("You are not a member of the board.")
        
        serializer.save(author=user, task_id=task_id)

class CommentsDetail(generics.RetrieveDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated ,IsBoardMemberOrOwnerForComments]

    def get_object(self):
        """Gets comment object for a specific comment id, and task_id and limits abaility to delete if user is not author, when rechecking object-permissions

        Raises:
            Http404: Comment doesn't exist

        Returns:
            comment: Comment object
        """        
        task_id = self.kwargs['pk']
        comment_id = self.kwargs['comment_id']

        try:
            comment = Comment.objects.select_related("task__board").get(
                id=comment_id, task_id=task_id
            )
        except Comment.DoesNotExist:
            raise NotFound('Comment not found')

        self.check_object_permissions(self.request, comment)
        return comment

class AssignedTasksList(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [ IsAuthenticated]

    def get_queryset(self):
        """Filters for tasks where user is assignee

        Returns:
            object: all tasks that user has been assigned to
        """        
        user = self.request.user    
        return Task.objects.filter(assignee=user).select_related('board', 'assignee', 'reviewer')


class ReviewedTasksList(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [ IsAuthenticated]

    def get_queryset(self):
        """Filters for tasks where user is reviewer

        Returns:
            object: all tasks where user has been assigned as reviewer
        """        
        user = self.request.user    
        return Task.objects.filter(reviewer=user).select_related('board', 'assignee', 'reviewer')
    