from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from ..models import Board, Task
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied

class IsBoardMemberOrOwner(BasePermission): 
    """
    Permission handles board-membership or ownership of the board
    """    
    def has_object_permission(self, request, view, obj):             
        if request.method in SAFE_METHODS: 
            return bool(request.user in obj.members.all() or request.user == obj.user)
        elif request.method in ['PATCH', 'PUT']:
            return bool(request.user in obj.members.all() or request.user == obj.user)
        else:
            return bool(request.user and request.user == obj.user)
        

class IsBoardMemberOrOwnerForComments(BasePermission):
    """
    Permission handles board-membership or ownership of the board when handling comments
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        if request.method == 'POST':
            task_id = view.kwargs.get('pk') 
            if not task_id:
                return False
            
            try:
                task = Task.objects.select_related('board').get(id=task_id)
                board = task.board
            except Task.DoesNotExist:
                raise NotFound('Task not found')

            return (
                request.user == board.user
                or request.user in board.members.all()
            )

        return True
    
    def has_object_permission(self, request, view, obj):
        board = obj.task.board
        if request.method in SAFE_METHODS:
            return bool(request.user == board.user or request.user in board.members.all())
        if request.method == 'DELETE': 
            return bool(request.user == obj.author)
        
        return False

class IsBoardMemberForTask(BasePermission):
    """
    Permission handles board-membership or ownership of the board when handling tasks
    """
    def has_object_permission(self, request, view, obj):
        board = obj.board
        user = request.user

        if request.method in SAFE_METHODS:
            return user == board.user or user in board.members.all()

        elif request.method in ['PUT', 'PATCH']:
            return user == board.user or user in board.members.all()

        elif request.method == 'DELETE':
            return user == board.user or user == obj.creator

        return False