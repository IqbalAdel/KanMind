from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from kanmind_app.models import Board, User, Task, Comment
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer for Member objects.
    Handles validation and serialization of Member data.

    Fields:
        id (int): Read-only. Unique identifier of the comment.
        email (str): Email of the User.
        fullname (str): Fullname of the User.
    """
    fullname = serializers.StringRelatedField(
        source='username',  
        read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class SafePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    A PrimaryKeyRelatedField that converts non-existent related object references
    into a proper HTTP 404 Not Found response instead of a 400 ValidationError.

    This field is useful in serializers where you want to reference another model
    by its primary key, and want DRF to return a 404 if the object does not exist.
    """
    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            if "does not exist" in str(exc.detail):
                raise NotFound("Object not found.")
            raise exc


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task objects.
    Handles validation and serialization of Task data.

    Fields:
        id (int): Read-only. Unique identifier of the task.
        board (int or object): The board this task belongs to (PrimaryKey or nested object).
        title (str): Title of the task.
        description (str): Detailed description of the task.
        status (str): Current status of the task (e.g., 'to-do', 'in-progress', 'done').
        priority (str): Priority of the task (e.g., 'low', 'medium', 'high').
        assignee_id (int): ID of the user assigned to the task.
        reviewer_id (int): ID of the user reviewing the task.
        assignee (str): Read-only. Name or representation of the assigned user.
        reviewer (str): Read-only. Name or representation of the reviewer user.
        due_date (datetime): Deadline for the task completion.
        comments_count (int): Read-only. Number of comments attached to this task.
    """
    assignee = MemberSerializer(read_only=True, required=False, allow_null=True)
    reviewer = MemberSerializer(read_only=True, required=False, allow_null=True)
    board = SafePrimaryKeyRelatedField(queryset=Board.objects.all())
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True
    )
    comments_count = serializers.SerializerMethodField()

    def get_comments_count(self, obj): 
        return obj.comments.count()
    class Meta: 
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority','assignee_id','reviewer_id', 'assignee', 'reviewer', 'due_date', 'comments_count']

    def validate(self, attrs):     
        user = self.context['request'].user

        board = attrs.get('board') or getattr(self.instance, 'board', None)
        
        assignee = attrs.get('assignee')
        if assignee and assignee != board.user and assignee not in board.members.all():
            res = serializers.ValidationError({'detail': 'Assignee must be a member of the board.'})
            res.status_code = 401
            raise res
        
        reviewer = attrs.get('reviewer')
        if reviewer and reviewer != board.user and reviewer not in board.members.all():
            res = serializers.ValidationError({'detail': 'Reviewer must be a member of the board.'})
            res.status_code = 401
            raise res

        return attrs
    

class TaskDetailSerializer(TaskSerializer):
    """
    Serializer for specific Task objects.
    Handles validation and serialization of specific Task data.

    Fields:
        id (int): Read-only. Unique identifier of the task.
        title (str): Title of the task.
        description (str): Detailed description of the task.
        status (str): Current status of the task (e.g., 'to-do', 'in-progress', 'done').
        priority (str): Priority of the task (e.g., 'low', 'medium', 'high').
        assignee_id (int): ID of the user assigned to the task.
        reviewer_id (int): ID of the user reviewing the task.
        assignee (str): Read-only. Name or representation of the assigned user.
        reviewer (str): Read-only. Name or representation of the reviewer user.
        due_date (datetime): Deadline for the task completion.
    """
    assignee = MemberSerializer(read_only=True, required=False, allow_null=True)
    reviewer = MemberSerializer(read_only=True, required=False, allow_null=True)

    class Meta: 
        model = Task
        fields = ['id','title', 'description', 'status', 'priority','assignee_id', 'reviewer_id','assignee', 'reviewer','due_date']

    def update(self, instance, validated_data):   
        allowed_fields = {'title', 'description', 'status', 'priority','assignee_id', 'reviewer_id', 'due_date'}
        for field in list(validated_data.keys()):
            if field not in allowed_fields:
                validated_data.pop(field)

        return super().update(instance, validated_data)
    

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment objects.
    Handles validation and serialization of Comment data.

    Fields:
        id (int): Read-only. Unique identifier of the comment.
        created_at (datetime): Timestamp when the comment was created.
        author (str): Read-only. Username of the comment's author.
        content (str): Required. Text content of the comment.
    """
    author = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id','created_at', 'author' ,'content']

    def validate_content(self, value):
        if not value or not value.strip():
            res = serializers.ValidationError("Comment content cannot be empty.")
            res.status_code = 400
            raise res
        return value


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for Board objects.
    Handles validation and serialization of Board data.

    Fields:
        id (int): Read-only. Unique identifier of the board.
        title (str): Title of the board.
        members (list of int): Primary keys of users who are members of the board.
        member_count (int): Read-only. Number of users who are members of the board.
        ticket_count (int): Read-only. Total number of tasks associated with this board.
        tasks_to_do_count (int): Read-only. Number of tasks with status 'to-do' in this board.
        tasks_high_prio_count (int): Read-only. Number of tasks with high priority in this board.
        owner_id (int): Read-only. Primary key of the board owner.
    """
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many = True,
        write_only = True,
    )

    member_count = serializers.SerializerMethodField()
    owner_id = serializers.PrimaryKeyRelatedField(
        source='user',  
        read_only=True
    )
    tasks_high_prio_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'member_count', "ticket_count", "tasks_to_do_count", "tasks_high_prio_count", 'owner_id']

    def get_member_count(self, obj):      
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()
    
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(priority__iexact='to-do').count()
    
    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority__iexact='high').count()


class BoardDetailSerializer(BoardSerializer):
    """
    Serializer for Board objects.
    Handles validation and serialization of Board data.

    Fields:
        id (int): Read-only. Unique identifier of the board.
        title (str): Title of the board.
        members (list of int): Primary keys of users who are members of the board.
        owner_id (int): Read-only. Primary key of the board owner.
        tasks: list of all task objects assigned to this board
    """   
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        source='user',  
        read_only=True
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Board objects.
    Handles validation and serialization of Board data.

    Fields:
        id (int): Read-only. Unique identifier of the board.
        title (str): Title of the board.
        members (list of int): Primary keys of users who are members of the board.
        owner_data: Data of Owner object .
        members_data: list of all members part of the board
    """
    owner_data = MemberSerializer(source='user', read_only=True)
    members_data = MemberSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']

    def get_fields(self):
        fields = super().get_fields()
        if self.context['request'].method in ['PATCH', 'PUT']:
            fields['owner_data'].write_only = False
            fields['members_data'].write_only = False
        return fields
    
    def update(self, instance, validated_data):        
        allowed_fields = {'title', 'members'}
        for field in list(validated_data.keys()):
            if field not in allowed_fields:
                validated_data.pop(field)

        return super().update(instance, validated_data)