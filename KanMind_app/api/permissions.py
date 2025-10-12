from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from ..models import Board

class IsBoardMemberOrOwner(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS: 
            return bool(request.user in obj.members.all())
        else:
            return bool(request.user and request.user == obj.user)
        

class IsBoardMemberOrOwnerForComments(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user
    
    def has_object_permission(self, request, view, obj):
        board = obj.task.board
        if request.method in SAFE_METHODS:
            return bool(request.user == board.user or request.user in board.members.all())
        if request.method == 'DELETE': 
            return bool(request.user == obj.author)
        
        return False

class IsBoardMemberForTask(BasePermission):
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