from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from ..models import Board

class IsAuthenticatedOrBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS: 
            return bool(request.user == obj.user or request.user in obj.members.all())
        elif request.method == 'POST':
            return IsAuthenticated
        elif request.method == 'DELETE': 
            return bool(request.user == obj.user)
        else:
            return bool(request.user and request.user == obj.user)
        

class IsBoardMemberOrOwnerOrCommentator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or request.method == 'POST': 
            return bool(request.user == obj.user or request.user in obj.members.all())
        else: 
            return bool(request.user == obj.user)
        

class IsBoardMemberForTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj.board
        if request.method in [ SAFE_METHODS,'POST','PUT', 'PATCH']:
            return bool(request.user == board.user or request.user in board.members.all())
        if request.method == 'DELETE':
            return bool (request.user == obj.user or request.user == board.user)
        
