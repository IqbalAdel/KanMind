from rest_framework import serializers, status
from KanMind_app.models import Board, User, Task, Comment
from rest_framework.response import Response

class MemberSerializer(serializers.ModelSerializer):
    fullname = serializers.StringRelatedField(
        source='username',  
        read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class TaskSerializer(serializers.ModelSerializer):
    assignee = MemberSerializer(read_only=True, required=False, allow_null=True)
    reviewer = MemberSerializer(read_only=True, required=False, allow_null=True)
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
        """Counts number of comments on task

        Returns:
            int: number of comments
        """        
        return obj.comments.count()
    class Meta: 
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority','assignee_id','reviewer_id', 'assignee', 'reviewer', 'due_date', 'comments_count']

    def validate(self, attrs):
        """validates for membership of the user, assignee and reviewer on creation of task


        Raises:
            serializers.ValidationError: Creator of task must be owner or member
            serializers.ValidationError: Only validate assignee/reviewer if provided, checks for membership
            serializers.ValidationError: Only validate assignee/reviewer if provided, checks for membership

        Returns:
            attrs: dictionary with task information
        """        
        user = self.context['request'].user

            # Use board from attrs if provided, otherwise from existing instance
        board = attrs.get('board') or getattr(self.instance, 'board', None)

        if not board:
            return Response({'Board is required for this task.'}, status=status.HTTP_404_NOT_FOUND)

        if user != board.user and user not in board.members.all():
            return Response({'You must be a member of the board.'}, status=status.HTTP_403_FORBIDDEN)
        assignee = attrs.get('assignee')
        if assignee and assignee != board.user and assignee not in board.members.all():
            return Response({'Assignee must be a member of the board.'}, status=status.HTTP_403_FORBIDDEN)

        reviewer = attrs.get('reviewer')
        if reviewer and reviewer != board.user and reviewer not in board.members.all():
            return Response({'Reviewer must be a member of the board.'}, status=status.HTTP_403_FORBIDDEN)

        return attrs

class TaskDetailSerializer(TaskSerializer):
    assignee = MemberSerializer(read_only=True, required=False, allow_null=True)
    reviewer = MemberSerializer(read_only=True, required=False, allow_null=True)

    class Meta: 
        model = Task
        fields = ['id','title', 'description', 'status', 'priority','assignee_id', 'reviewer_id','assignee', 'reviewer','due_date']

    def update(self, instance, validated_data):
        """Only allows update or patch request for certain fields
        
        """        
        allowed_fields = {'title', 'description', 'status', 'priority','assignee_id', 'reviewer_id', 'due_date'}
        for field in list(validated_data.keys()):
            if field not in allowed_fields:
                validated_data.pop(field)

        return super().update(instance, validated_data)
    

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id','created_at', 'author' ,'content']

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Comment content cannot be empty.")
        return value


class BoardSerializer(serializers.ModelSerializer):
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
        """Counts number members

        Returns:
            int: number of members in board
        """        
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        """Counts number tasks

        Returns:
            int: number of tasks in board
        """
        return obj.tasks.count()
    def get_tasks_to_do_count(self, obj):
        """Counts number tasks with status to-do

        Returns:
            int: number of tasks in board
        """
        return obj.tasks.filter(priority__iexact='to-do').count()
    def get_tasks_high_prio_count(self, obj):
        """Counts number tasks with high priority

        Returns:
            int: number of tasks in board
        """
        return obj.tasks.filter(priority__iexact='high').count()


class BoardDetailSerializer(BoardSerializer):
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
    owner_data = MemberSerializer(source='user', read_only=True)
    members_data = MemberSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']

    def get_fields(self):
        """Hide owner_data and members_data from API form input"""
        fields = super().get_fields()
        if self.context['request'].method in ['PATCH', 'PUT']:
            fields['owner_data'].write_only = False
            fields['members_data'].write_only = False
        return fields
    
    def update(self, instance, validated_data):
        """Only allows update or patch request for title and member fields
        
        """        
        allowed_fields = {'title', 'members'}
        for field in list(validated_data.keys()):
            if field not in allowed_fields:
                validated_data.pop(field)

        return super().update(instance, validated_data)
    
